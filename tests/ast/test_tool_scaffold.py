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

from coreason_meta_engineering.ast.tool_scaffold import FunctionInjectTransformer


def test_function_inject_transformer_basic() -> None:
    source = "def existing_function():\n    pass\n"
    module = cst.parse_module(source)
    transformer = FunctionInjectTransformer(
        tool_name="my_new_tool",
        parameters=[{"name": "x", "type": "int"}],
        return_type="str",
        action_space_id="urn:coreason:actionspace:my_tool:v1",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    assert "def my_new_tool(x: int) -> str:" in code
    assert "@mcp.tool()" in code
    assert 'my_new_tool.__action_space_urn__ = "urn:coreason:actionspace:my_tool:v1"' in code
    assert "MCP ROUTING TRIGGERS: urn:coreason:actionspace:my_tool:v1" in code
    assert "from mcp.server.fastmcp import mcp" in code
    assert "existing_function" in code


def test_function_inject_transformer_idempotency() -> None:
    source = "def my_new_tool():\n    pass\n"
    module = cst.parse_module(source)
    transformer = FunctionInjectTransformer(
        tool_name="my_new_tool",
        parameters=[],
        return_type="None",
        action_space_id="urn:coreason:actionspace:my_tool:v1",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    # Should not inject a second time
    assert code.count("def my_new_tool") == 1
    assert "@mcp.tool()" not in code


def test_function_inject_no_return_type() -> None:
    source = ""
    module = cst.parse_module(source)
    transformer = FunctionInjectTransformer(
        tool_name="no_return", parameters=[], return_type="", action_space_id="urn:coreason:actionspace:no_ret:v1"
    )
    new_module = module.visit(transformer)
    code = new_module.code

    assert "def no_return():" in code
    assert "-> " not in code


def test_function_inject_with_existing_mcp_import() -> None:
    source = "from mcp.server.fastmcp import mcp\n"
    module = cst.parse_module(source)
    transformer = FunctionInjectTransformer(tool_name="my_tool", parameters=[], return_type="", action_space_id="urn:x")
    new_module = module.visit(transformer)
    code = new_module.code

    # Should not add another import
    assert code.count("from mcp.server.fastmcp import mcp") == 1
