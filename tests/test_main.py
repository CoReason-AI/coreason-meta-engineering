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

from typer.testing import CliRunner

from coreason_meta_engineering.main import app

runner = CliRunner()


def test_scaffold_model_cli(tmp_path: Path) -> None:
    # 1. Create dummy file
    target_file = tmp_path / "dummy.py"
    target_file.write_text("import pydantic\n", encoding="utf-8")

    # 2. Schema payload
    schema = {
        "properties": {
            "name": {"type": "string", "description": "Person's name"},
            "age": {"type": "integer"},
            "optional_field": {"type": "string"},
        },
        "required": ["name", "age"],
    }
    schema_payload = json.dumps(schema)

    # 3. Invoke CLI
    result = runner.invoke(
        app,
        [
            "scaffold-manifest-state",
            "Person",
            schema_payload,
            "--target-file",
            str(target_file),
            "--action-space-id",
            "urn:coreason:actionspace:test:v1",
        ],
    )

    # 4. Assert exit code
    assert result.exit_code == 0, result.stdout
    assert "Successfully injected Person into" in result.stdout

    # 5. Assert file modifications
    new_content = target_file.read_text(encoding="utf-8")
    assert "class Person(CoreasonBaseState):" in new_content
    assert "Person.model_rebuild()" in new_content
    assert "name: Annotated[str, StringConstraints(max_length=2000)]" in new_content
    assert "age: int" in new_content

    # Assert optional field logic separately to avoid E501
    assert "optional_field: Annotated[str, StringConstraints(max_length=2000)] | None" in new_content
    assert 'Field(default=None, description="")' in new_content


def test_scaffold_model_cli_file_payload(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy_file.py"
    target_file.write_text("import pydantic\n", encoding="utf-8")

    schema = {
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "scaffold-manifest-state",
            "PersonFile",
            str(schema_file),
            "--target-file",
            str(target_file),
            "--action-space-id",
            "urn:coreason:actionspace:test:v1",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "Successfully injected PersonFile into" in result.stdout

    new_content = target_file.read_text(encoding="utf-8")
    assert "class PersonFile(CoreasonBaseState):" in new_content


def test_scaffold_model_cli_invalid_file_fallback(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy_file.py"
    target_file.write_text("import pydantic\n", encoding="utf-8")

    # Use a schema payload that triggers OSError but is still a valid json string
    # To test actual fallback code block and hit OSError
    from unittest.mock import patch

    schema_payload_fallback_clean = '{"properties": {"name": {"type": "string"}}}'

    with patch("src.coreason_meta_engineering.main.Path.is_file") as mock_is_file:
        mock_is_file.side_effect = OSError("Mocked OS Error")
        result3 = runner.invoke(
            app,
            [
                "scaffold-manifest-state",
                "PersonFallbackClean",
                schema_payload_fallback_clean,
                "--target-file",
                str(target_file),
                "--action-space-id",
                "urn:coreason:actionspace:test:v1",
            ],
        )
        assert result3.exit_code == 0


def test_scaffold_model_cli_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("import pydantic\n", encoding="utf-8")

    schema_payload = '{"properties": {"name": {"type": "string"}}, "required": ["name"]}'

    result = runner.invoke(
        app,
        [
            "scaffold-manifest-state",
            "BadModel",
            schema_payload,
            "--target-file",
            str(target_file),
            "--action-space-id",
            "finance_ledger_v1",
        ],
    )

    assert result.exit_code != 0
    assert "urn:coreason:actionspace:" in result.output


def test_scaffold_mcp_tool_cli(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = (
        '{"properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "is_active": {"type": "boolean"}}}'
    )
    result = runner.invoke(
        app,
        [
            "scaffold-logic-actuator",
            "MyTool",
            schema_payload,
            "--target-file",
            str(target_file),
            "--action-space-id",
            "urn:coreason:actionspace:my_tool:v1",
        ],
    )
    assert result.exit_code == 0
    assert "Successfully injected MyTool" in result.output
    content = target_file.read_text()
    assert "def MyTool" in content


def test_scaffold_mcp_tool_cli_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = '{"properties": {"name": {"type": "string"}}}'
    result = runner.invoke(
        app,
        [
            "scaffold-logic-actuator",
            "MyTool",
            schema_payload,
            "--target-file",
            str(target_file),
            "--action-space-id",
            "invalid",
        ],
    )
    assert result.exit_code != 0
    assert "Invalid URN" in result.output


def test_scaffold_mcp_tool_cli_fallback(tmp_path: Path) -> None:
    from unittest.mock import patch

    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = '{"properties": {"name": {"type": "string"}}}'
    with patch("src.coreason_meta_engineering.main.Path.is_file") as mock_is_file:
        mock_is_file.side_effect = OSError("Mocked")
        result = runner.invoke(
            app,
            [
                "scaffold-logic-actuator",
                "MyTool",
                schema_payload,
                "--target-file",
                str(target_file),
                "--action-space-id",
                "urn:coreason:actionspace:v1",
            ],
        )
        assert result.exit_code == 0


def test_scaffold_mcp_tool_cli_file(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"properties": {"name": {"type": "string"}}}')
    result = runner.invoke(
        app,
        [
            "scaffold-logic-actuator",
            "MyTool",
            str(schema_file),
            "--target-file",
            str(target_file),
            "--action-space-id",
            "urn:coreason:actionspace:my_tool:v1",
        ],
    )
    assert result.exit_code == 0


def test_scaffold_agent_node_cli(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("class BaseAgent: pass\n")
    result = runner.invoke(
        app,
        [
            "scaffold-epistemic-node",
            "MyAgent",
            "role",
            "--target-file",
            str(target_file),
            "--action-space-id",
            "urn:coreason:actionspace:my_agent:v1",
        ],
    )
    assert result.exit_code == 0
    assert "Successfully injected MyAgent" in result.output
    content = target_file.read_text()
    assert "class MyAgent" in content


def test_scaffold_agent_node_cli_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("class BaseAgent: pass\n")
    result = runner.invoke(
        app,
        [
            "scaffold-epistemic-node",
            "MyAgent",
            "role",
            "--target-file",
            str(target_file),
            "--action-space-id",
            "invalid",
        ],
    )
    assert result.exit_code != 0
    assert "Invalid URN" in result.output
