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

from coreason_meta_engineering.ast.scaffold import ClassInjectTransformer


def test_class_inject_basic_and_docstring() -> None:
    code = "import pydantic\n"
    module = cst.parse_module(code)
    fields = [{"name": "basic_field", "type": "int", "description": "basic int field"}]
    transformer = ClassInjectTransformer("NewState", fields)
    modified = module.visit(transformer)
    modified_code = modified.code

    # Verify class inheritance
    assert "class NewState(CoreasonBaseState):" in modified_code

    # Verify 4-part docstring
    assert "AGENT INSTRUCTION: [Define topological boundary]" in modified_code
    assert "CAUSAL AFFORDANCE: [Define graph mutation or tool execution]" in modified_code
    assert "EPISTEMIC BOUNDS: [Define mathematical/physical limits]" in modified_code
    assert "MCP ROUTING TRIGGERS: [Comma-separated algorithmic tags]" in modified_code

    # Verify field
    assert 'basic_field: int = Field(description="basic int field")' in modified_code

    # Verify model_rebuild logic for empty file
    assert "NewState.model_rebuild()" in modified_code


def test_class_inject_list_validator() -> None:
    code = "import pydantic\n"
    module = cst.parse_module(code)
    fields = [
        {"name": "str_list", "type": "list[str]", "description": "a list of strings"},
        {"name": "int_field", "type": "int", "description": "just an int"},
    ]
    transformer = ClassInjectTransformer("SortState", fields)
    modified = module.visit(transformer)
    modified_code = modified.code

    # Verify lists field parsing
    assert 'str_list: list[str] = Field(description="a list of strings")' in modified_code
    assert 'int_field: int = Field(description="just an int")' in modified_code

    # Verify enforce_canonical_sort validator exists
    assert '@model_validator(mode="after")' in modified_code
    assert "def _enforce_canonical_sort(self) -> Self:" in modified_code
    assert 'object.__setattr__(self, "str_list", sorted(self.str_list))' in modified_code


def test_class_inject_before_existing_rebuild() -> None:
    code = "class Existing(CoreasonBaseState):\n    pass\nExisting.model_rebuild()\n"
    module = cst.parse_module(code)
    fields = [{"name": "f1", "type": "str", "description": "d1"}]
    transformer = ClassInjectTransformer("InjectedClass", fields)
    modified = module.visit(transformer)
    modified_code = modified.code

    # Verify InjectedClass model_rebuild is placed before Existing.model_rebuild
    injected_idx = modified_code.find("InjectedClass.model_rebuild()")
    existing_idx = modified_code.find("Existing.model_rebuild()")

    assert injected_idx != -1
    assert existing_idx != -1
    assert injected_idx < existing_idx

    # Verify the class is inserted before Existing model rebuild
    class_idx = modified_code.find("class InjectedClass")
    assert class_idx < injected_idx
