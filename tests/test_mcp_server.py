# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

"""Tests for mcp_server.py."""

from pathlib import Path

import pytest

from coreason_meta_engineering.mcp_server import scaffold_manifest_state


def test_scaffold_ontology_model_success(tmp_path: Path) -> None:
    target_file = tmp_path / "ontology.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    schema = {
        "properties": {
            "name": {"type": "string", "description": "The name"},
            "count": {"type": "integer", "description": "The count"},
        },
        "required": ["name"],
    }

    result = scaffold_manifest_state(
        state_name="Test Model Class",
        geometric_schema=schema,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
    )

    assert "class TestModelClass(CoreasonBaseState):" in result
    assert "TestModelClass.model_rebuild()" in result


def test_scaffold_ontology_model_target_not_a_file(tmp_path: Path) -> None:
    missing_target = tmp_path / "missing_dir"
    missing_target.mkdir()

    with pytest.raises(ValueError, match="is a directory, not a file"):
        scaffold_manifest_state(
            state_name="Test Model Class",
            geometric_schema={"properties": {}},
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
    assert "def my_actuator_func(" in result
    assert "@mcp.tool()" in result


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

    with pytest.raises(ValueError, match="is a directory, not a file"):
        scaffold_logic_actuator(
            actuator_name="My Actuator",
            geometric_schema={"properties": {}},
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:solver:my_actuator:v1",
            agent_instruction="i",
            causal_affordance="a",
            epistemic_bounds="b",
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
    assert "class MyAgentClass(CoreasonBaseAgent):" in result
    assert "MyAgentClass.model_rebuild()" in result


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

    with pytest.raises(ValueError, match="is a directory, not a file"):
        scaffold_epistemic_node(
            node_name="My Agent",
            cognitive_boundary_directive="role",
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:node:my_agent:v1",
        )


def test_mcp_server_new_files_and_sanitization(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import (
        scaffold_epistemic_node,
        scaffold_logic_actuator,
        scaffold_manifest_state,
    )

    target1 = tmp_path / "new_state.py"
    res1 = scaffold_manifest_state(
        state_name="1_invalid_class_start",
        geometric_schema={"properties": {}},
        target_file_path=str(target1),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
    )
    assert "Class1InvalidClassStart" in res1

    target2 = tmp_path / "new_node.py"
    res2 = scaffold_epistemic_node(
        node_name="___",
        cognitive_boundary_directive="role",
        target_file_path=str(target2),
        action_space_id="urn:coreason:actionspace:node:test:v1",
    )
    assert "GeneratedClass" in res2

    target3 = tmp_path / "new_actuator1.py"
    res3 = scaffold_logic_actuator(
        actuator_name="1_actuator",
        geometric_schema={"properties": {}},
        target_file_path=str(target3),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
        agent_instruction="i",
        causal_affordance="a",
        epistemic_bounds="b",
    )
    assert "def tool_1_actuator(" in res3

    target4 = tmp_path / "new_actuator2.py"
    res4 = scaffold_logic_actuator(
        actuator_name="___",
        geometric_schema={"properties": {}},
        target_file_path=str(target4),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
        agent_instruction="i",
        causal_affordance="a",
        epistemic_bounds="b",
    )
    assert "def generated_identifier(" in res4


def test_reconcile_manifest_state(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import reconcile_manifest_state

    target_file = tmp_path / "dummy.py"
    target_file.write_text("class DummyState:\n    pass\n")
    schema_payload = {"properties": {"name": {"type": "string"}}}

    result = reconcile_manifest_state(
        state_name="DummyState",
        geometric_schema=schema_payload,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:solver:test:v1",
    )
    assert "class DummyState" in result
    assert "name: Annotated[str" in result


def test_scaffold_kubernetes_crd_success(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import scaffold_kubernetes_crd

    target_file = tmp_path / "dummy.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    schema = {
        "properties": {
            "name": {"type": "string", "description": "The name"},
        },
        "required": ["name"],
    }

    result = scaffold_kubernetes_crd(
        crd_name="TestCRD",
        geometric_schema=schema,
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:substrate:test_crd:v1",
        api_group="test.group",
        api_version="v1",
        kind="TestKind",
    )

    assert "class Testcrd(KubernetesCRDBase):" in result
    assert 'api_group: ClassVar[str] = "test.group"' in result
    assert "Testcrd.model_rebuild()" in result


def test_scaffold_kubernetes_crd_invalid_urn(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import scaffold_kubernetes_crd

    target_file = tmp_path / "dummy.py"
    target_file.write_text("class CoreasonBaseState:\n    pass\n")

    with pytest.raises(ValueError, match="Invalid URN format"):
        scaffold_kubernetes_crd(
            crd_name="BadModel",
            geometric_schema={"properties": {}},
            target_file_path=str(target_file),
            action_space_id="finance_ledger_v1",
        )


def test_scaffold_kubernetes_crd_target_not_a_file(tmp_path: Path) -> None:
    from coreason_meta_engineering.mcp_server import scaffold_kubernetes_crd

    missing_target = tmp_path / "missing_dir"
    missing_target.mkdir()

    with pytest.raises(ValueError, match="is a directory, not a file"):
        scaffold_kubernetes_crd(
            crd_name="TestCRD",
            geometric_schema={"properties": {}},
            target_file_path=str(missing_target),
            action_space_id="urn:coreason:actionspace:substrate:test_crd:v1",
        )


# ═════════════════════════════════════════════════════════════════════════════
# verify_solver_diff (PVV Pipeline MCP Tool)
# ═════════════════════════════════════════════════════════════════════════════


class TestVerifySolverDiff:
    """Tests for the verify_solver_diff MCP tool."""

    def test_valid_code_returns_receipt(self) -> None:
        from coreason_meta_engineering.mcp_server import verify_solver_diff

        result = verify_solver_diff(
            deliberation_trace="Thinking hard...",
            payload="x = 42\n",
            solver_urn="urn:coreason:solver:claw_developer:v1",
            tokens_burned=500,
        )
        assert isinstance(result, dict)
        assert "execution_hash" in result
        assert len(result["execution_hash"]) == 64
        assert result["solver_urn"] == "urn:coreason:solver:claw_developer:v1"
        assert result["tokens_burned"] == 500

    def test_receipt_dict_structure(self) -> None:
        from coreason_meta_engineering.mcp_server import verify_solver_diff

        result = verify_solver_diff(
            deliberation_trace="Careful analysis...",
            payload="def add(a: int, b: int) -> int:\n    return a + b\n",
            solver_urn="urn:coreason:solver:test:v1",
            tokens_burned=0,
        )
        assert result["topology_class"] == "oracle_execution_receipt"
        assert result["human_attestation_signature"] is None
