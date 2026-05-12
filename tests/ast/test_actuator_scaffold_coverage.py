# Copyright (c) 2026 CoReason, Inc.
import libcst as cst

from coreason_meta_engineering.ast.actuator_scaffold import LogicInjectionFunctor


def test_logic_injection_functor_complex_scenarios() -> None:
    # Test case for raw statements in logic_body (hits line 109)
    # Test case for Any/Annotated/StringConstraints needs (hits lines 160-229)
    # Test case for required_imports (hits lines 231-235)

    geometric_schema = [
        {"name": "x", "type": "Annotated[int, StringConstraints(max_length=10)]"},
        {"name": "y", "type": "Any"},
    ]

    functor = LogicInjectionFunctor(
        actuator_name="test_tool",
        geometric_schema=geometric_schema,
        return_type="Any",
        action_space_id="urn:test:v1",
        required_imports=["import os", "from math import sqrt"],
        logic_body="print('hello world')",
        agent_instruction="Instruction",
        causal_affordance="Affordance",
        epistemic_bounds="Bounds",
    )

    code = "import sys\n"
    module = cst.parse_module(code)
    modified = module.visit(functor)

    generated_code = modified.code
    assert "import os" in generated_code
    assert "from math import sqrt" in generated_code
    assert "from typing import Any, Annotated" in generated_code
    assert "from pydantic import StringConstraints" in generated_code
    assert "print('hello world')" in generated_code
    assert "AGENT INSTRUCTION: Instruction" in generated_code
    assert "Any" in generated_code
    assert "__action_space_urn__" in generated_code


def test_logic_injection_functor_idempotency() -> None:
    functor = LogicInjectionFunctor(
        actuator_name="test_tool", geometric_schema=[], return_type="int", action_space_id="urn:test:v1"
    )

    code = "def test_tool(): pass"
    module = cst.parse_module(code)
    modified = module.visit(functor)

    # Should not change the code because test_tool already exists
    assert modified.code == code


def test_logic_injection_functor_malformed_logic() -> None:
    functor = LogicInjectionFunctor(
        actuator_name="test_tool",
        geometric_schema=[],
        return_type="int",
        action_space_id="urn:test:v1",
        logic_body="if true: # malformed",
    )

    code = ""
    module = cst.parse_module(code)
    modified = module.visit(functor)
    assert "pass" in modified.code  # Fallback to Pass()


def test_logic_injection_functor_invalid_required_import() -> None:
    functor = LogicInjectionFunctor(
        actuator_name="test_tool",
        geometric_schema=[],
        return_type="int",
        action_space_id="urn:test:v1",
        required_imports=["not a valid import!"],
    )

    code = ""
    module = cst.parse_module(code)
    modified = module.visit(functor)
    assert "not a valid import!" not in modified.code
