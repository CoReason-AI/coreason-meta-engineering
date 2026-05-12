# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>
import re
import typing
from pathlib import Path

import libcst as cst
from coreason_manifest.spec import DeliberativeEnvelope
from mcp.server.fastmcp import FastMCP

from coreason_meta_engineering.ast.actuator_scaffold import LogicInjectionFunctor
from coreason_meta_engineering.ast.kubernetes_crd_scaffold import KubernetesCRDInjectionFunctor
from coreason_meta_engineering.ast.node_scaffold import EpistemicNodeInjectionFunctor
from coreason_meta_engineering.ast.state_reconciliation import StateReconciliationFunctor
from coreason_meta_engineering.ast.state_scaffold import StateInjectionFunctor
from coreason_meta_engineering.pvv import execute_pvv_pipeline
from coreason_meta_engineering.schema import resolve_epistemic_schema_to_ast_bindings
from coreason_meta_engineering.utils.topological_validation import verify_cryptographic_urn_boundary

__action_space_urn__ = "urn:coreason:actionspace:effector:meta_engineering:v1"


def _sanitize_python_identifier(name: str) -> str:
    safe_name = name.lower()
    safe_name = re.sub(r"[^a-z0-9_]", "_", safe_name)
    safe_name = re.sub(r"_+", "_", safe_name)
    safe_name = safe_name.strip("_")
    if safe_name and safe_name[0].isdigit():
        safe_name = f"tool_{safe_name}"
    if not safe_name:
        safe_name = "generated_identifier"
    return safe_name


def _sanitize_python_class_name(name: str) -> str:
    safe_name = re.sub(r"[^a-zA-Z0-9]", " ", name).title().replace(" ", "")
    if safe_name and safe_name[0].isdigit():
        safe_name = f"Class{safe_name}"
    if not safe_name:
        safe_name = "GeneratedClass"
    return safe_name


mcp = FastMCP("CoReason Agentic Forge")


@mcp.tool()  # type: ignore[misc]
def scaffold_manifest_state(
    state_name: str,
    geometric_schema: dict[str, typing.Any],
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoreasonBaseState",
) -> str:
    """
    Scaffolds a new model by parsing JSON schema and injecting it into the target Python file.
    """
    state_name = _sanitize_python_class_name(state_name)
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    source_code = target_file.read_text(encoding="utf-8") if target_file.exists() and target_file.is_file() else ""

    fields = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    module = cst.parse_module(source_code)
    transformer = StateInjectionFunctor(
        state_name=state_name, geometric_schema=fields, action_space_id=action_space_id, base_class=base_class
    )
    new_module = module.visit(transformer)

    return new_module.code


@mcp.tool()  # type: ignore[misc]
def reconcile_manifest_state(
    state_name: str,
    geometric_schema: dict[str, typing.Any],
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoreasonBaseState",
) -> str:
    """
    Reconciles an existing model by parsing JSON schema and updating it in the target Python file.
    """
    state_name = _sanitize_python_class_name(state_name)
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    source_code = target_file.read_text(encoding="utf-8") if target_file.exists() and target_file.is_file() else ""

    fields = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    module = cst.parse_module(source_code)
    transformer = StateReconciliationFunctor(
        state_name=state_name, geometric_schema=fields, action_space_id=action_space_id, base_class=base_class
    )
    new_module = module.visit(transformer)

    return new_module.code


@mcp.tool()  # type: ignore[misc]
def scaffold_logic_actuator(
    actuator_name: str,
    geometric_schema: dict[str, typing.Any],
    target_file_path: str,
    action_space_id: str,
    agent_instruction: str,
    causal_affordance: str,
    epistemic_bounds: str,
    return_type: str = "None",
    required_imports: list[str] | None = None,
    logic_body: str | None = None,
) -> str:
    """
    Scaffolds a new logic actuator function by parsing JSON schema and injecting it into the target Python file.
    """
    actuator_name = _sanitize_python_identifier(actuator_name)
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    source_code = target_file.read_text(encoding="utf-8") if target_file.exists() and target_file.is_file() else ""

    parameters = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    module = cst.parse_module(source_code)
    transformer = LogicInjectionFunctor(
        actuator_name=actuator_name,
        geometric_schema=parameters,
        return_type=return_type,
        action_space_id=action_space_id,
        required_imports=required_imports or [],
        logic_body=logic_body,
        agent_instruction=agent_instruction,
        causal_affordance=causal_affordance,
        epistemic_bounds=epistemic_bounds,
    )
    new_module = module.visit(transformer)
    return new_module.code


@mcp.tool()  # type: ignore[misc]
def scaffold_epistemic_node(
    node_name: str,
    cognitive_boundary_directive: str,
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoreasonBaseAgent",
) -> str:
    """
    Scaffolds a new Swarm Agent structure into the target Python file.
    """
    node_name = _sanitize_python_class_name(node_name)
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    source_code = target_file.read_text(encoding="utf-8") if target_file.exists() and target_file.is_file() else ""

    module = cst.parse_module(source_code)
    transformer = EpistemicNodeInjectionFunctor(
        node_name=node_name,
        cognitive_boundary_directive=cognitive_boundary_directive,
        action_space_id=action_space_id,
        base_class=base_class,
    )
    new_module = module.visit(transformer)
    return new_module.code

@mcp.tool()  # type: ignore[misc]
def scaffold_kubernetes_crd(
    crd_name: str,
    geometric_schema: dict[str, typing.Any],
    target_file_path: str,
    action_space_id: str,
    api_group: str = "chaos-mesh.org",
    api_version: str = "v1alpha1",
    kind: str = "NetworkChaos",
) -> str:
    """
    Scaffolds a Kubernetes Custom Resource Definition (CRD) AST mapping.
    When a ChaosExperimentTask is requested, it formats it for Kubernetes CRDs instead of Python dicts.
    """
    crd_name = _sanitize_python_class_name(crd_name)
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    source_code = target_file.read_text(encoding="utf-8") if target_file.exists() and target_file.is_file() else ""

    fields = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    module = cst.parse_module(source_code)
    transformer = KubernetesCRDInjectionFunctor(
        crd_name=crd_name,
        geometric_schema=fields,
        action_space_id=action_space_id,
        api_group=api_group,
        api_version=api_version,
        kind=kind,
    )
    new_module = module.visit(transformer)
    return new_module.code


@mcp.tool()  # type: ignore[misc]
def verify_solver_diff(
    deliberation_trace: str,
    payload: str,
    solver_urn: str,
    tokens_burned: int,
) -> dict[str, typing.Any]:
    """Verify a high-entropy solver diff through the PVV pipeline.

    Accepts raw envelope components, constructs a ``DeliberativeEnvelope``,
    and runs the full Epistemic Strip → Syntax Integrity → Kinetic Guillotine
    → Receipt Generation pipeline.

    Returns the ``OracleExecutionReceipt`` as a dictionary.
    """
    envelope = DeliberativeEnvelope[str](
        deliberation_trace=deliberation_trace,
        payload=payload,
    )
    receipt = execute_pvv_pipeline(
        envelope=envelope,
        solver_urn=solver_urn,
        tokens_burned=tokens_burned,
    )
    return receipt.model_dump()


def main() -> None:  # pragma: no cover
    mcp.run()
