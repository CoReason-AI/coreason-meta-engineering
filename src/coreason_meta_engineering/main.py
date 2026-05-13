# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import asyncio
import contextlib
import json
import os
import sys
import typing
from pathlib import Path

import httpx
import libcst as cst
import typer
import yaml

from coreason_meta_engineering.ast.actuator_scaffold import LogicInjectionFunctor
from coreason_meta_engineering.ast.node_scaffold import (
    EpistemicNodeInjectionFunctor,
    apply_prosperity_headers,
    strip_existing_headers_and_apply_proprietary,
)
from coreason_meta_engineering.ast.state_scaffold import StateInjectionFunctor
from coreason_meta_engineering.schema import DEFAULT_PROSPERITY_HASH, resolve_epistemic_schema_to_ast_bindings
from coreason_meta_engineering.utils.ast_extraction import extract_kinetic_skeleton
from coreason_meta_engineering.utils.congruence_judge import CongruenceFaultError, evaluate_congruence
from coreason_meta_engineering.utils.kinetic_guillotine import KineticGuillotineError, execute_guillotine_scan
from coreason_meta_engineering.utils.logger import logger
from coreason_meta_engineering.utils.topological_validation import (
    SemanticAmbiguityError,
    check_semantic_ambiguity,
    generate_multi_well_embeddings,
    verify_cryptographic_urn_boundary,
)


def enforce_cryptographic_license(
    target_file: Path, action_space_id: str, manifest_data: dict[str, typing.Any]
) -> None:
    license_hash = manifest_data.get("license_hash", DEFAULT_PROSPERITY_HASH)
    commercial_owner = manifest_data.get("commercial_owner")

    if license_hash != DEFAULT_PROSPERITY_HASH:
        pub_key = os.environ.get("COREASON_PUBLIC_KEY", "unknown")
        authority_url = os.environ.get("COREASON_URN_AUTHORITY_URL", "http://localhost:8080")

        payload = {"target_urn": action_space_id, "license_hash": license_hash, "requester_public_key": pub_key}

        try:
            resp = httpx.post(f"{authority_url}/api/v1/auth/verify_commercial_rights", json=payload, timeout=2.0)
            if resp.status_code == 200 and resp.json().get("authorized") is True:
                pass
            else:
                logger.error("CryptographicLicenseError: Unauthorized.")
                sys.exit(1)
        except Exception:
            logger.error(
                "ConnectionError: Cannot verify commercial override. Ensure your local URN Authority is running."
            )
            sys.exit(1)

        code = target_file.read_text(encoding="utf-8")
        code = strip_existing_headers_and_apply_proprietary(code, commercial_owner, license_hash)
        target_file.write_text(code, encoding="utf-8")
    else:
        code = target_file.read_text(encoding="utf-8")
        code = apply_prosperity_headers(code)
        target_file.write_text(code, encoding="utf-8")


app = typer.Typer()


def parse_geometric_schema(val: str) -> dict[str, typing.Any]:
    try:
        path = Path(val)
        if path.is_file():
            return typing.cast("dict[str, typing.Any]", json.loads(path.read_text(encoding="utf-8")))
    except OSError as e:
        logger.debug(f"Path is not a valid file or cannot be read: {e}")
    return typing.cast("dict[str, typing.Any]", json.loads(val))


@app.command(name="scaffold-manifest-state")  # type: ignore[misc]
def scaffold_manifest_state(
    state_name: str,
    geometric_schema: typing.Annotated[dict[str, typing.Any], typer.Argument(parser=parse_geometric_schema)],
    target_file: Path = typer.Option(..., exists=True, dir_okay=False, writable=True),  # noqa: B008
    action_space_id: str = typer.Option(..., help="The globally unique URN for this capability"),
    base_class: str = typer.Option("CoreasonBaseState", help="The base class to inherit from"),
) -> None:
    """
    Scaffolds a new model by parsing JSON schema and injecting it into the target Python file.
    """
    logger.info(f"Fabricating passive data state {state_name} into {target_file}")
    try:
        verify_cryptographic_urn_boundary(action_space_id)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    # 2. Resolve fields
    fields = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    # 3. Read target file text
    source_code = target_file.read_text(encoding="utf-8")

    # 4. Parse AST and inject
    module = cst.parse_module(source_code)
    transformer = StateInjectionFunctor(
        state_name=state_name, geometric_schema=fields, action_space_id=action_space_id, base_class=base_class
    )
    new_module = module.visit(transformer)

    # 5. Write modified code
    target_file.write_text(new_module.code, encoding="utf-8")

    # 6. Licensing
    enforce_cryptographic_license(target_file, action_space_id, geometric_schema)

    # 7. Print success message
    typer.echo(f"Successfully injected {state_name} into {target_file}")


@app.command(name="scaffold-logic-actuator")  # type: ignore[misc]
def scaffold_logic_actuator(
    actuator_name: str,
    geometric_schema: typing.Annotated[dict[str, typing.Any], typer.Argument(parser=parse_geometric_schema)],
    target_file: Path = typer.Option(..., exists=True, dir_okay=False, writable=True),  # noqa: B008
    action_space_id: str = typer.Option(..., help="The globally unique URN for this actuator"),
    return_type: str = typer.Option("None", help="Return type of the function"),
) -> None:
    """
    Scaffolds a new logic actuator function by parsing JSON schema and injecting it into the target Python file.
    """
    logger.info(f"Fabricating active logic {actuator_name} into {target_file}")
    try:
        verify_cryptographic_urn_boundary(action_space_id)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    parameters = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    source_code = target_file.read_text(encoding="utf-8")
    module = cst.parse_module(source_code)
    transformer = LogicInjectionFunctor(
        actuator_name=actuator_name,
        geometric_schema=parameters,
        return_type=return_type,
        action_space_id=action_space_id,
    )
    new_module = module.visit(transformer)
    target_file.write_text(new_module.code, encoding="utf-8")
    enforce_cryptographic_license(target_file, action_space_id, geometric_schema)

    typer.echo(f"Successfully injected {actuator_name} into {target_file}")


@app.command(name="scaffold-epistemic-node")  # type: ignore[misc]
def scaffold_epistemic_node(
    node_name: str,
    cognitive_boundary_directive: str,
    target_file: Path = typer.Option(..., exists=True, dir_okay=False, writable=True),  # noqa: B008
    action_space_id: str = typer.Option(..., help="The globally unique URN for this capability"),
    base_class: str = typer.Option("CoreasonBaseAgent", help="The base class to inherit from"),
) -> None:
    """
    Scaffolds a new Swarm Agent structure into the target Python file.
    """
    logger.info(f"Fabricating autonomous entity {node_name} into {target_file}")
    try:
        verify_cryptographic_urn_boundary(action_space_id)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    source_code = target_file.read_text(encoding="utf-8")
    module = cst.parse_module(source_code)
    transformer = EpistemicNodeInjectionFunctor(
        node_name=node_name,
        cognitive_boundary_directive=cognitive_boundary_directive,
        action_space_id=action_space_id,
        base_class=base_class,
    )
    new_module = module.visit(transformer)
    target_file.write_text(new_module.code, encoding="utf-8")
    # For epistemic node, we don't have geometric_schema in the args, just use empty dict to trigger default
    enforce_cryptographic_license(target_file, action_space_id, {})

    typer.echo(f"Successfully injected {node_name} into {target_file}")


@app.command(name="publish")  # type: ignore[misc]
def publish_urn(manifest_path: str = typer.Argument(..., help="Path to manifest.yaml")) -> None:
    """
    Publish a URN capability, validating through the Semantic and DLP Guillotines.
    """
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        logger.error(f"Manifest not found at {manifest_path}")
        sys.exit(1)

    try:
        manifest_data = yaml.safe_load(manifest_file.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to parse manifest: {e}")
        sys.exit(1)

    urn = manifest_data.get("urn", "unknown_urn")
    server_path = manifest_file.parent / "server.py"

    # 1. AST Extraction
    if not server_path.exists():
        logger.error(f"server.py not found in {manifest_file.parent}")
        sys.exit(1)

    skeleton = extract_kinetic_skeleton(str(server_path))
    docstring = skeleton.get("docstring", "")

    # 2. Semantic Disambiguation (Multi-Well)
    embeddings = generate_multi_well_embeddings(docstring)

    # Locate local registry matrix
    registry_path = manifest_file.parents[2] / "registry" / "compiled_matrix.json"
    local_registry = {}
    if registry_path.exists():
        with contextlib.suppress(Exception):
            local_registry = json.loads(registry_path.read_text(encoding="utf-8"))

    try:
        check_semantic_ambiguity(embeddings, local_registry)
    except SemanticAmbiguityError as e:
        logger.error(f"Publish blocked by Semantic Ambiguity:\n{e}")
        sys.exit(1)

    # 3. LLM-as-a-Judge Congruence Engine
    try:
        judge_response = evaluate_congruence(manifest_data, skeleton)
        manifest_data["congruence_score"] = judge_response.get("composite_congruence", 0.0)
        manifest_data["congruence_reasoning"] = judge_response.get("reasoning", "")
        for k, v in embeddings.items():
            manifest_data[f"embedding_{k}"] = v

        # Write the updated manifest
        # Using ruamel.yaml to preserve comments if any, but yaml is fine for now
        with open(manifest_file, "w", encoding="utf-8") as f:
            yaml.dump(manifest_data, f, default_flow_style=False)

    except CongruenceFaultError as e:
        logger.error(f"Publish blocked by Congruence Judge:\n{e}")
        sys.exit(1)

    # 4. Gather Payload
    payload_files = []
    payload_files.append({"file_name": manifest_file.name, "content": manifest_file.read_text(encoding="utf-8")})

    payload_files.extend(
        {"file_name": py_file.name, "content": py_file.read_text(encoding="utf-8")}
        for py_file in manifest_file.parent.glob("*.py")
    )

    # 5. THE DLP GUILLOTINE
    try:
        asyncio.run(execute_guillotine_scan(urn, payload_files))
    except KineticGuillotineError as e:
        logger.error(f"Publish blocked by DLP Compliance Engine:\n{e}")
        sys.exit(1)  # Hard exit, fail-closed

    # 6. Cryptographic Commitment
    # Code execution only reaches here if MCP returns "CLEAN"
    typer.echo(f"Payload for {urn} is SEMANTICALLY CONGRUENT and DLP CLEAN. Proceeding to cryptographic commitment.")
    # signature = sign_payload(payload_files, local_private_key)
    # commit_to_epistemic_ledger(urn, payload_files, signature)


if __name__ == "__main__":  # pragma: no cover
    app()
