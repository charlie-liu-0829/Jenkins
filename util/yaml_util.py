"""YAML loading with safe, runtime value substitution.

Supported placeholders:

* ``${API_BASE_URL}`` reads an environment variable and then project settings.
  ``${NAME:-fallback}`` provides a local fallback.
* ``{{ user_id }}`` reads a value from the context passed to ``read_yaml``.
* ``{{ uuid }}``, ``{{ timestamp }}`` and ``{{ date }}`` are built-in values.
  No Python expression is evaluated from YAML.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from functools import lru_cache
import logging
import os
from pathlib import Path
import re
from time import time
from uuid import uuid4

import yaml

from settings import settings

logger = logging.getLogger(__name__)

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
_CONTEXT_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*\}\}")


class YamlUtil:
    def __init__(self, file):
        self.file = str(Path(file).expanduser().resolve())
        logger.debug("准备打开 yaml 文件：%s", self.file)

    def read_yaml(self, context: dict | None = None, *, strict: bool = True):
        """Read and render one YAML document without mutating the cache."""
        variables = _variables(context)
        stat = Path(self.file).stat()
        data = deepcopy(_load_yaml(self.file, stat.st_mtime_ns, stat.st_size))
        return _render(data, variables, strict=strict)

    def read_cases(self, context: dict | None = None, *, strict: bool = True):
        """Return validated ``(cases, ids)`` for pytest parametrization."""
        data = self.read_yaml(context, strict=strict)
        cases = data.get("cases")
        ids = data.get("ids")
        if not isinstance(cases, list) or not cases:
            raise ValueError(f"YAML cases 必须是非空列表: {self.file}")
        for index, case in enumerate(cases):
            location = f"{self.file}: cases[{index}]"
            if not isinstance(case, dict):
                raise ValueError(f"用例必须是对象: {location}")
            if not isinstance(case.get("title"), str) or not case["title"].strip():
                raise ValueError(f"用例必须包含非空 title: {location}")
            request = case.get("request")
            if not isinstance(request, dict) or not isinstance(
                request.get("method"), str
            ):
                raise ValueError(f"用例 request 必须包含 method: {location}")
            if request["method"].upper() not in {
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "HEAD",
                "OPTIONS",
            }:
                raise ValueError(f"不支持的请求方法: {location}")
            if "url" in request and (
                not isinstance(request["url"], str) or not request["url"].strip()
            ):
                raise ValueError(f"请求 url 必须是非空字符串: {location}")
            expected = case.get("expected")
            if not isinstance(expected, dict) or not {"code", "msg"} <= expected.keys():
                raise ValueError(f"用例 expected 必须包含 code 和 msg: {location}")
        if ids is None:
            ids = [case.get("title", str(index)) for index, case in enumerate(cases)]
        if not isinstance(ids, list) or len(ids) != len(cases):
            raise ValueError(f"YAML cases 与 ids 数量不一致: {self.file}")
        return cases, [str(item) for item in ids]

    def write_yaml(self, data):
        path = Path(self.file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)
        _load_yaml.cache_clear()
        logger.debug("写入 yaml 文件：%s", self.file)
        return True


@lru_cache(maxsize=128)
def _load_yaml(file: str, modified_ns: int, size: int):
    path = Path(file)
    if not path.is_file():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML 根节点必须是对象: {path}")
    return data


def _variables(context: dict | None) -> dict:
    values = {
        "api_base_url": settings.api_base_url,
        "api_timeout": settings.api_timeout,
        "user_phone": settings.user_phone,
        "user_password": settings.user_password,
        "admin_phone": settings.admin_phone,
        "admin_password": settings.admin_password,
        "db_host": settings.db_host,
        "db_port": settings.db_port,
        "db_user": settings.db_user,
        "db_name": settings.db_name,
    }
    values.update({key.upper(): value for key, value in values.items()})
    values.update(
        {
            "API_BASE_URL": settings.api_base_url,
            "API_TIMEOUT": settings.api_timeout,
            "TEST_USER_PHONE": settings.user_phone,
            "TEST_USER_PASSWORD": settings.user_password,
            "TEST_ADMIN_PHONE": settings.admin_phone,
            "TEST_ADMIN_PASSWORD": settings.admin_password,
            "DB_HOST": settings.db_host,
            "DB_PORT": settings.db_port,
            "DB_USER": settings.db_user,
            "DB_NAME": settings.db_name,
        }
    )
    if context:
        values.update(context)
    return values


def _lookup(
    name: str, variables: dict, strict: bool, fallback=None, *, environment_first=False
):
    if environment_first and name in os.environ:
        value = os.environ[name]
    elif name in variables:
        value = variables[name]
    elif name in os.environ:
        value = os.environ[name]
    elif fallback is not None:
        return fallback
    else:
        if strict:
            raise KeyError(f"YAML 动态变量未配置: {name}")
        return ""
    if value == "" and fallback is not None:
        return fallback
    return value


def _render(value, variables: dict, *, strict: bool):
    if isinstance(value, dict):
        return {
            key: _render(item, variables, strict=strict) for key, item in value.items()
        }
    if isinstance(value, list):
        return [_render(item, variables, strict=strict) for item in value]
    if not isinstance(value, str):
        return value

    full_env = _ENV_PATTERN.fullmatch(value)
    if full_env:
        return _lookup(
            full_env.group(1),
            variables,
            strict,
            full_env.group(2),
            environment_first=True,
        )
    full_context = _CONTEXT_PATTERN.fullmatch(value)
    if full_context:
        return _dynamic_value(full_context.group(1), variables, strict)

    def replace_env(match):
        return str(
            _lookup(
                match.group(1),
                variables,
                strict,
                match.group(2),
                environment_first=True,
            )
        )

    value = _ENV_PATTERN.sub(replace_env, value)
    return _CONTEXT_PATTERN.sub(
        lambda match: str(_dynamic_value(match.group(1), variables, strict)), value
    )


def _dynamic_value(name: str, variables: dict, strict: bool):
    if name == "uuid":
        return str(uuid4())
    if name == "timestamp":
        return int(time())
    if name == "date":
        return datetime.now().strftime("%Y-%m-%d")
    return _lookup(name, variables, strict)
