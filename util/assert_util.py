"""Shared response checks with useful failures for API test cases."""

from __future__ import annotations


def assert_response(response, expected: dict) -> dict:
    """Check HTTP status and declared top-level fields, parsing JSON once."""
    status = expected.get("status_code", 200)
    assert (
        response.status_code == status
    ), f"HTTP 状态码: 预期 {status}，实际 {response.status_code}"
    try:
        body = response.json()
    except ValueError as exc:
        raise AssertionError("接口未返回有效 JSON") from exc
    assert isinstance(body, dict), "接口 JSON 根节点必须是对象"
    for field, value in expected.items():
        if field == "status_code":
            continue
        assert field in body, f"响应缺少字段: {field}"
        assert (
            body[field] == value
        ), f"响应字段 {field}: 预期 {value!r}，实际 {body[field]!r}"
    return body
