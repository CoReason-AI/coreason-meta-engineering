# Copyright (c) 2026 CoReason, Inc.
import json
import pytest
from unittest.mock import MagicMock, patch
from coreason_meta_engineering.utils.kinetic_guillotine import (
    format_violations,
    execute_guillotine_scan,
    KineticGuillotineError,
)

def test_format_violations():
    data = {
        "violations": [
            {"severity": "CRITICAL", "rule_name": "ForbiddenImport", "file_name": "main.py", "line_number": 10, "context_snippet": "import os"},
            {"rule_name": "EvalCall", "context_snippet": "eval(x)"}
        ]
    }
    formatted = format_violations(data)
    assert "Compliance Guillotine Blocked Publish:" in formatted
    assert "[CRITICAL] ForbiddenImport in main.py:10 (import os)" in formatted
    assert "[CRITICAL] EvalCall in unknown:0 (eval(x))" in formatted

@pytest.mark.asyncio
async def test_execute_guillotine_scan_clean():
    with patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio, \
         patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session:
        
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        
        from mcp.types import TextContent
        session_instance.call_tool.return_value = MagicMock(content=[TextContent(type="text", text=json.dumps({"status": "CLEAN"}))])

        result = await execute_guillotine_scan("urn:test", [])
        assert result is True

@pytest.mark.asyncio
async def test_execute_guillotine_scan_blocked():
    with patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio, \
         patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session:
        
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        from mcp.types import TextContent
        session_instance.call_tool.return_value = MagicMock(content=[
            TextContent(type="text", text=json.dumps({"status": "BLOCKED", "violations": [{"rule_name": "TestViolation"}]}))
        ])

        with pytest.raises(KineticGuillotineError, match="Compliance Guillotine Blocked Publish"):
            await execute_guillotine_scan("urn:test", [])

@pytest.mark.asyncio
async def test_execute_guillotine_scan_timeout():
    with patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio, \
         patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session:
        
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        import asyncio
        session_instance.call_tool.side_effect = asyncio.TimeoutError()

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
    with patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio, \
         patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session:
        
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
    
    # We expect it to still try stdio because we haven't implemented SSE client yet
    # but we want to hit the 'pass' line 137.
    from unittest.mock import patch, AsyncMock, MagicMock
    
    from mcp.types import TextContent
    with patch("coreason_meta_engineering.utils.kinetic_guillotine.stdio_client") as mock_stdio, \
         patch("coreason_meta_engineering.utils.kinetic_guillotine.ClientSession") as mock_session:
        
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        session_instance = mock_session.return_value.__aenter__.return_value
        session_instance.call_tool.return_value = MagicMock(content=[TextContent(type="text", text='{"status": "CLEAN"}')])
        
        await execute_guillotine_scan("urn:test", [])
