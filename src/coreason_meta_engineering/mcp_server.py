# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import typing
from pathlib import Path

import libcst as cst
from mcp.server.fastmcp import FastMCP

from coreason_meta_engineering.ast.actuator_scaffold import LogicInjectionFunctor
from coreason_meta_engineering.ast.node_scaffold import EpistemicNodeInjectionFunctor
from coreason_meta_engineering.ast.state_scaffold import StateInjectionFunctor
from coreason_meta_engineering.schema import resolve_epistemic_schema_to_ast_bindings
from coreason_meta_engineering.utils.topological_validation import verify_cryptographic_urn_boundary
from coreason_meta_engineering.ast.urn_packager import package_urn_bundle

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
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    if not target_file.exists() or not target_file.is_file():
        raise FileNotFoundError(f"Target file {target_file_path} does not exist or is not a file.")

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

    # 6. Return success message
    return f"Successfully injected {state_name} into {target_file_path}"


@mcp.tool()  # type: ignore[misc]
def scaffold_logic_actuator(
    actuator_name: str,
    geometric_schema: dict[str, typing.Any],
    target_file_path: str,
    action_space_id: str,
    return_type: str = "None",
) -> str:
    """
    Scaffolds a new logic actuator function by parsing JSON schema and injecting it into the target Python file.
    """
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    if not target_file.exists() or not target_file.is_file():
        raise FileNotFoundError(f"Target file {target_file_path} does not exist or is not a file.")

    # Convert schema to parameters list
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
    return f"Successfully injected {actuator_name} into {target_file_path}"


@mcp.tool()  # type: ignore[misc]
def scaffold_epistemic_node(
    node_name: str,
    cognitive_boundary_directive: str,
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoReasonBaseAgent",
) -> str:
    """
    Scaffolds a new Swarm Agent structure into the target Python file.
    """
    target_file = Path(target_file_path)
    verify_cryptographic_urn_boundary(action_space_id)
    if not target_file.exists() or not target_file.is_file():
        raise FileNotFoundError(f"Target file {target_file_path} does not exist or is not a file.")

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
    return f"Successfully injected {node_name} into {target_file_path}"


@mcp.tool()  # type: ignore[misc]
def promote_to_urn_authority(
    source_file_path: str,
    target_urn: str,
    urn_authority_dir: str,
) -> str:
    """
    Automates the packaging, migration, and local cleanup of URNs into the coreason-urn-authority.
    """
    return package_urn_bundle(source_file_path, target_urn, urn_authority_dir)


def main() -> None:  # pragma: no cover
    mcp.run()
