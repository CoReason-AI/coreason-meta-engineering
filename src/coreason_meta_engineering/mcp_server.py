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

import libcst as cst
from mcp.server.fastmcp import FastMCP

from coreason_meta_engineering.ast.agent_scaffold import AgentInjectTransformer
from coreason_meta_engineering.ast.scaffold import ClassInjectTransformer
from coreason_meta_engineering.ast.tool_scaffold import FunctionInjectTransformer
from coreason_meta_engineering.schema import resolve_json_schema_to_fields
from coreason_meta_engineering.utils.validation import validate_action_space_urn

mcp = FastMCP("CoReason Agentic Forge")


@mcp.tool()  # type: ignore[misc]
def scaffold_ontology_model(
    model_name: str,
    schema_payload: str,
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoreasonBaseState",
) -> str:
    """
    Scaffolds a new model by parsing JSON schema and injecting it into the target Python file.
    """
    target_file = Path(target_file_path)
    validate_action_space_urn(action_space_id)
    if not target_file.exists() or not target_file.is_file():
        raise FileNotFoundError(f"Target file {target_file_path} does not exist or is not a file.")

    # 1. Parse schema payload
    try:
        payload_path = Path(schema_payload)
        if payload_path.is_file():
            schema_payload = payload_path.read_text(encoding="utf-8")
    except OSError:
        pass  # Not a valid path string, treat as raw JSON

    schema_dict = json.loads(schema_payload)

    # 2. Resolve fields
    fields = resolve_json_schema_to_fields(schema_dict)

    # 3. Read target file text
    source_code = target_file.read_text(encoding="utf-8")

    # 4. Parse AST and inject
    module = cst.parse_module(source_code)
    transformer = ClassInjectTransformer(
        name=model_name, fields=fields, action_space_id=action_space_id, base_class=base_class
    )
    new_module = module.visit(transformer)

    # 5. Write modified code
    target_file.write_text(new_module.code, encoding="utf-8")

    # 6. Return success message
    return f"Successfully injected {model_name} into {target_file_path}"


@mcp.tool()  # type: ignore[misc]
def scaffold_mcp_tool(
    tool_name: str,
    schema_payload: str,
    target_file_path: str,
    action_space_id: str,
    return_type: str = "None",
) -> str:
    """
    Scaffolds a new MCP tool function by parsing JSON schema and injecting it into the target Python file.
    """
    target_file = Path(target_file_path)
    validate_action_space_urn(action_space_id)
    if not target_file.exists() or not target_file.is_file():
        raise FileNotFoundError(f"Target file {target_file_path} does not exist or is not a file.")

    try:
        payload_path = Path(schema_payload)
        if payload_path.is_file():
            schema_payload = payload_path.read_text(encoding="utf-8")
    except OSError:
        pass

    schema_dict = json.loads(schema_payload)

    # Convert schema to parameters list
    parameters = resolve_json_schema_to_fields(schema_dict)

    source_code = target_file.read_text(encoding="utf-8")
    module = cst.parse_module(source_code)
    transformer = FunctionInjectTransformer(
        tool_name=tool_name, parameters=parameters, return_type=return_type, action_space_id=action_space_id
    )
    new_module = module.visit(transformer)
    target_file.write_text(new_module.code, encoding="utf-8")
    return f"Successfully injected {tool_name} into {target_file_path}"


@mcp.tool()  # type: ignore[misc]
def scaffold_agent_node(
    agent_name: str,
    role_description: str,
    target_file_path: str,
    action_space_id: str,
    base_class: str = "CoReasonBaseAgent",
) -> str:
    """
    Scaffolds a new Swarm Agent structure into the target Python file.
    """
    target_file = Path(target_file_path)
    validate_action_space_urn(action_space_id)
    if not target_file.exists() or not target_file.is_file():
        raise FileNotFoundError(f"Target file {target_file_path} does not exist or is not a file.")

    source_code = target_file.read_text(encoding="utf-8")
    module = cst.parse_module(source_code)
    transformer = AgentInjectTransformer(
        agent_name=agent_name, role_description=role_description, action_space_id=action_space_id, base_class=base_class
    )
    new_module = module.visit(transformer)
    target_file.write_text(new_module.code, encoding="utf-8")
    return f"Successfully injected {agent_name} into {target_file_path}"


def main() -> None:  # pragma: no cover
    mcp.run()
