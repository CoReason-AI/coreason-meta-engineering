# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

import json
from pathlib import Path

import pytest

from coreason_meta_engineering.mcp_server import scaffold_ontology_model


def test_scaffold_ontology_model_with_json_string(tmp_path: Path) -> None:
    # Setup dummy target file
    target_file = tmp_path / "ontology.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    # Define schema payload as string
    schema = {
        "properties": {
            "name": {"type": "string", "description": "The name"},
            "count": {"type": "integer", "description": "The count"},
        },
        "required": ["name"],
    }
    schema_payload = json.dumps(schema)

    # Call the tool function
    result = scaffold_ontology_model(
        model_name="TestModel",
        schema_payload=schema_payload,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:test:v1",
    )

    # Assertions
    assert result == f"Successfully injected TestModel into {target_file}"
    content = target_file.read_text()
    assert "class TestModel(CoreasonBaseState):" in content
    assert "TestModel.model_rebuild()" in content


def test_scaffold_ontology_model_with_file_path(tmp_path: Path) -> None:
    # Setup dummy target file
    target_file = tmp_path / "ontology.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    # Setup dummy schema file
    schema_file = tmp_path / "schema.json"
    schema = {
        "properties": {
            "flag": {"type": "boolean", "description": "A flag"},
        },
        "required": ["flag"],
    }
    schema_file.write_text(json.dumps(schema))

    # Call the tool function with file path as schema payload
    result = scaffold_ontology_model(
        model_name="AnotherModel",
        schema_payload=str(schema_file),
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:test:v1",
    )

    # Assertions
    assert result == f"Successfully injected AnotherModel into {target_file}"
    content = target_file.read_text()
    assert "class AnotherModel(CoreasonBaseState):" in content
    assert "AnotherModel.model_rebuild()" in content


def test_scaffold_ontology_model_target_not_found(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing.py"

    with pytest.raises(FileNotFoundError, match="does not exist or is not a file"):
        scaffold_ontology_model(
            model_name="FailModel",
            schema_payload="{}",
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:test:v1",
        )


def test_scaffold_ontology_model_invalid_file_fallback(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy_file.py"
    target_file.write_text("import pydantic\n", encoding="utf-8")

    from unittest.mock import patch

    schema_payload_fallback_clean = '{"properties": {"name": {"type": "string"}}}'

    with patch("coreason_meta_engineering.mcp_server.Path.is_file") as mock_is_file:
        # We only want to throw OSError when checking the schema payload, not the target_file.
        # The schema payload uses payload_path.is_file()
        # This will raise OSError exactly once (for the schema payload check)
        # We don't want to break the first `target_file.is_file()` check.
        # But wait, target_file.is_file() is checked *first* in the logic!
        # Let's side_effect with a list to return True for target_file.is_file(),
        # and raise OSError for payload_path.is_file()
        mock_is_file.side_effect = [True, OSError("Mocked OS Error")]
        result = scaffold_ontology_model(
            model_name="PersonFallbackClean",
            schema_payload=schema_payload_fallback_clean,
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:test:v1",
        )
        assert result == f"Successfully injected PersonFallbackClean into {target_file}"
        assert "class PersonFallbackClean(CoreasonBaseState):" in target_file.read_text(encoding="utf-8")


def test_scaffold_ontology_model_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "ontology.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_ontology_model(
            model_name="BadModel",
            schema_payload='{"properties": {}}',
            target_file_path=str(target_file),
            action_space_id="finance_ledger_v1",
        )


def test_scaffold_mcp_tool_success(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = (
        '{"properties": {"name": {"type": "string"}, "age": '
        '{"type": "integer"}, "is_active": {"type": "boolean"}}}'
    )
    from coreason_meta_engineering.mcp_server import scaffold_mcp_tool

    result = scaffold_mcp_tool(
        tool_name="MyTool",
        schema_payload=schema_payload,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:my_tool:v1",
    )
    assert result == f"Successfully injected MyTool into {target_file}"
    content = target_file.read_text()
    assert "def MyTool" in content
    assert "@mcp.tool()" in content


def test_scaffold_mcp_tool_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = '{"properties": {"name": {"type": "string"}}}'
    from coreason_meta_engineering.mcp_server import scaffold_mcp_tool

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_mcp_tool(
            tool_name="MyTool",
            schema_payload=schema_payload,
            target_file_path=str(target_file),
            action_space_id="invalid"
        )
        
def test_scaffold_mcp_tool_target_not_found(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing.py"
    from coreason_meta_engineering.mcp_server import scaffold_mcp_tool
    with pytest.raises(FileNotFoundError, match="does not exist or is not a file"):
        scaffold_mcp_tool(
            tool_name="MyTool",
            schema_payload='{"properties": {}}',
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:test:v1"
        )


def test_scaffold_mcp_tool_fallback(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    from unittest.mock import patch
    schema_payload = '{"properties": {"name": {"type": "string"}}}'
    from coreason_meta_engineering.mcp_server import scaffold_mcp_tool
    
    with patch("coreason_meta_engineering.mcp_server.Path.is_file") as mock_is_file:
        mock_is_file.side_effect = [True, OSError("Mocked OS Error")]
        result = scaffold_mcp_tool(
            tool_name="MyTool",
            schema_payload=schema_payload,
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:my_tool:v1"
        )
        assert result == f"Successfully injected MyTool into {target_file}"


def test_scaffold_mcp_tool_file(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"properties": {"name": {"type": "string"}}}')
    from coreason_meta_engineering.mcp_server import scaffold_mcp_tool
    result = scaffold_mcp_tool(
        tool_name="MyTool",
        schema_payload=str(schema_file),
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:my_tool:v1"
    )
    assert result == f"Successfully injected MyTool into {target_file}"



def test_scaffold_agent_node_success(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("class CoreasonBaseAgent: pass\n")
    from coreason_meta_engineering.mcp_server import scaffold_agent_node

    result = scaffold_agent_node(
        agent_name="MyAgent",
        role_description="role",
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:my_agent:v1",
    )
    assert result == f"Successfully injected MyAgent into {target_file}"
    content = target_file.read_text()
    assert "class MyAgent(CoReasonBaseAgent):" in content
    assert "system_prompt" in content


def test_scaffold_agent_node_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("class CoreasonBaseAgent: pass\n")
    from coreason_meta_engineering.mcp_server import scaffold_agent_node

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_agent_node(
            agent_name="MyAgent",
            role_description="role",
            target_file_path=str(target_file),
            action_space_id="invalid"
        )

def test_scaffold_agent_node_target_not_found(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing.py"
    from coreason_meta_engineering.mcp_server import scaffold_agent_node
    with pytest.raises(FileNotFoundError, match="does not exist or is not a file"):
        scaffold_agent_node(
            agent_name="MyAgent",
            role_description="role",
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:test:v1"
        )
