# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

from typing import Any


def resolve_epistemic_schema_to_ast_bindings(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Translates standard JSON Schema properties into coreason-manifest's highly bounded Pydantic types.
    """
    properties = schema.get("properties", {})
    required_fields = set(schema.get("required", []))
    fields: list[dict[str, Any]] = []

    def _resolve_type(prop_schema: dict[str, Any]) -> str:
        schema_type = prop_schema.get("type")
        if schema_type == "string":
            return "Annotated[str, StringConstraints(max_length=2000)]"
        if schema_type == "integer":
            return "int"
        if schema_type == "number":
            return "float"
        if schema_type == "boolean":
            return "bool"
        if schema_type == "array":
            items_schema = prop_schema.get("items", {})
            item_type = _resolve_type(items_schema)
            return f"list[{item_type}]"
        if schema_type == "object":
            return "dict[str, Any]"
        return "Any"

    for prop_name, prop_schema in properties.items():
        base_type = _resolve_type(prop_schema)

        is_required = prop_name in required_fields
        final_type = base_type if is_required else f"{base_type} | None"

        description = prop_schema.get("description", "")

        fields.append(
            {
                "name": prop_name,
                "type": final_type,
                "description": description,
                "optional": not is_required,
            }
        )

    return fields
