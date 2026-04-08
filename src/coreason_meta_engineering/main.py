# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

import json
from pathlib import Path

import libcst as cst
import typer

from coreason_meta_engineering.ast.scaffold import ClassInjectTransformer
from coreason_meta_engineering.schema import resolve_json_schema_to_fields
from coreason_meta_engineering.utils.logger import logger

app = typer.Typer()


@app.command(name="scaffold-model")  # type: ignore[misc]
def scaffold_model(
    model_name: str,
    schema_payload: str,
    target_file: Path = typer.Option(..., exists=True, dir_okay=False, writable=True),  # noqa: B008
) -> None:
    """
    Scaffolds a new model by parsing JSON schema and injecting it into the target Python file.
    """
    logger.info(f"Scaffolding model {model_name} into {target_file}")

    # 1. Parse schema payload
    schema_dict = json.loads(schema_payload)

    # 2. Resolve fields
    fields = resolve_json_schema_to_fields(schema_dict)

    # 3. Read target file text
    source_code = target_file.read_text(encoding="utf-8")

    # 4. Parse AST and inject
    module = cst.parse_module(source_code)
    transformer = ClassInjectTransformer(name=model_name, fields=fields)
    new_module = module.visit(transformer)

    # 5. Write modified code
    target_file.write_text(new_module.code, encoding="utf-8")

    # 6. Print success message
    typer.echo(f"Successfully injected {model_name} into {target_file}")


if __name__ == "__main__":  # pragma: no cover
    app()
