# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

import libcst as cst

from coreason_meta_engineering.ast.state_reconciliation import StateReconciliationFunctor


def test_state_reconciliation_existing_class() -> None:
    source_code = '''
from typing import Any
from pydantic import Field

class MyExistingState(CoreasonBaseState):
    """
    AGENT INSTRUCTION: This is the original docstring.
    MCP ROUTING TRIGGERS: urn:coreason:actionspace:test:v1
    """
    __action_space_urn__ = "urn:coreason:actionspace:test:v1"
    
    old_field: str = Field(description="Old field")
    
MyExistingState.model_rebuild()
'''
    module = cst.parse_module(source_code)
    geometric_schema = [
        {"name": "new_field", "type": "int", "description": "A shiny new integer field"},
        {"name": "items", "type": "list[str]", "description": "List of strings"},
    ]

    transformer = StateReconciliationFunctor(
        state_name="MyExistingState",
        geometric_schema=geometric_schema,
        action_space_id="urn:coreason:actionspace:test:v1",
    )

    new_module = module.visit(transformer)
    new_code = new_module.code

    assert "class MyExistingState(CoreasonBaseState):" in new_code
    assert "AGENT INSTRUCTION: This is the original docstring." in new_code
    assert "old_field" not in new_code
    assert 'new_field: int = Field(description="A shiny new integer field")' in new_code
    assert 'items: list[str] = Field(description="List of strings")' in new_code
    assert "def _enforce_canonical_sort(self) -> Self:" in new_code
    assert "from typing import Self" in new_code
    assert "from pydantic import model_validator" in new_code


def test_state_reconciliation_class_not_found() -> None:
    source_code = """
# Just some empty file
"""
    module = cst.parse_module(source_code)
    geometric_schema = [{"name": "new_field", "type": "int", "description": "A shiny new integer field"}]

    transformer = StateReconciliationFunctor(
        state_name="MyNewState", geometric_schema=geometric_schema, action_space_id="urn:coreason:actionspace:test:v2"
    )

    new_module = module.visit(transformer)
    new_code = new_module.code

    # Should fallback to scaffolding
    assert "class MyNewState(CoreasonBaseState):" in new_code
    assert '__action_space_urn__ = "urn:coreason:actionspace:test:v2"' in new_code
    assert "MyNewState.model_rebuild()" in new_code


def test_state_reconciliation_missing_docstring_and_urn() -> None:
    source_code = """
class MyExistingState:
    old_field: str
"""
    module = cst.parse_module(source_code)
    geometric_schema = [
        {"name": "new_field", "type": "Any", "description": "Any field"},
        {
            "name": "annotated_field",
            "type": "Annotated[str, StringConstraints(min_length=1)]",
            "description": "A field",
        },
    ]

    transformer = StateReconciliationFunctor(
        state_name="MyExistingState",
        geometric_schema=geometric_schema,
        action_space_id="urn:coreason:actionspace:test:v3",
    )

    new_module = module.visit(transformer)
    new_code = new_module.code

    assert "AGENT INSTRUCTION:" in new_code
    assert '__action_space_urn__ = "urn:coreason:actionspace:test:v3"' in new_code
    assert "Any" in new_code
    assert "Annotated" in new_code
    assert "StringConstraints" in new_code


def test_state_reconciliation_existing_imports() -> None:
    source_code = """
from typing import Any, Annotated, Self
from pydantic import Field, model_validator, StringConstraints

class MyState(CoreasonBaseState):
    pass
"""
    module = cst.parse_module(source_code)
    geometric_schema = [
        {"name": "items", "type": "list[str]", "description": "list"},
        {"name": "any_f", "type": "Any", "description": "any"},
        {"name": "ann_f", "type": "Annotated[str, StringConstraints()]", "description": "ann"},
    ]

    transformer = StateReconciliationFunctor(
        state_name="MyState",
        geometric_schema=geometric_schema,
        action_space_id="urn:coreason:actionspace:test:v4",
    )

    new_module = module.visit(transformer)
    new_code = new_module.code
    assert new_code.count("Any") == 2
    assert new_code.count("Field") == 4
