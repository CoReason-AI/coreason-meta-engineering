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

from coreason_meta_engineering.mcp_server import scaffold_manifest_state


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

    # Call the actuator function
    result = scaffold_manifest_state(
        state_name="TestModel",
        geometric_schema=schema_payload,
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

    # Call the actuator function with file path as schema payload
    result = scaffold_manifest_state(
        state_name="AnotherModel",
        geometric_schema=str(schema_file),
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
        scaffold_manifest_state(
            state_name="FailModel",
            geometric_schema="{}",
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
        result = scaffold_manifest_state(
            state_name="PersonFallbackClean",
            geometric_schema=schema_payload_fallback_clean,
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:test:v1",
        )
        assert result == f"Successfully injected PersonFallbackClean into {target_file}"
        assert "class PersonFallbackClean(CoreasonBaseState):" in target_file.read_text(encoding="utf-8")


def test_scaffold_ontology_model_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "ontology.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_manifest_state(
            state_name="BadModel",
            geometric_schema='{"properties": {}}',
            target_file_path=str(target_file),
            action_space_id="finance_ledger_v1",
        )


def test_scaffold_actuator_success(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = (
        '{"properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "is_active": {"type": "boolean"}}}'
    )
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    result = scaffold_logic_actuator(
        actuator_name="MyActuator",
        geometric_schema=schema_payload,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:my_actuator:v1",
    )
    assert result == f"Successfully injected MyActuator into {target_file}"
    content = target_file.read_text()
    assert "def MyActuator" in content
    assert "@mcp.tool()" in content


def test_scaffold_actuator_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = '{"properties": {"name": {"type": "string"}}}'
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_logic_actuator(
            actuator_name="MyActuator",
            geometric_schema=schema_payload,
            target_file_path=str(target_file),
            action_space_id="invalid",
        )


def test_scaffold_actuator_target_not_found(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing.py"
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    with pytest.raises(FileNotFoundError, match="does not exist or is not a file"):
        scaffold_logic_actuator(
            actuator_name="MyActuator",
            geometric_schema='{"properties": {}}',
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:test:v1",
        )


def test_scaffold_actuator_fallback(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    from unittest.mock import patch

    schema_payload = '{"properties": {"name": {"type": "string"}}}'
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    with patch("coreason_meta_engineering.mcp_server.Path.is_file") as mock_is_file:
        mock_is_file.side_effect = [True, OSError("Mocked OS Error")]
        result = scaffold_logic_actuator(
            actuator_name="MyActuator",
            geometric_schema=schema_payload,
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:my_actuator:v1",
        )
        assert result == f"Successfully injected MyActuator into {target_file}"


def test_scaffold_actuator_file(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"properties": {"name": {"type": "string"}}}')
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    result = scaffold_logic_actuator(
        actuator_name="MyActuator",
        geometric_schema=str(schema_file),
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:my_actuator:v1",
    )
    assert result == f"Successfully injected MyActuator into {target_file}"


def test_scaffold_agent_node_success(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("class CoreasonBaseAgent: pass\n")
    from coreason_meta_engineering.mcp_server import scaffold_epistemic_node

    result = scaffold_epistemic_node(
        node_name="MyAgent",
        cognitive_boundary_directive="role",
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
    from coreason_meta_engineering.mcp_server import scaffold_epistemic_node

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_epistemic_node(
            node_name="MyAgent",
            cognitive_boundary_directive="role",
            target_file_path=str(target_file),
            action_space_id="invalid",
        )


def test_scaffold_agent_node_target_not_found(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing.py"
    from coreason_meta_engineering.mcp_server import scaffold_epistemic_node

    with pytest.raises(FileNotFoundError, match="does not exist or is not a file"):
        scaffold_epistemic_node(
            node_name="MyAgent",
            cognitive_boundary_directive="role",
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:test:v1",
        )
