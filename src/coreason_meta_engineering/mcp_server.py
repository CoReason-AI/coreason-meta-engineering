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
from datetime import UTC

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


@mcp.tool()  # type: ignore[misc]
def scaffold_manifest_yaml(
    target_dir: str,
    urn: str,
    author_id: str,
) -> str:
    """Scaffolds a new manifest.yaml for a given URN, injecting default CLA properties based on the AST Guillotine."""
    import os
    from datetime import datetime

    import yaml

    # AST Guillotine checks
    cla_status = "UNSIGNED"
    cla_assignee = ""
    # CoReason Global default
    tenant_cid = "889955217295c2bfef2d6812071b633b0819477e67f57853febf116f69f30531"

    if os.environ.get("AST_GUILLOTINE_ACTIVE") == "True":
        cla_status = "AUTO_ASSIGNED_PPL3"
        cla_assignee = "urn:tenant:coreason:global:authority"
    else:
        # Commercial Exception Active - Attempt to pull configured private identity
        import hvac

        vault_url = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
        vault_token = os.environ.get("VAULT_TOKEN", "dev-only-token")
        try:
            client = hvac.Client(url=vault_url, token=vault_token)
            response = client.secrets.kv.v2.read_secret_version(
                path="coreason/identity", raise_on_deleted_version=False
            )
            if response and "data" in response and "data" in response["data"]:
                ident = response["data"]["data"]
                private_cid = ident.get("tenant_cid")
                if private_cid:
                    tenant_cid = private_cid
                    # Sovereign assignment to themselves
                    cla_assignee = private_cid
        except Exception:
            pass

    manifest_data = {
        "urn": urn,
        "tenant_cid": tenant_cid,
        "default_clearance_tiers": [200],
        "default_minimum_rigidity_tier": 255,
        "epistemic_status": "DRAFT",
        "provenance": {
            "author_id": author_id,
            "created_at": datetime.now(UTC).isoformat(),
            "oracle_validator": None,
            "certification": "pending",
            "prior_event_hash": None,
            "cla_status": cla_status,
            "cla_assignee": cla_assignee,
            "cla_version": "v1.0",
        },
        "validation": {"test_coverage_pct": 0.0, "latency_ms": 0, "cryptographic_hash": "null"},
    }

    import pathlib

    target = pathlib.Path(target_dir) / "manifest.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)

    with open(target, "w", encoding="utf-8") as f:
        yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)

    return f"Scaffolded manifest.yaml at {target}"


def main() -> None:  # pragma: no cover
    mcp.run()
