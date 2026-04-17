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

import libcst as cst

from coreason_meta_engineering.ast.scaffold import ClassInjectTransformer

TEST_URN = "urn:coreason:actionspace:test:v1"


def test_class_inject_basic_and_docstring() -> None:
    code = "import pydantic\n"
    module = cst.parse_module(code)
    fields = [{"name": "basic_field", "type": "int", "description": "basic int field"}]
    transformer = ClassInjectTransformer("NewState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    # Verify class inheritance
    assert "class NewState(CoreasonBaseState):" in modified_code

    # Verify 4-part docstring
    assert "AGENT INSTRUCTION: [Define topological boundary]" in modified_code
    assert "CAUSAL AFFORDANCE: [Define graph mutation or tool execution]" in modified_code
    assert "EPISTEMIC BOUNDS: [Define mathematical/physical limits]" in modified_code

    # Verify URN Discovery Trigger in docstring
    assert f"MCP ROUTING TRIGGERS: {TEST_URN}" in modified_code

    # Verify URN class attribute
    assert f'__action_space_urn__ = "{TEST_URN}"' in modified_code

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
    transformer = ClassInjectTransformer("SortState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    # Verify lists field parsing
    assert 'str_list: list[str] = Field(description="a list of strings")' in modified_code
    assert 'int_field: int = Field(description="just an int")' in modified_code

    # Verify enforce_canonical_sort validator exists
    assert '@model_validator(mode="after")' in modified_code
    assert "def _enforce_canonical_sort(self) -> Self:" in modified_code
    assert 'if getattr(self, "str_list", None) is not None:' in modified_code
    assert 'object.__setattr__(self, "str_list", sorted(self.str_list))' in modified_code


def test_class_inject_optional_list_validator() -> None:
    code = "import pydantic\n"
    module = cst.parse_module(code)
    fields = [
        {"name": "opt_list", "type": "list[str] | None", "description": "optional list"},
        {"name": "ann_list", "type": "Annotated[list[int], Field()]", "description": "annotated list"},
    ]
    transformer = ClassInjectTransformer("SortOptState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    # Verify both fragile arrays were detected
    assert 'if getattr(self, "opt_list", None) is not None:' in modified_code
    assert 'if getattr(self, "ann_list", None) is not None:' in modified_code

    # Verify missing import insertion
    assert "from typing import Self" in modified_code


def test_class_inject_self_import_exists() -> None:
    code = "from typing import Self\nimport pydantic\n"
    module = cst.parse_module(code)
    fields = [{"name": "basic_field", "type": "list[int]", "description": "basic int field"}]
    transformer = ClassInjectTransformer("NewState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    # Should only be imported once (already existing, should not be injected again)
    assert modified_code.count("from typing import Self") == 1


def test_class_inject_before_existing_rebuild() -> None:
    code = "class Existing(CoreasonBaseState):\n    pass\nExisting.model_rebuild()\n"
    module = cst.parse_module(code)
    fields = [{"name": "f1", "type": "str", "description": "d1"}]
    transformer = ClassInjectTransformer("InjectedClass", fields, action_space_id=TEST_URN)
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


def test_class_inject_auto_imports() -> None:
    code = "import pydantic\n"
    module = cst.parse_module(code)
    fields: list[dict[str, Any]] = [
        {
            "name": "basic",
            "type": "Annotated[str, StringConstraints(max_length=20)] | None",
            "description": "basic",
            "optional": True,
        },
        {"name": "metadata", "type": "dict[str, Any]", "description": "meta"},
        {"name": "a_list", "type": "list[int]", "description": "a list"},
    ]
    transformer = ClassInjectTransformer("AutoImportState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    assert "from typing import Self, Any, Annotated" in modified_code
    assert "from pydantic import Field, model_validator, StringConstraints" in modified_code


def test_class_inject_auto_imports_existing() -> None:
    code = "from typing import Self, Any, Annotated\nfrom pydantic import Field, model_validator, StringConstraints\n"
    module = cst.parse_module(code)
    fields: list[dict[str, Any]] = [
        {
            "name": "basic",
            "type": "Annotated[str, StringConstraints(max_length=20)] | None",
            "description": "basic",
            "optional": True,
        },
        {"name": "metadata", "type": "dict[str, Any]", "description": "meta"},
        {"name": "a_list", "type": "list[int]", "description": "a list"},
    ]
    transformer = ClassInjectTransformer("AutoImportState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    assert modified_code.count("Any") == 2
    assert modified_code.count("Annotated") == 2
    assert modified_code.count("Self") == 2
    assert modified_code.count("Field") == 4
    assert modified_code.count("model_validator") == 2
    assert modified_code.count("StringConstraints") == 2


def test_class_inject_no_list_no_self_or_model_validator() -> None:
    code = "import pydantic\n"
    module = cst.parse_module(code)
    fields: list[dict[str, Any]] = [
        {
            "name": "basic",
            "type": "int",
            "description": "basic",
        },
    ]
    transformer = ClassInjectTransformer("NoListState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    assert "Self" not in modified_code
    assert "model_validator" not in modified_code


def test_class_inject_idempotency() -> None:
    """The Idempotency Axiom: injecting the same class twice must not duplicate."""
    code = "class IdempotentState(CoreasonBaseState):\n    pass\nIdempotentState.model_rebuild()\n"
    module = cst.parse_module(code)
    fields = [{"name": "f1", "type": "int", "description": "a field"}]
    transformer = ClassInjectTransformer("IdempotentState", fields, action_space_id=TEST_URN)
    modified = module.visit(transformer)
    modified_code = modified.code

    # The class must not be duplicated
    assert modified_code.count("class IdempotentState") == 1

    # model_rebuild must not be duplicated
    assert modified_code.count("IdempotentState.model_rebuild()") == 1

    # The code should be returned unchanged
    assert modified_code == code
