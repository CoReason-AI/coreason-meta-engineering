# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
from pathlib import Path

import pytest

from coreason_meta_engineering.mcp_server import scaffold_manifest_state


def test_scaffold_ontology_model_success(tmp_path: Path) -> None:
    # Setup dummy target file
    target_file = tmp_path / "ontology.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    # Define schema payload as dict
    schema = {
        "properties": {
            "name": {"type": "string", "description": "The name"},
            "count": {"type": "integer", "description": "The count"},
        },
        "required": ["name"],
    }

    # Call the actuator function
    result = scaffold_manifest_state(
        state_name="Test Model Class",
        geometric_schema=schema,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
    )

    # Assertions
    assert result == f"Successfully injected TestModelClass into {target_file}"
    content = target_file.read_text()
    assert "class TestModelClass(CoreasonBaseState):" in content
    assert "TestModelClass.model_rebuild()" in content


def test_scaffold_ontology_model_target_not_a_file(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing_dir"
    missing_target.mkdir()

    with pytest.raises(FileNotFoundError, match="exists but is not a file"):
        scaffold_manifest_state(
            state_name="FailModel",
            geometric_schema={},
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:solver:test:v1",
        )


def test_scaffold_ontology_model_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "ontology.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_manifest_state(
            state_name="BadModel",
            geometric_schema={"properties": {}},
            target_file_path=str(target_file),
            action_space_id="finance_ledger_v1",
        )


def test_scaffold_actuator_success(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = {
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "is_active": {"type": "boolean"}}
    }
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    result = scaffold_logic_actuator(
        actuator_name="My Actuator Func",
        geometric_schema=schema_payload,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:solver:my_actuator:v1",
        agent_instruction="Test instruction",
        causal_affordance="Test affordance",
        epistemic_bounds="Test bounds",
    )
    assert result == f"Successfully injected my_actuator_func into {target_file}"
    content = target_file.read_text()
    assert "def my_actuator_func(" in content
    assert "@mcp.tool()" in content


def test_scaffold_actuator_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = {"properties": {"name": {"type": "string"}}}
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_logic_actuator(
            actuator_name="MyActuator",
            geometric_schema=schema_payload,
            target_file_path=str(target_file),
            action_space_id="invalid",
            agent_instruction="Test instruction",
            causal_affordance="Test affordance",
            epistemic_bounds="Test bounds",
        )


def test_scaffold_actuator_target_not_a_file(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing_dir"
    missing_target.mkdir()
    from coreason_meta_engineering.mcp_server import scaffold_logic_actuator

    with pytest.raises(FileNotFoundError, match="exists but is not a file"):
        scaffold_logic_actuator(
            actuator_name="MyActuator",
            geometric_schema={},
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:solver:test:v1",
            agent_instruction="Test instruction",
            causal_affordance="Test affordance",
            epistemic_bounds="Test bounds",
        )


def test_scaffold_agent_node_success(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("class CoreasonBaseAgent: pass\n")
    from coreason_meta_engineering.mcp_server import scaffold_epistemic_node

    result = scaffold_epistemic_node(
        node_name="My Agent Class",
        cognitive_boundary_directive="role",
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:node:my_agent:v1",
    )
    assert result == f"Successfully injected MyAgentClass into {target_file}"
    content = target_file.read_text()
    assert "class MyAgentClass(CoreasonBaseAgent):" in content
    assert "MyAgentClass.model_rebuild()" in content


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


def test_scaffold_agent_node_target_not_a_file(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing_dir"
    missing_target.mkdir()
    from coreason_meta_engineering.mcp_server import scaffold_epistemic_node

    with pytest.raises(FileNotFoundError, match="exists but is not a file"):
        scaffold_epistemic_node(
            node_name="MyAgent",
            cognitive_boundary_directive="role",
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:solver:test:v1",
        )


def test_mcp_server_new_files_and_sanitization(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import (
        scaffold_epistemic_node,
        scaffold_logic_actuator,
        scaffold_manifest_state,
    )

    # Test creating a new file from scratch & valid sanitization with digit prefix
    target1 = tmp_path / "new_state.py"
    scaffold_manifest_state(
        state_name="1_invalid_class_start",
        geometric_schema={"properties": {}},
        target_file_path=str(target1),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
    )
    assert target1.exists()
    assert "Class1InvalidClassStart" in target1.read_text()

    # Test creating a new file from scratch & fallback class name
    target2 = tmp_path / "new_node.py"
    scaffold_epistemic_node(
        node_name="___",
        cognitive_boundary_directive="role",
        target_file_path=str(target2),
        action_space_id="urn:coreason:actionspace:node:test:v1",
    )
    assert target2.exists()
    assert "GeneratedClass" in target2.read_text()

    # Test creating a new file from scratch & valid sanitization with digit prefix for identifier
    target3 = tmp_path / "new_actuator1.py"
    scaffold_logic_actuator(
        actuator_name="1_actuator",
        geometric_schema={"properties": {}},
        target_file_path=str(target3),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
        agent_instruction="i",
        causal_affordance="a",
        epistemic_bounds="b",
    )
    assert target3.exists()
    assert "def tool_1_actuator(" in target3.read_text()

    # Test fallback identifier for empty string
    target4 = tmp_path / "new_actuator2.py"
    scaffold_logic_actuator(
        actuator_name="___",
        geometric_schema={"properties": {}},
        target_file_path=str(target4),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
        agent_instruction="i",
        causal_affordance="a",
        epistemic_bounds="b",
    )
    assert target4.exists()
    assert "def generated_identifier(" in target4.read_text()


def test_mcp_broadcast_urn_to_mesh(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import broadcast_urn_to_mesh

    manifest = tmp_path / "manifest.yaml"
    manifest.write_text('urn: "urn:test"\nvalidation:\n  cryptographic_hash: "sha256:123"', encoding="utf-8")

    result = broadcast_urn_to_mesh(str(tmp_path))
    assert "Successfully broadcasted" in result


def test_mcp_accumulate_pvv_signatures(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import accumulate_pvv_signatures

    manifest = tmp_path / "manifest.yaml"
    manifest.write_text('epistemic_status: "DRAFT"\nconsensus_signatures: []', encoding="utf-8")

    receipts = [
        {
            "urn": "urn:test",
            "cid": "sha256:abc",
            "node_id": "genesis_node_1",
            "signature_jwt": "genesis_jwt_abc",
            "is_approved": True,
        }
    ]

    result = accumulate_pvv_signatures(str(tmp_path), receipts)
    assert "Status -> PUBLISHED" in result
