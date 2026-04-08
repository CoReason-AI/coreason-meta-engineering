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

from coreason_meta_engineering.schema import resolve_json_schema_to_fields


def test_resolve_json_schema_to_fields_basic() -> None:
    schema: dict[str, Any] = {
        "properties": {
            "name": {"type": "string", "description": "Name of the person"},
            "age": {"type": "integer"},
            "score": {"type": "number", "description": "Score value"},
            "is_active": {"type": "boolean", "description": "Active flag"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "metadata": {"type": "object", "description": "Extra metadata"},
        },
        "required": ["name", "age"],
    }

    fields = resolve_json_schema_to_fields(schema)

    assert len(fields) == 6

    name_field = next(f for f in fields if f["name"] == "name")
    assert name_field["type"] == "Annotated[str, StringConstraints(max_length=2000)]"
    assert name_field["description"] == "Name of the person"

    age_field = next(f for f in fields if f["name"] == "age")
    assert age_field["type"] == "int"
    assert age_field["description"] == ""

    score_field = next(f for f in fields if f["name"] == "score")
    assert score_field["type"] == "float | None"
    assert score_field["description"] == "Score value"

    is_active_field = next(f for f in fields if f["name"] == "is_active")
    assert is_active_field["type"] == "bool | None"
    assert is_active_field["description"] == "Active flag"

    tags_field = next(f for f in fields if f["name"] == "tags")
    assert tags_field["type"] == "list[Annotated[str, StringConstraints(max_length=2000)]] | None"
    assert tags_field["description"] == ""

    metadata_field = next(f for f in fields if f["name"] == "metadata")
    assert metadata_field["type"] == "dict[str, Any] | None"
    assert metadata_field["description"] == "Extra metadata"


def test_resolve_json_schema_to_fields_unknown_type() -> None:
    schema: dict[str, Any] = {
        "properties": {
            "unknown_field": {"type": "unknown_type"},
        },
        "required": ["unknown_field"],
    }

    fields = resolve_json_schema_to_fields(schema)
    assert len(fields) == 1
    assert fields[0]["type"] == "Any"


def test_resolve_json_schema_to_fields_empty() -> None:
    fields = resolve_json_schema_to_fields({})
    assert fields == []
