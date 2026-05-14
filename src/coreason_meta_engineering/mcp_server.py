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

from coreason_manifest.spec import CognitiveDeliberativeEnvelopeState
from mcp.server.fastmcp import FastMCP

from coreason_meta_engineering.forge_orchestrator import orchestrate_generation
from coreason_meta_engineering.pvv import execute_pvv_pipeline
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
    Scaffolds a new model by orchestrating LLM agents bounded by the JSON schema.
    """
    state_name = _sanitize_python_class_name(state_name)
    verify_cryptographic_urn_boundary(action_space_id)

    prompt_template = (
        f"Generate a class named {state_name} inheriting from {base_class}.\n"
        f"Include a docstring with AGENT INSTRUCTION, CAUSAL AFFORDANCE, "
        f"EPISTEMIC BOUNDS, and MCP ROUTING TRIGGERS ({action_space_id}).\n"
        f"Ensure all fields map correctly to the provided geometric schema.\n"
    )

    return orchestrate_generation(
        target_file_path=target_file_path,
        action_space_id=action_space_id,
        geometric_schema=geometric_schema,
        complexity_score=3,
        prompt_template=prompt_template,
    )


@mcp.tool()  # type: ignore[misc]
def reconcile_manifest_state(
    state_name: str,
    geometric_schema: dict[str, typing.Any],
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoreasonBaseState",
) -> str:
    """
    Reconciles an existing model by orchestrating LLM agents bounded by the JSON schema.
    """
    state_name = _sanitize_python_class_name(state_name)
    verify_cryptographic_urn_boundary(action_space_id)

    prompt_template = (
        f"Reconcile the existing class named {state_name} inheriting from {base_class} with the new schema.\n"
        f"Include a docstring with AGENT INSTRUCTION, CAUSAL AFFORDANCE, "
        f"EPISTEMIC BOUNDS, and MCP ROUTING TRIGGERS ({action_space_id}).\n"
        f"Ensure all fields map correctly to the provided geometric schema.\n"
    )

    return orchestrate_generation(
        target_file_path=target_file_path,
        action_space_id=action_space_id,
        geometric_schema=geometric_schema,
        complexity_score=5,
        prompt_template=prompt_template,
    )


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
    Scaffolds a new logic actuator function by orchestrating LLM agents bounded by the JSON schema.
    """
    actuator_name = _sanitize_python_identifier(actuator_name)
    verify_cryptographic_urn_boundary(action_space_id)

    prompt_template = (
        f"Generate a function named {actuator_name} bounded by the @mcp.tool() decorator returning {return_type}.\n"
        f"Include a docstring with AGENT INSTRUCTION: {agent_instruction}\n"
        f"CAUSAL AFFORDANCE: {causal_affordance}\n"
        f"EPISTEMIC BOUNDS: {epistemic_bounds}\n"
        f"MCP ROUTING TRIGGERS: {action_space_id}.\n"
        f"Required imports to include if possible: {required_imports or []}\n"
        f"Suggested logic body: {logic_body or 'pass'}\n"
    )

    return orchestrate_generation(
        target_file_path=target_file_path,
        action_space_id=action_space_id,
        geometric_schema=geometric_schema,
        complexity_score=8,
        prompt_template=prompt_template,
    )


@mcp.tool()  # type: ignore[misc]
def scaffold_epistemic_node(
    node_name: str,
    cognitive_boundary_directive: str,
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoreasonBaseAgent",
) -> str:
    """
    Scaffolds a new Swarm Agent structure by orchestrating LLM agents.
    """
    node_name = _sanitize_python_class_name(node_name)
    verify_cryptographic_urn_boundary(action_space_id)

    prompt_template = (
        f"Generate an agent class named {node_name} inheriting from {base_class}.\n"
        f"The agent must adhere to the cognitive boundary directive: {cognitive_boundary_directive}\n"
        f"Include a docstring with AGENT INSTRUCTION, CAUSAL AFFORDANCE, "
        f"EPISTEMIC BOUNDS, and MCP ROUTING TRIGGERS ({action_space_id}).\n"
    )

    return orchestrate_generation(
        target_file_path=target_file_path,
        action_space_id=action_space_id,
        geometric_schema={},
        complexity_score=8,
        prompt_template=prompt_template,
    )


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
    Scaffolds a Kubernetes Custom Resource Definition (CRD) AST mapping by orchestrating LLM agents.
    """
    crd_name = _sanitize_python_class_name(crd_name)
    verify_cryptographic_urn_boundary(action_space_id)

    prompt_template = (
        f"Generate a class for Kubernetes CRD named {crd_name}.\n"
        f"API Group: {api_group}, API Version: {api_version}, Kind: {kind}\n"
        f"Include a docstring with AGENT INSTRUCTION, CAUSAL AFFORDANCE, "
        f"EPISTEMIC BOUNDS, and MCP ROUTING TRIGGERS ({action_space_id}).\n"
    )

    return orchestrate_generation(
        target_file_path=target_file_path,
        action_space_id=action_space_id,
        geometric_schema=geometric_schema,
        complexity_score=5,
        prompt_template=prompt_template,
    )


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
    envelope = CognitiveDeliberativeEnvelopeState[str](
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
