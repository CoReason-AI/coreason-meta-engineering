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

from coreason_meta_engineering.ast.scaffold import ClassInjectTransformer
from coreason_meta_engineering.schema import resolve_json_schema_to_fields

mcp = FastMCP("CoReason Agentic Forge")


@mcp.tool()  # type: ignore[misc]
def scaffold_ontology_model(
    model_name: str,
    schema_payload: str,
    target_file_path: str,
    action_space_id: str,
) -> str:
    """
    Scaffolds a new model by parsing JSON schema and injecting it into the target Python file.
    """
    target_file = Path(target_file_path)
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
    transformer = ClassInjectTransformer(name=model_name, fields=fields, action_space_id=action_space_id)
    new_module = module.visit(transformer)

    # 5. Write modified code
    target_file.write_text(new_module.code, encoding="utf-8")

    # 6. Return success message
    return f"Successfully injected {model_name} into {target_file_path}"


def main() -> None:  # pragma: no cover
    mcp.run()
