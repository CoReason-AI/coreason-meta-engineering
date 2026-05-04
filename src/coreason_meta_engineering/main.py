# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import json
import typing
from pathlib import Path

import libcst as cst
import typer

from coreason_meta_engineering.ast.actuator_scaffold import LogicInjectionFunctor
from coreason_meta_engineering.ast.node_scaffold import EpistemicNodeInjectionFunctor
from coreason_meta_engineering.ast.state_scaffold import StateInjectionFunctor
from coreason_meta_engineering.schema import resolve_epistemic_schema_to_ast_bindings
from coreason_meta_engineering.utils.logger import logger
from coreason_meta_engineering.utils.topological_validation import verify_cryptographic_urn_boundary

app = typer.Typer()


def parse_geometric_schema(val: str) -> dict[str, typing.Any]:
    try:
        path = Path(val)
        if path.is_file():
            return typing.cast("dict[str, typing.Any]", json.loads(path.read_text(encoding="utf-8")))
    except OSError:
        pass
    return typing.cast("dict[str, typing.Any]", json.loads(val))


@app.command(name="scaffold-manifest-state")  # type: ignore[misc]
def scaffold_manifest_state(
    state_name: str,
    geometric_schema: typing.Annotated[dict[str, typing.Any], typer.Argument(parser=parse_geometric_schema)],
    target_file: Path = typer.Option(..., exists=True, dir_okay=False, writable=True),  # noqa: B008
    action_space_id: str = typer.Option(..., help="The globally unique URN for this capability"),
    base_class: str = typer.Option("CoreasonBaseState", help="The base class to inherit from"),
) -> None:
    """
    Scaffolds a new model by parsing JSON schema and injecting it into the target Python file.
    """
    logger.info(f"Fabricating passive data state {state_name} into {target_file}")
    try:
        verify_cryptographic_urn_boundary(action_space_id)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    # 2. Resolve fields
    fields = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    # 3. Read target file text
    source_code = target_file.read_text(encoding="utf-8")

    # 4. Parse AST and inject
    module = cst.parse_module(source_code)
    transformer = StateInjectionFunctor(
        state_name=state_name, geometric_schema=fields, action_space_id=action_space_id, base_class=base_class
    )
    new_module = module.visit(transformer)

    # 5. Write modified code
    target_file.write_text(new_module.code, encoding="utf-8")

    # 6. Print success message
    typer.echo(f"Successfully injected {state_name} into {target_file}")


@app.command(name="scaffold-logic-actuator")  # type: ignore[misc]
def scaffold_logic_actuator(
    actuator_name: str,
    geometric_schema: typing.Annotated[dict[str, typing.Any], typer.Argument(parser=parse_geometric_schema)],
    target_file: Path = typer.Option(..., exists=True, dir_okay=False, writable=True),  # noqa: B008
    action_space_id: str = typer.Option(..., help="The globally unique URN for this actuator"),
    return_type: str = typer.Option("None", help="Return type of the function"),
) -> None:
    """
    Scaffolds a new logic actuator function by parsing JSON schema and injecting it into the target Python file.
    """
    logger.info(f"Fabricating active logic {actuator_name} into {target_file}")
    try:
        verify_cryptographic_urn_boundary(action_space_id)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    parameters = resolve_epistemic_schema_to_ast_bindings(geometric_schema)

    source_code = target_file.read_text(encoding="utf-8")
    module = cst.parse_module(source_code)
    transformer = LogicInjectionFunctor(
        actuator_name=actuator_name,
        geometric_schema=parameters,
        return_type=return_type,
        action_space_id=action_space_id,
    )
    new_module = module.visit(transformer)
    target_file.write_text(new_module.code, encoding="utf-8")

    typer.echo(f"Successfully injected {actuator_name} into {target_file}")


@app.command(name="scaffold-epistemic-node")  # type: ignore[misc]
def scaffold_epistemic_node(
    node_name: str,
    cognitive_boundary_directive: str,
    target_file: Path = typer.Option(..., exists=True, dir_okay=False, writable=True),  # noqa: B008
    action_space_id: str = typer.Option(..., help="The globally unique URN for this capability"),
    base_class: str = typer.Option("CoreasonBaseAgent", help="The base class to inherit from"),
) -> None:
    """
    Scaffolds a new Swarm Agent structure into the target Python file.
    """
    logger.info(f"Fabricating autonomous entity {node_name} into {target_file}")
    try:
        verify_cryptographic_urn_boundary(action_space_id)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    source_code = target_file.read_text(encoding="utf-8")
    module = cst.parse_module(source_code)
    transformer = EpistemicNodeInjectionFunctor(
        node_name=node_name,
        cognitive_boundary_directive=cognitive_boundary_directive,
        action_space_id=action_space_id,
        base_class=base_class,
    )
    new_module = module.visit(transformer)
    target_file.write_text(new_module.code, encoding="utf-8")

    typer.echo(f"Successfully injected {node_name} into {target_file}")


if __name__ == "__main__":  # pragma: no cover
    app()
