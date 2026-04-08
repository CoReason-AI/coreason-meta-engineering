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
import pydantic  # noqa: F401


class ClassInjectTransformer(cst.CSTTransformer):  # type: ignore
    """
    A decoupled libcst transformer that injects a newly defined class and its
    accompanying model_rebuild() call into a given Python module AST.
    """

    def __init__(self, name: str, fields: list[dict[str, typing.Any]]):
        super().__init__()
        self.name = name
        self.fields = fields

        self.docstring = textwrap.dedent(
            '''\
            """
            AGENT INSTRUCTION: [Define topological boundary]

            CAUSAL AFFORDANCE: [Define graph mutation or tool execution]

            EPISTEMIC BOUNDS: [Define mathematical/physical limits]

            MCP ROUTING TRIGGERS: [Comma-separated algorithmic tags]
            """'''
        )

    def _build_docstring(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value=self.docstring))])

    def _build_field(self, field_def: dict[str, typing.Any]) -> cst.SimpleStatementLine:
        name = field_def["name"]
        field_type = field_def["type"]
        description = field_def["description"]
        is_optional = field_def.get("optional", False)

        # Parse type annotation. We need to parse this string to CST nodes.
        type_node = cst.parse_expression(field_type)

        field_args = []
        if is_optional:
            field_args.append(
                cst.Arg(
                    value=cst.Name(value="None"),
                    keyword=cst.Name(value="default"),
                    equal=cst.AssignEqual(
                        whitespace_before=cst.SimpleWhitespace(""),
                        whitespace_after=cst.SimpleWhitespace(""),
                    ),
                )
            )

        field_args.append(
            cst.Arg(
                value=cst.SimpleString(value=f'"{description}"'),
                keyword=cst.Name(value="description"),
                equal=cst.AssignEqual(
                    whitespace_before=cst.SimpleWhitespace(""),
                    whitespace_after=cst.SimpleWhitespace(""),
                ),
            )
        )

        return cst.SimpleStatementLine(
            body=[
                cst.AnnAssign(
                    target=cst.Name(value=name),
                    annotation=cst.Annotation(annotation=type_node),
                    value=cst.Call(
                        func=cst.Name(value="Field"),
                        args=field_args,
                    ),
                )
            ]
        )

    def _build_validator(self, list_fields: list[str]) -> cst.FunctionDef:
        body_lines: list[cst.BaseStatement] = [
            cst.If(
                test=cst.Comparison(
                    left=cst.Call(
                        func=cst.Name(value="getattr"),
                        args=[
                            cst.Arg(value=cst.Name(value="self")),
                            cst.Arg(value=cst.SimpleString(value=f'"{field}"')),
                            cst.Arg(value=cst.Name(value="None")),
                        ],
                    ),
                    comparisons=[
                        cst.ComparisonTarget(
                            operator=cst.IsNot(),
                            comparator=cst.Name(value="None"),
                        ),
                    ],
                ),
                body=cst.IndentedBlock(
                    body=[
                        cst.SimpleStatementLine(
                            body=[
                                cst.Expr(
                                    value=cst.Call(
                                        func=cst.Attribute(
                                            value=cst.Name(value="object"), attr=cst.Name(value="__setattr__")
                                        ),
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
                    ]
                ),
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
            if "list[" in f["type"]:
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

        # Gather required imports based on schema fields
        needs_any = any("Any" in f["type"] for f in self.fields)
        needs_annotated = any("Annotated" in f["type"] for f in self.fields)
        needs_string_constraints = any("StringConstraints" in f["type"] for f in self.fields)

        has_self_import = False
        has_any_import = False
        has_annotated_import = False
        has_field_import = False
        has_string_constraints_import = False

        for stmt in updated_node.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for node in stmt.body:
                    if isinstance(node, cst.ImportFrom) and node.module and isinstance(node.names, (tuple, list)):
                        mod_name = getattr(node.module, "value", None)
                        for name_item in node.names:
                            if mod_name == "typing":
                                if name_item.name.value == "Self":
                                    has_self_import = True
                                if name_item.name.value == "Any":
                                    has_any_import = True
                                if name_item.name.value == "Annotated":
                                    has_annotated_import = True
                            elif mod_name == "pydantic":
                                if name_item.name.value == "Field":
                                    has_field_import = True
                                if name_item.name.value == "StringConstraints":
                                    has_string_constraints_import = True

        new_body = list(updated_node.body)

        insert_import_idx = 0
        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine) and any(
                isinstance(n, (cst.Import, cst.ImportFrom)) for n in stmt.body
            ):
                insert_import_idx = i + 1
                break

        typing_imports = []
        if not has_self_import:
            typing_imports.append(cst.ImportAlias(name=cst.Name(value="Self")))
        if needs_any and not has_any_import:
            typing_imports.append(cst.ImportAlias(name=cst.Name(value="Any")))
        if needs_annotated and not has_annotated_import:
            typing_imports.append(cst.ImportAlias(name=cst.Name(value="Annotated")))

        if typing_imports:
            new_body.insert(
                insert_import_idx,
                cst.SimpleStatementLine(
                    body=[cst.ImportFrom(module=cst.Name(value="typing"), names=typing_imports)]
                ),
            )
            insert_import_idx += 1

        pydantic_imports = []
        if not has_field_import:
            pydantic_imports.append(cst.ImportAlias(name=cst.Name(value="Field")))
        if needs_string_constraints and not has_string_constraints_import:
            pydantic_imports.append(cst.ImportAlias(name=cst.Name(value="StringConstraints")))

        if pydantic_imports:
            new_body.insert(
                insert_import_idx,
                cst.SimpleStatementLine(
                    body=[cst.ImportFrom(module=cst.Name(value="pydantic"), names=pydantic_imports)]
                ),
            )
            insert_import_idx += 1

        # We need to insert before the first .model_rebuild() call.
        # If none exists, we append to the end.
        insert_idx = len(new_body)

        for i, stmt in enumerate(new_body):
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
                if insert_idx != len(new_body):
                    break

        new_body.insert(insert_idx, new_class)
        new_body.insert(insert_idx + 1, new_rebuild)

        return updated_node.with_changes(body=new_body)
