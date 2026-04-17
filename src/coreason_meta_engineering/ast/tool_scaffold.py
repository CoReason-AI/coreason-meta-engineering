# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

import textwrap
import typing

import libcst as cst


class FunctionInjectTransformer(cst.CSTTransformer):  # type: ignore[misc]
    """
    A decoupled libcst transformer that injects a newly defined function bounded by
    the @mcp.tool() decorator.
    """

    def __init__(
        self,
        tool_name: str,
        parameters: list[dict[str, typing.Any]],
        return_type: str,
        action_space_id: str,
    ):
        super().__init__()
        self.tool_name = tool_name
        self.parameters = parameters
        self.return_type = return_type
        self.action_space_id = action_space_id

        self.docstring = textwrap.dedent(
            f'''\
            """
            AGENT INSTRUCTION: [Define topological boundary]

            CAUSAL AFFORDANCE: [Define graph mutation or tool execution]

            EPISTEMIC BOUNDS: [Define mathematical/physical limits]

            MCP ROUTING TRIGGERS: {self.action_space_id}
            """'''
        )

    def _build_docstring(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value=self.docstring))])

    def _build_parameter(self, param_def: dict[str, typing.Any]) -> cst.Param:
        # Schema provides name and type
        name = param_def["name"]
        field_type_str = param_def["type"]
        type_node = cst.parse_expression(field_type_str)
        return cst.Param(name=cst.Name(value=name), annotation=cst.Annotation(annotation=type_node))

    def _build_urn_attribute(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[
                        cst.AssignTarget(
                            target=cst.Attribute(
                                value=cst.Name(value=self.tool_name),
                                attr=cst.Name(value="__action_space_urn__"),
                            )
                        )
                    ],
                    value=cst.SimpleString(value=f'"{self.action_space_id}"'),
                )
            ]
        )

    def _build_function(self) -> cst.FunctionDef:
        body_elements: list[cst.BaseStatement] = []
        body_elements.append(self._build_docstring())
        body_elements.append(cst.SimpleStatementLine(body=[cst.Pass()]))

        params = [self._build_parameter(p) for p in self.parameters]

        return cst.FunctionDef(
            name=cst.Name(value=self.tool_name),
            params=cst.Parameters(params=params),
            body=cst.IndentedBlock(body=body_elements),
            decorators=[
                cst.Decorator(
                    decorator=cst.Call(
                        func=cst.Attribute(value=cst.Name(value="mcp"), attr=cst.Name(value="tool")),
                        args=[],
                    )
                )
            ],
            returns=cst.Annotation(annotation=cst.parse_expression(self.return_type)) if self.return_type else None,
        )

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:  # noqa: N802, ARG002
        # Idempotency Axiom: If the function already exists, halt injection entirely.
        for stmt in updated_node.body:
            if isinstance(stmt, cst.FunctionDef) and stmt.name.value == self.tool_name:
                return updated_node

        new_function = self._build_function()

        has_mcp_import = False
        insert_import_idx = 0

        new_body = list(updated_node.body)

        # Proper check
        for stmt in new_body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for node in stmt.body:
                    if isinstance(node, cst.ImportFrom):
                        # Construct fully qualified path
                        pass

        # Since it's easier to just string-match the import logic for idempotency inside leave_Module if CST gets hairy:
        for stmt in updated_node.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for node in stmt.body:
                    if isinstance(node, cst.ImportFrom) and isinstance(node.names, (tuple, list)):
                        for name_item in node.names:
                            if name_item.name.value == "mcp":
                                has_mcp_import = True

        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine) and any(
                isinstance(n, (cst.Import, cst.ImportFrom)) for n in stmt.body
            ):
                insert_import_idx = i + 1

        if not has_mcp_import:
            # We want: from mcp.server.fastmcp import mcp
            mcp_import = cst.SimpleStatementLine(
                body=[
                    cst.ImportFrom(
                        module=cst.Attribute(
                            value=cst.Attribute(value=cst.Name(value="mcp"), attr=cst.Name(value="server")),
                            attr=cst.Name(value="fastmcp"),
                        ),
                        names=[cst.ImportAlias(name=cst.Name(value="mcp"))],
                    )
                ]
            )
            new_body.insert(insert_import_idx, mcp_import)

        new_body.append(new_function)
        new_body.append(self._build_urn_attribute())

        return updated_node.with_changes(body=new_body)
