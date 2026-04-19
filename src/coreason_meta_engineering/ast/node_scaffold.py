# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import textwrap

import libcst as cst


class EpistemicNodeInjectionFunctor(cst.CSTTransformer):  # type: ignore[misc]
    """
    A decoupled libcst transformer that injects a newly defined Swarm Agent class
    into a given Python module AST.
    """

    def __init__(
        self,
        node_name: str,
        cognitive_boundary_directive: str,
        action_space_id: str,
        base_class: str = "CoReasonBaseAgent",
    ):
        super().__init__()
        self.node_name = node_name
        self.cognitive_boundary_directive = cognitive_boundary_directive
        self.action_space_id = action_space_id
        self.base_class = base_class

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

    def _build_urn_attribute(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(target=cst.Name(value="__action_space_urn__"))],
                    value=cst.SimpleString(value=f'"{self.action_space_id}"'),
                )
            ]
        )

    def _build_system_prompt_attribute(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(
            body=[
                cst.AnnAssign(
                    target=cst.Name(value="system_prompt"),
                    annotation=cst.Annotation(annotation=cst.Name(value="str")),
                    value=cst.SimpleString(value=f'"""{self.cognitive_boundary_directive}"""'),
                )
            ]
        )

    def _build_authorized_tools(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(
            body=[
                cst.AnnAssign(
                    target=cst.Name(value="authorized_tools"),
                    annotation=cst.Annotation(
                        annotation=cst.Subscript(
                            value=cst.Name(value="list"),
                            slice=[cst.SubscriptElement(slice=cst.Index(value=cst.Name(value="Any")))],
                        )
                    ),
                    value=cst.List(elements=[]),
                )
            ]
        )

    def _build_canonical_sort(self) -> cst.FunctionDef:
        return cst.FunctionDef(
            name=cst.Name(value="_enforce_canonical_sort"),
            params=cst.Parameters(params=[cst.Param(name=cst.Name(value="self"))]),
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
                                        cst.Arg(value=cst.SimpleString(value='"authorized_tools"')),
                                        cst.Arg(
                                            value=cst.Call(
                                                func=cst.Name(value="sorted"),
                                                args=[
                                                    cst.Arg(
                                                        value=cst.Attribute(
                                                            value=cst.Name(value="self"),
                                                            attr=cst.Name(value="authorized_tools"),
                                                        )
                                                    )
                                                ],
                                            )
                                        ),
                                    ],
                                )
                            )
                        ]
                    ),
                    cst.SimpleStatementLine(body=[cst.Return(value=cst.Name(value="self"))]),
                ]
            ),
            decorators=[
                cst.Decorator(
                    decorator=cst.Call(
                        func=cst.Name(value="model_validator"),
                        args=[
                            cst.Arg(
                                value=cst.SimpleString(value='"after"'),
                                keyword=cst.Name(value="mode"),
                                equal=cst.AssignEqual(),
                            )
                        ],
                    )
                )
            ],
            returns=cst.Annotation(annotation=cst.Name(value="Self")),
        )

    def _build_model_rebuild(self) -> cst.SimpleStatementLine:
        return cst.SimpleStatementLine(
            body=[
                cst.Expr(
                    value=cst.Call(
                        func=cst.Attribute(
                            value=cst.Name(value=self.node_name),
                            attr=cst.Name(value="model_rebuild"),
                        ),
                        args=[],
                    )
                )
            ]
        )

    def _build_class(self) -> cst.ClassDef:
        body_elements: list[cst.BaseStatement] = []
        body_elements.append(self._build_docstring())
        body_elements.append(self._build_urn_attribute())
        body_elements.append(self._build_system_prompt_attribute())
        body_elements.append(self._build_authorized_tools())
        body_elements.append(self._build_canonical_sort())

        return cst.ClassDef(
            name=cst.Name(value=self.node_name),
            bases=[cst.Arg(value=cst.Name(value=self.base_class))],
            body=cst.IndentedBlock(body=body_elements),
        )

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:  # noqa: N802, ARG002
        # Idempotency Axiom: If the class already exists, halt injection entirely.
        for stmt in updated_node.body:
            if isinstance(stmt, cst.ClassDef) and stmt.name.value == self.node_name:
                return updated_node

        new_class = self._build_class()

        has_any_import = False
        insert_import_idx = 0

        new_body = list(updated_node.body)

        has_typing_self = False
        has_pydantic_validator = False

        for stmt in new_body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for node in stmt.body:
                    if (
                        isinstance(node, cst.ImportFrom)
                        and getattr(node.module, "value", None) == "typing"
                        and isinstance(node.names, (tuple, list))
                    ):
                        for name_item in node.names:
                            if name_item.name.value == "Any":
                                has_any_import = True
                            if name_item.name.value == "Self":
                                has_typing_self = True

                    if (
                        isinstance(node, cst.ImportFrom)
                        and getattr(node.module, "value", None) == "pydantic"
                        and isinstance(node.names, (tuple, list))
                    ):
                        for name_item in node.names:
                            if name_item.name.value == "model_validator":
                                has_pydantic_validator = True

        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine) and any(
                isinstance(n, (cst.Import, cst.ImportFrom)) for n in stmt.body
            ):
                insert_import_idx = i + 1

        # Combine typing imports
        missing_typing = []
        if not has_any_import:
            missing_typing.append("Any")
        if not has_typing_self:
            missing_typing.append("Self")

        if missing_typing:
            typing_import = cst.SimpleStatementLine(
                body=[
                    cst.ImportFrom(
                        module=cst.Name(value="typing"),
                        names=[cst.ImportAlias(name=cst.Name(value=m)) for m in missing_typing],
                    )
                ]
            )
            new_body.insert(insert_import_idx, typing_import)

        if not has_pydantic_validator:
            pydantic_import = cst.SimpleStatementLine(
                body=[
                    cst.ImportFrom(
                        module=cst.Name(value="pydantic"),
                        names=[cst.ImportAlias(name=cst.Name(value="model_validator"))],
                    )
                ]
            )
            new_body.insert(insert_import_idx, pydantic_import)

        new_body.append(new_class)
        new_body.append(self._build_model_rebuild())

        return updated_node.with_changes(body=new_body)
