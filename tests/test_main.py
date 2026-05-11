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
            "urn:coreason:actionspace:solver:test:v1",
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
            "urn:coreason:actionspace:solver:test:v1",
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
                "urn:coreason:actionspace:solver:test:v1",
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
    assert "actionspace" in result.output


def test_scaffold_actuator_cli(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = (
        '{"properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "is_active": {"type": "boolean"}}}'
    )
    result = runner.invoke(
        app,
        [
            "scaffold-logic-actuator",
            "MyActuator",
            schema_payload,
            "--target-file",
            str(target_file),
            "--action-space-id",
            "urn:coreason:actionspace:solver:my_actuator:v1",
        ],
    )
    assert result.exit_code == 0
    assert "Successfully injected MyActuator" in result.output
    content = target_file.read_text()
    assert "def MyActuator" in content


def test_scaffold_actuator_cli_invalid_urn(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_payload = '{"properties": {"name": {"type": "string"}}}'
    result = runner.invoke(
        app,
        [
            "scaffold-logic-actuator",
            "MyActuator",
            schema_payload,
            "--target-file",
            str(target_file),
            "--action-space-id",
            "invalid",
        ],
    )
    assert result.exit_code != 0
    assert "Invalid URN" in result.output


def test_scaffold_actuator_cli_fallback(tmp_path: Path) -> None:
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
                "MyActuator",
                schema_payload,
                "--target-file",
                str(target_file),
                "--action-space-id",
                "urn:coreason:actionspace:solver:test:v1",
            ],
        )
        assert result.exit_code == 0


def test_scaffold_actuator_cli_file(tmp_path: Path) -> None:
    target_file = tmp_path / "dummy.py"
    target_file.write_text("def x(): pass\n")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"properties": {"name": {"type": "string"}}}')
    result = runner.invoke(
        app,
        [
            "scaffold-logic-actuator",
            "MyActuator",
            str(schema_file),
            "--target-file",
            str(target_file),
            "--action-space-id",
            "urn:coreason:actionspace:solver:my_actuator:v1",
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
            "urn:coreason:actionspace:node:my_agent:v1",
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


def test_enforce_cryptographic_license_commercial(tmp_path, monkeypatch):

    from coreason_meta_engineering.main import enforce_cryptographic_license

    target = tmp_path / "server.py"
    target.write_text("print('test')")

    monkeypatch.setenv("COREASON_COMMERCIAL_OWNER", "CoReason")
    monkeypatch.setenv("COREASON_LICENSE_HASH", "LIC-123")
    monkeypatch.setenv("COREASON_URN_AUTHORITY_URL", "http://localhost:8080")
    monkeypatch.setenv("COREASON_PUBLIC_KEY", "PUB-123")

    import httpx

    class MockResp:
        status_code = 200

        def json(self):
            return {"authorized": True}

    def mock_post(*_args, **_kwargs):
        return MockResp()

    monkeypatch.setattr(httpx, "post", mock_post)

    manifest_data = {"license_hash": "LIC-123", "commercial_owner": "CoReason"}

    enforce_cryptographic_license(target, "urn:coreason:actionspace:oracle:test:v1", manifest_data)
    assert "Copyright (c) 2026 CoReason" in target.read_text()
    assert "LIC-123" in target.read_text()


def test_enforce_cryptographic_license_unauthorized(tmp_path, monkeypatch):
    import httpx
    import pytest

    from coreason_meta_engineering.main import enforce_cryptographic_license

    target = tmp_path / "server.py"
    target.write_text("print('test')")

    monkeypatch.setenv("COREASON_URN_AUTHORITY_URL", "http://localhost:8080")

    class MockResp:
        status_code = 200

        def json(self):
            return {"authorized": False}

    monkeypatch.setattr(httpx, "post", lambda *_args, **_kwargs: MockResp())

    with pytest.raises(SystemExit) as excinfo:
        enforce_cryptographic_license(target, "urn:test", {"license_hash": "BAD"})
    assert excinfo.value.code == 1


def test_enforce_cryptographic_license_error(tmp_path, monkeypatch):
    import httpx
    import pytest

    from coreason_meta_engineering.main import enforce_cryptographic_license

    target = tmp_path / "server.py"
    target.write_text("print('test')")

    monkeypatch.setattr(httpx, "post", Exception("Network error"))

    with pytest.raises(SystemExit) as excinfo:
        enforce_cryptographic_license(target, "urn:test", {"license_hash": "BAD"})
    assert excinfo.value.code == 1
