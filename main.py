from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="运行 API 自动化测试并生成 Allure 报告"
    )
    parser.add_argument(
        "--no-report", action="store_true", help="只运行测试，不生成 Allure HTML 报告"
    )
    args, pytest_args = parser.parse_known_args(argv)

    # Import lazily so ``python main.py --help`` still works when the test
    # environment has not installed the project dependencies yet.
    import pytest

    root = Path(__file__).resolve().parent
    previous_directory = Path.cwd()
    collecting = any(arg in {"--collect-only", "--co"} for arg in pytest_args)
    try:
        os.chdir(root)
        if not collecting:
            pytest_args = ["--clean-alluredir", *pytest_args]
        code = pytest.main(pytest_args, plugins=None)
    finally:
        os.chdir(previous_directory)
    if (
        not args.no_report
        and not collecting
        and code
        in (
            pytest.ExitCode.OK,
            pytest.ExitCode.TESTS_FAILED,
        )
    ):
        report_cmd = [
            "allure",
            "generate",
            str(root / "report/json_report"),
            "-o",
            str(root / "report/html_report"),
            "--clean",
        ]
        try:
            report = subprocess.run(report_cmd, cwd=root, check=False)
        except OSError as exc:
            print(
                f"无法生成 Allure HTML 报告：{exc}。可安装 Allure CLI 或使用 --no-report。",
                file=sys.stderr,
            )
            return int(code) or 1
        if report.returncode:
            return int(code) or report.returncode
    return int(code)


if __name__ == "__main__":
    sys.exit(main())
