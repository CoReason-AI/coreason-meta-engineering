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
import pydantic  # noqa: F401


class ClassInjectTransformer(cst.CSTTransformer):  # type: ignore[misc]
    """
    A decoupled libcst transformer that injects a newly defined class and its
    accompanying model_rebuild() call into a given Python module AST.
    """

    def __init__(self, name: str, fields: list[dict[str, str]]):
        super().__init__()
        self.name = name
        self.fields = fields

        self.docstring = (
            '"""\n    AGENT INSTRUCTION: [Define topological boundary]\n\n'
            "    CAUSAL AFFORDANCE: [Define graph mutation or tool execution]\n\n"
            "    EPISTEMIC BOUNDS: [Define mathematical/physical limits]\n\n"
            '    MCP ROUTING TRIGGERS: [Comma-separated algorithmic tags]\n    """'
        )

    def _build_docstring(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value=self.docstring))])

    def _build_field(self, field_def: dict[str, str]) -> cst.SimpleStatementLine:
        name = field_def["name"]
        field_type = field_def["type"]
        description = field_def["description"]

        # Parse type annotation. We need to parse this string to CST nodes.
        type_node = cst.parse_expression(field_type)

        return cst.SimpleStatementLine(
            body=[
                cst.AnnAssign(
                    target=cst.Name(value=name),
                    annotation=cst.Annotation(annotation=type_node),
                    value=cst.Call(
                        func=cst.Name(value="Field"),
                        args=[
                            cst.Arg(
                                value=cst.SimpleString(value=f'"{description}"'),
                                keyword=cst.Name(value="description"),
                                equal=cst.AssignEqual(
                                    whitespace_before=cst.SimpleWhitespace(""),
                                    whitespace_after=cst.SimpleWhitespace(""),
                                ),
                            )
                        ],
                    ),
                )
            ]
        )

    def _build_validator(self, list_fields: list[str]) -> cst.FunctionDef:
        body_lines: list[cst.BaseStatement] = [
            cst.SimpleStatementLine(
                body=[
                    cst.Expr(
                        value=cst.Call(
                            func=cst.Attribute(value=cst.Name(value="object"), attr=cst.Name(value="__setattr__")),
                            args=[
                                cst.Arg(value=cst.Name(value="self")),
                                cst.Arg(value=cst.SimpleString(value=f'"{field}"')),
                                cst.Arg(
                                    value=cst.Call(
                                        func=cst.Name(value="sorted"),
                                        args=[
                                            cst.Arg(
                                                value=cst.Attribute(
                                                    value=cst.Name(value="self"), attr=cst.Name(value=field)
                                                )
                                            )
                                        ],
                                    )
                                ),
                            ],
                        )
                    )
                ]
            )
            for field in list_fields
        ]

        body_lines.append(cst.SimpleStatementLine(body=[cst.Return(value=cst.Name(value="self"))]))

        return cst.FunctionDef(
            name=cst.Name(value="_enforce_canonical_sort"),
            params=cst.Parameters(params=[cst.Param(name=cst.Name(value="self"))]),
            body=cst.IndentedBlock(body=body_lines),
            decorators=[
                cst.Decorator(
                    decorator=cst.Call(
                        func=cst.Name(value="model_validator"),
                        args=[
                            cst.Arg(
                                value=cst.SimpleString(value='"after"'),
                                keyword=cst.Name(value="mode"),
                                equal=cst.AssignEqual(
                                    whitespace_before=cst.SimpleWhitespace(""),
                                    whitespace_after=cst.SimpleWhitespace(""),
                                ),
                            )
                        ],
                    )
                )
            ],
            returns=cst.Annotation(annotation=cst.Name(value="Self")),
        )

    def _build_class(self) -> cst.ClassDef:
        body_elements: list[cst.BaseStatement] = []
        body_elements.append(self._build_docstring())

        list_fields = []
        for f in self.fields:
            body_elements.append(self._build_field(f))
            if f["type"].startswith("list["):
                list_fields.append(f["name"])

        if list_fields:
            # Need to append empty line manually or just function def
            body_elements.append(self._build_validator(list_fields))

        return cst.ClassDef(
            name=cst.Name(value=self.name),
            bases=[cst.Arg(value=cst.Name(value="CoreasonBaseState"))],
            body=cst.IndentedBlock(body=body_elements),
        )

    def _build_rebuild_call(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(
            body=[
                cst.Expr(
                    value=cst.Call(
                        func=cst.Attribute(value=cst.Name(value=self.name), attr=cst.Name(value="model_rebuild"))
                    )
                )
            ]
        )

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:  # noqa: N802, ARG002
        new_class = self._build_class()
        new_rebuild = self._build_rebuild_call()

        # We need to insert before the first .model_rebuild() call.
        # If none exists, we append to the end.
        insert_idx = len(updated_node.body)

        for i, stmt in enumerate(updated_node.body):
            if isinstance(stmt, cst.SimpleStatementLine):
                for expr in stmt.body:
                    if (
                        isinstance(expr, cst.Expr)
                        and isinstance(expr.value, cst.Call)
                        and isinstance(expr.value.func, cst.Attribute)
                        and expr.value.func.attr.value == "model_rebuild"
                    ):
                        insert_idx = i
                        break
                if insert_idx != len(updated_node.body):
                    break

        new_body = list(updated_node.body)
        new_body.insert(insert_idx, new_class)
        new_body.insert(insert_idx + 1, new_rebuild)

        return updated_node.with_changes(body=new_body)
