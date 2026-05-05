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
import typing

import libcst as cst


class LogicInjectionFunctor(cst.CSTTransformer):  # type: ignore[misc]
    """
    A decoupled libcst transformer that injects a newly defined function bounded by
    the @mcp.tool() decorator.
    """

    def __init__(
        self,
        actuator_name: str,
        geometric_schema: list[dict[str, typing.Any]],
        return_type: str,
        action_space_id: str,
        required_imports: list[str] | None = None,
        logic_body: str | None = None,
        agent_instruction: str | None = None,
        causal_affordance: str | None = None,
        epistemic_bounds: str | None = None,
    ):
        super().__init__()
        self.actuator_name = actuator_name
        self.geometric_schema = geometric_schema
        self.return_type = return_type
        self.action_space_id = action_space_id
        self.required_imports = required_imports or []
        self.logic_body = logic_body

        ai = agent_instruction or "[Define topological boundary]"
        ca = causal_affordance or "[Define graph mutation or tool execution]"
        eb = epistemic_bounds or "[Define mathematical/physical limits]"

        self.docstring = textwrap.dedent(
            f'''\
            """
            AGENT INSTRUCTION: {ai}

            CAUSAL AFFORDANCE: {ca}

            EPISTEMIC BOUNDS: {eb}

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
                                value=cst.Name(value=self.actuator_name),
                                attr=cst.Name(value="__action_space_urn__"),
                            )
                        )
                    ],
                    value=cst.SimpleString(value=f'"{self.action_space_id}"'),
                )
            ]
        )

    def _extract_logic_body_parts(self) -> tuple[list[cst.BaseStatement], list[cst.Param] | None]:
        """Parse logic_body and extract inlined statements + function params.

        Returns a tuple of (body_statements, params_or_none).
        If logic_body contains a function def, extracts its body and params.
        If logic_body is raw statements, returns them directly with no params.
        """
        if not self.logic_body:
            return [], None

        try:
            parsed = cst.parse_module(textwrap.dedent(self.logic_body))
        except Exception:
            return [], None

        for stmt in parsed.body:
            if isinstance(stmt, cst.FunctionDef):
                # Extract body statements from the inner function (inline them)
                inner_body = typing.cast(list[cst.BaseStatement], list(stmt.body.body))
                # Extract params from the inner function signature
                inner_params = list(stmt.params.params)
                return inner_body, inner_params

        # logic_body is raw statements, not a function def
        return list(parsed.body), None

    def _build_function(self) -> cst.FunctionDef:
        body_elements: list[cst.BaseStatement] = []
        body_elements.append(self._build_docstring())

        # Cascading priority for function body:
        # 1. logic_body statements (inlined, not nested)
        # 2. Pass() fallback
        logic_stmts, logic_params = self._extract_logic_body_parts()
        if logic_stmts:
            body_elements.extend(logic_stmts)
        else:
            body_elements.append(cst.SimpleStatementLine(body=[cst.Pass()]))

        # Cascading priority for parameters:
        # 1. logic_body function signature (ground truth from LLM code)
        # 2. geometric_schema (JSON Schema properties)
        # 3. empty params
        if logic_params is not None:
            params = logic_params
        elif self.geometric_schema:
            params = [self._build_parameter(p) for p in self.geometric_schema]
        else:
            params = []

        return cst.FunctionDef(
            name=cst.Name(value=self.actuator_name),
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
            if isinstance(stmt, cst.FunctionDef) and stmt.name.value == self.actuator_name:
                return updated_node

        new_function = self._build_function()

        needs_any = any("Any" in p.get("type", "") for p in self.geometric_schema) or (
            self.return_type and "Any" in self.return_type
        )
        needs_annotated = any("Annotated" in p.get("type", "") for p in self.geometric_schema) or (
            self.return_type and "Annotated" in self.return_type
        )
        needs_stringconfig = any("StringConstraints" in p.get("type", "") for p in self.geometric_schema)

        has_mcp_import = False
        has_any_import = False
        has_annotated_import = False
        has_stringconstraints_import = False
        insert_import_idx = 0

        new_body = list(updated_node.body)

        for stmt in new_body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for node in stmt.body:
                    if isinstance(node, cst.ImportFrom) and isinstance(node.names, (tuple, list)):
                        mod_name = ""
                        if getattr(node, "module", None) is not None and isinstance(node.module, cst.Name):
                            mod_name = node.module.value

                        for name_item in node.names:
                            val = name_item.name.value
                            if val == "mcp":
                                has_mcp_import = True
                            if val == "Any" and mod_name == "typing":
                                has_any_import = True
                            if val == "Annotated" and mod_name == "typing":
                                has_annotated_import = True
                            if val == "StringConstraints" and mod_name == "pydantic":
                                has_stringconstraints_import = True

        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine) and any(
                isinstance(n, (cst.Import, cst.ImportFrom)) for n in stmt.body
            ):
                insert_import_idx = i + 1

        missing_typing = []
        if needs_any and not has_any_import:
            missing_typing.append("Any")
        if needs_annotated and not has_annotated_import:
            missing_typing.append("Annotated")

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
            insert_import_idx += 1

        if needs_stringconfig and not has_stringconstraints_import:
            pydantic_import = cst.SimpleStatementLine(
                body=[
                    cst.ImportFrom(
                        module=cst.Name(value="pydantic"),
                        names=[cst.ImportAlias(name=cst.Name(value="StringConstraints"))],
                    )
                ]
            )
            new_body.insert(insert_import_idx, pydantic_import)
            insert_import_idx += 1

        for imp_str in self.required_imports:
            try:
                parsed_stmt = cst.parse_statement(imp_str)
                new_body.insert(insert_import_idx, parsed_stmt)
                insert_import_idx += 1
            except cst.ParserSyntaxError:
                pass

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
