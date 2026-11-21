"""Pytest helpers for loading declarative YAML cases once at collection time."""

from __future__ import annotations

from pathlib import Path

import pytest

from util.yaml_util import YamlUtil


def case_parametrize(path: str | Path, context: dict | None = None):
    """Build a parametrization marker from one validated YAML document."""
    cases, ids = YamlUtil(path).read_cases(context)
    return pytest.mark.parametrize("case_info", cases, ids=ids)
