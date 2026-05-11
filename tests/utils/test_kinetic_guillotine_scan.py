# Copyright (c) 2026 CoReason, Inc.
import json
from unittest.mock import MagicMock, patch

import pytest

from coreason_meta_engineering.utils.kinetic_guillotine import (
    KineticGuillotineError,
    execute_guillotine_scan,
    format_violations,
)


def test_format_violations():
    data = {
        "violations": [
            {
                "severity": "CRITICAL",
                "rule_name": "ForbiddenImport",
                "file_name": "main.py",
                "line_number": 10,
                "context_snippet": "import os",
            },
            {"rule_name": "EvalCall", "context_snippet": "eval(x)"},
        ]
    }
    formatted = format_violations(data)
    assert "Compliance Guillotine Blocked Publish:" in formatted
    assert "[CRITICAL] ForbiddenImport in main.py:10 (import os)" in formatted
    assert "[CRITICAL] EvalCall in unknown:0 (eval(x))" in formatted


@pytest.mark.asyncio
async def test_execute_guillotine_scan_clean():
    with (
        patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio,
        patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session,
    ):
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value

        from mcp.types import TextContent

        resp = MagicMock(content=[TextContent(type="text", text=json.dumps({"status": "CLEAN"}))])
        session_instance.call_tool.return_value = resp

        result = await execute_guillotine_scan("urn:test", [])
        assert result is True


@pytest.mark.asyncio
async def test_execute_guillotine_scan_blocked():
    with (
        patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio,
        patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session,
    ):
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        from mcp.types import TextContent

        session_instance.call_tool.return_value = MagicMock(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({"status": "BLOCKED", "violations": [{"rule_name": "TestViolation"}]}),
                )
            ]
        )

        with pytest.raises(KineticGuillotineError, match="Compliance Guillotine Blocked Publish"):
            await execute_guillotine_scan("urn:test", [])


@pytest.mark.asyncio
async def test_execute_guillotine_scan_timeout():
    with (
        patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio,
        patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session,
    ):
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        session_instance.call_tool.side_effect = TimeoutError()

        with pytest.raises(KineticGuillotineError, match="ComplianceTimeout"):
            await execute_guillotine_scan("urn:test", [])


@pytest.mark.asyncio
async def test_execute_guillotine_scan_connection_error():
    with patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio:
        mock_stdio.side_effect = Exception("Connection refused")

        with pytest.raises(KineticGuillotineError, match="GuillotineConnectionError"):
            await execute_guillotine_scan("urn:test", [])


@pytest.mark.asyncio
async def test_execute_guillotine_scan_invalid_content_type():
    with (
        patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio,
        patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session,
    ):
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        session_instance.call_tool.return_value = MagicMock(content=[MagicMock()])  # Not TextContent

        with pytest.raises(KineticGuillotineError, match="Invalid response from compliance server"):
            await execute_guillotine_scan("urn:test", [])


def test_format_violations_empty():
    assert format_violations({}) == "Compliance Guillotine Blocked Publish:"


@pytest.mark.asyncio
async def test_execute_guillotine_scan_sse(monkeypatch):
    from coreason_meta_engineering.utils.kinetic_guillotine import execute_guillotine_scan

    monkeypatch.setenv("COREASON_COMPLIANCE_URL", "http://localhost:8080")

    from mcp.types import TextContent

    with (
        patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio,
        patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session,
    ):
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        resp_text = '{"status": "CLEAN"}'
        session_instance.call_tool.return_value = MagicMock(content=[TextContent(type="text", text=resp_text)])

        await execute_guillotine_scan("urn:test", [])
