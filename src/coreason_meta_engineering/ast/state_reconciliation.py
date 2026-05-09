# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

import typing

import libcst as cst

from coreason_meta_engineering.ast.state_scaffold import StateInjectionFunctor


class StateReconciliationFunctor(StateInjectionFunctor):  # type: ignore[misc]
    """
    A libcst transformer that updates an existing Pydantic state class by replacing its fields
    with a new geometric schema, while preserving the docstring and __action_space_urn__.
    """

    def __init__(
        self,
        state_name: str,
        geometric_schema: list[dict[str, typing.Any]],
        action_space_id: str,
        base_class: str = "CoreasonBaseState",
    ):
        super().__init__(
            state_name=state_name,
            geometric_schema=geometric_schema,
            action_space_id=action_space_id,
            base_class=base_class,
        )
        self.class_found = False

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:  # noqa: N802
        if updated_node.name.value == self.state_name:
            self.class_found = True
            docstring_node = None
            urn_node = None

            for stmt in original_node.body.body:
                if isinstance(stmt, cst.SimpleStatementLine):
                    for node in stmt.body:
                        if isinstance(node, cst.Expr) and isinstance(node.value, cst.SimpleString):
                            if not docstring_node:
                                docstring_node = stmt
                        elif (
                            isinstance(node, cst.Assign)
                            and len(node.targets) == 1
                            and isinstance(node.targets[0].target, cst.Name)
                            and node.targets[0].target.value == "__action_space_urn__"
                        ):
                            urn_node = stmt

            new_body_elements: list[cst.BaseStatement] = []
            if docstring_node:
                new_body_elements.append(docstring_node)
            else:
                new_body_elements.append(self._build_docstring())

            if urn_node:
                new_body_elements.append(urn_node)
            else:
                new_body_elements.append(self._build_urn_attribute())

            list_fields = []
            for f in self.geometric_schema:
                new_body_elements.append(self._build_field(f))
                if "list[" in f["type"]:
                    list_fields.append(f["name"])

            if list_fields:
                new_body_elements.append(self._build_validator(list_fields))

            return updated_node.with_changes(body=cst.IndentedBlock(body=new_body_elements))
        return updated_node

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:  # noqa: N802, ARG002
        # Gather required imports based on schema fields
        needs_self = any("list[" in f["type"] for f in self.geometric_schema)
        needs_any = any("Any" in f["type"] for f in self.geometric_schema)
        needs_annotated = any("Annotated" in f["type"] for f in self.geometric_schema)
        needs_string_constraints = any("StringConstraints" in f["type"] for f in self.geometric_schema)

        has_self_import = False
        has_any_import = False
        has_annotated_import = False
        has_field_import = False
        has_model_validator_import = False
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
                                elif name_item.name.value == "Any":
                                    has_any_import = True
                                elif name_item.name.value == "Annotated":
                                    has_annotated_import = True
                            elif mod_name == "pydantic":
                                if name_item.name.value == "Field":
                                    has_field_import = True
                                elif name_item.name.value == "model_validator":
                                    has_model_validator_import = True
                                elif name_item.name.value == "StringConstraints":
                                    has_string_constraints_import = True

        new_body = list(updated_node.body)

        insert_import_idx = 0
        for i, stmt in enumerate(new_body):
            if isinstance(stmt, cst.SimpleStatementLine) and any(
                isinstance(n, (cst.Import, cst.ImportFrom)) for n in stmt.body
            ):
                insert_import_idx = i + 1

        typing_imports = []
        if needs_self and not has_self_import:
            typing_imports.append(cst.ImportAlias(name=cst.Name(value="Self")))
        if needs_any and not has_any_import:
            typing_imports.append(cst.ImportAlias(name=cst.Name(value="Any")))
        if needs_annotated and not has_annotated_import:
            typing_imports.append(cst.ImportAlias(name=cst.Name(value="Annotated")))

        if typing_imports:
            new_body.insert(
                insert_import_idx,
                cst.SimpleStatementLine(body=[cst.ImportFrom(module=cst.Name(value="typing"), names=typing_imports)]),
            )
            insert_import_idx += 1

        pydantic_imports = []
        if not has_field_import:
            pydantic_imports.append(cst.ImportAlias(name=cst.Name(value="Field")))
        if needs_self and not has_model_validator_import:
            pydantic_imports.append(cst.ImportAlias(name=cst.Name(value="model_validator")))
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

        # Only append new_class if the class was not found (fallback to scaffolding)
        if not self.class_found:
            new_class = self._build_class()
            new_rebuild = self._build_rebuild_call()
            new_body.append(new_class)
            new_body.append(new_rebuild)

        return updated_node.with_changes(body=new_body)
