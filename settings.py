"""Runtime configuration for the API test suite.

Non-sensitive values have local defaults. CI or another environment can
override them with environment variables instead of editing test data or
committing credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # Allows lightweight tooling to import settings pre-install.
    load_dotenv = None

_ENV_FILE = Path(__file__).resolve().with_name(".env")

if load_dotenv is not None:
    load_dotenv(_ENV_FILE, override=False)
elif _ENV_FILE.is_file():
    # Keep local runs usable before dependencies are installed. This fallback
    # intentionally supports the simple KEY=VALUE format used by .env.example.
    for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _key, _value = _line.split("=", 1)
        _key, _value = _key.strip(), _value.strip().strip("'\"")
        os.environ.setdefault(_key, _value)


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value is not None and value != "" else default


@dataclass(frozen=True)
class Settings:
    api_base_url: str = _env("API_BASE_URL", "http://127.0.0.1:8082")
    api_timeout: float = float(_env("API_TIMEOUT", "10"))
    user_phone: str = _env("TEST_USER_PHONE", "13900000001")
    user_password: str = _env("TEST_USER_PASSWORD", "Test1234")
    admin_phone: str = _env("TEST_ADMIN_PHONE", "13800000000")
    admin_password: str = _env("TEST_ADMIN_PASSWORD", "Admin1234")
    db_host: str = _env("DB_HOST", "127.0.0.1")
    db_port: int = int(_env("DB_PORT", "3306"))
    db_user: str = _env("DB_USER", "root")
    db_password: str = _env("DB_PASSWORD", "")
    db_name: str = _env("DB_NAME", "ecommerce_demo")

    @property
    def has_database_password(self) -> bool:
        return bool(self.db_password)

    def validate_database(self) -> None:
        """Raise an actionable error before PyMySQL reports ``using password: NO``."""
        if not self.db_password:
            raise RuntimeError(
                "未配置数据库密码。请复制 .env.example 为 .env 并设置 DB_PASSWORD，"
                "或在运行前导出 DB_PASSWORD 环境变量。"
            )


settings = Settings()
