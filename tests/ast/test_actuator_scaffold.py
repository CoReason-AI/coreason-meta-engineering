# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import libcst as cst

from coreason_meta_engineering.ast.actuator_scaffold import LogicInjectionFunctor


def test_function_inject_transformer_basic() -> None:
    source = "def existing_function():\n    pass\n"
    module = cst.parse_module(source)
    transformer = LogicInjectionFunctor(
        actuator_name="my_new_actuator",
        geometric_schema=[
            {"name": "x", "type": "int"},
            {"name": "y", "type": "Annotated[str, StringConstraints(max_length=200)]"},
        ],
        return_type="str",
        action_space_id="urn:coreason:actionspace:my_actuator:v1",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    assert "def my_new_actuator(x: int, y: Annotated[str, StringConstraints(max_length=200)]) -> str:" in code
    assert "@mcp.tool()" in code
    assert 'my_new_actuator.__action_space_urn__ = "urn:coreason:actionspace:my_actuator:v1"' in code
    assert "MCP ROUTING TRIGGERS: urn:coreason:actionspace:my_actuator:v1" in code
    assert "from mcp.server.fastmcp import mcp" in code
    assert "from typing import Annotated" in code
    assert "from pydantic import StringConstraints" in code
    assert "existing_function" in code


def test_function_inject_transformer_idempotency() -> None:
    source = "def my_new_actuator():\n    pass\n"
    module = cst.parse_module(source)
    transformer = LogicInjectionFunctor(
        actuator_name="my_new_actuator",
        geometric_schema=[],
        return_type="None",
        action_space_id="urn:coreason:actionspace:my_actuator:v1",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    # Should not inject a second time
    assert code.count("def my_new_actuator") == 1
    assert "@mcp.tool()" not in code


def test_function_inject_no_return_type() -> None:
    source = ""
    module = cst.parse_module(source)
    transformer = LogicInjectionFunctor(
        actuator_name="no_return",
        geometric_schema=[],
        return_type="",
        action_space_id="urn:coreason:actionspace:no_ret:v1",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    assert "def no_return():" in code
    assert "-> " not in code


def test_function_inject_with_existing_mcp_import() -> None:
    source = (
        "from pydantic import StringConstraints\n"
        "from typing import Any, Annotated\n"
        "from mcp.server.fastmcp import mcp\n"
    )
    module = cst.parse_module(source)
    transformer = LogicInjectionFunctor(
        actuator_name="my_actuator",
        geometric_schema=[{"name": "a", "type": "Annotated[Any, StringConstraints()]"}],
        return_type="",
        action_space_id="urn:x",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    # Should not add another import
    assert code.count("from mcp.server.fastmcp import mcp") == 1
    assert code.count("StringConstraints") == 2
    assert code.count("from typing import Any, Annotated") == 1


def test_function_inject_with_any_import() -> None:
    source = "def x(): pass\n"
    module = cst.parse_module(source)
    transformer = LogicInjectionFunctor(
        actuator_name="my_actuator",
        geometric_schema=[{"name": "a", "type": "Any"}],
        return_type="",
        action_space_id="urn:x",
    )
    new_module = module.visit(transformer)
    assert "from typing import Any" in new_module.code
