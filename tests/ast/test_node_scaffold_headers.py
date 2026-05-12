# Copyright (c) 2026 CoReason, Inc.
from coreason_meta_engineering.ast.node_scaffold import (
    apply_prosperity_headers,
    strip_existing_headers_and_apply_proprietary,
)


def test_strip_existing_headers() -> None:
    code = "# Copyright (c) 2025 CoReason\n# Prosperity License\n# Some other comment\nprint('hello')"
    result = strip_existing_headers_and_apply_proprietary(code, "CoReason, Inc", "HASH123")
    assert "HASH123" in result
    assert "CoReason, Inc" in result
    assert "# Some other comment" in result
    assert "print('hello')" in result


def test_apply_prosperity_headers_idempotent() -> None:
    code = "# Copyright (c) 2026 CoReason, Inc.. All Rights Reserved\n# Prosperity Public License 3.0\nprint('hello')"
    result = apply_prosperity_headers(code)
    assert result == code
