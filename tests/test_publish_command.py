# Copyright (c) 2026 CoReason, Inc.
import pytest
from typer.testing import CliRunner
from pathlib import Path
import json
import yaml
from unittest.mock import patch, AsyncMock
from coreason_meta_engineering.main import app

runner = CliRunner()

def test_publish_command_success(tmp_path, monkeypatch):
    capability_dir = tmp_path / "assets" / "solver" / "test_v1"
    capability_dir.mkdir(parents=True)
    
    manifest_path = capability_dir / "manifest.yaml"
    manifest_data = {
        "urn": "urn:coreason:actionspace:solver:test:v1",
        "license_hash": "LIC-123"
    }
    manifest_path.write_text(yaml.dump(manifest_data))
    
    server_path = capability_dir / "server.py"
    server_path.write_text('"""\nAGENT INSTRUCTION: test\nCAUSAL AFFORDANCE: test\nEPISTEMIC BOUNDS: test\nMCP ROUTING TRIGGERS: urn:test\n"""\nimport os\n')
    
    monkeypatch.setattr("coreason_meta_engineering.main.evaluate_congruence", lambda m, s: {"composite_congruence": 0.99, "reasoning": "Good"})
    monkeypatch.setattr("coreason_meta_engineering.main.generate_multi_well_embeddings", lambda d: {"instruction": [0.1]*384})
    
    # Coverage for lines 231-232: registry exists but invalid json
    # Correct path: manifest_file.parents[2] / "registry" / "compiled_matrix.json"
    registry_dir = manifest_path.parents[2] / "registry"
    registry_dir.mkdir(parents=True)
    registry_file = registry_dir / "compiled_matrix.json"
    registry_file.write_text("invalid json")
    
    with patch("coreason_meta_engineering.main.execute_guillotine_scan", new_callable=AsyncMock) as mock_scan:
        mock_scan.return_value = True
        result = runner.invoke(app, ["publish", str(manifest_path)])
        assert result.exit_code == 0

def test_publish_command_semantic_fail(tmp_path, monkeypatch):
    capability_dir = tmp_path / "assets" / "solver" / "test_v1"
    capability_dir.mkdir(parents=True)
    manifest_path = capability_dir / "manifest.yaml"
    manifest_path.write_text("urn: urn:coreason:actionspace:solver:test:v1")
    server_path = capability_dir / "server.py"
    server_path.write_text('"""\nAGENT INSTRUCTION: test\nCAUSAL AFFORDANCE: test\nEPISTEMIC BOUNDS: test\nMCP ROUTING TRIGGERS: urn:test\n"""\n')

    from coreason_meta_engineering.utils.topological_validation import SemanticAmbiguityError
    def mock_ambiguity(e, r): raise SemanticAmbiguityError("Ambiguous")
    monkeypatch.setattr("coreason_meta_engineering.main.check_semantic_ambiguity", mock_ambiguity)
    monkeypatch.setattr("coreason_meta_engineering.main.generate_multi_well_embeddings", lambda d: {})

    result = runner.invoke(app, ["publish", str(manifest_path)])
    assert result.exit_code != 0 or "Publish blocked by Semantic Ambiguity" in result.stderr or "Publish blocked by Semantic Ambiguity" in result.stdout

def test_publish_command_scan_fail(tmp_path, monkeypatch):
    capability_dir = tmp_path / "assets" / "solver" / "test_v1"
    capability_dir.mkdir(parents=True)
    manifest_path = capability_dir / "manifest.yaml"
    manifest_path.write_text("urn: urn:coreason:actionspace:solver:test:v1")
    server_path = capability_dir / "server.py"
    server_path.write_text('"""\nAGENT INSTRUCTION: test\nCAUSAL AFFORDANCE: test\nEPISTEMIC BOUNDS: test\nMCP ROUTING TRIGGERS: urn:test\n"""\n')

    from coreason_meta_engineering.utils.kinetic_guillotine import KineticGuillotineError
    with patch("coreason_meta_engineering.main.execute_guillotine_scan", new_callable=AsyncMock) as mock_scan:
        mock_scan.side_effect = KineticGuillotineError("Scan failed")
        result = runner.invoke(app, ["publish", str(manifest_path)])
        assert result.exit_code != 0 or "Publish blocked by DLP Compliance Engine" in result.stderr or "Publish blocked by DLP Compliance Engine" in result.stdout

def test_publish_command_congruence_fail(tmp_path, monkeypatch):
    capability_dir = tmp_path / "assets" / "solver" / "test_v1"
    capability_dir.mkdir(parents=True)
    manifest_path = capability_dir / "manifest.yaml"
    manifest_path.write_text("urn: urn:coreason:actionspace:solver:test:v1")
    server_path = capability_dir / "server.py"
    server_path.write_text('"""\nAGENT INSTRUCTION: test\nCAUSAL AFFORDANCE: test\nEPISTEMIC BOUNDS: test\nMCP ROUTING TRIGGERS: urn:test\n"""\n')

    with patch("coreason_meta_engineering.main.execute_guillotine_scan", new_callable=AsyncMock) as mock_scan:
        mock_scan.return_value = True
        from coreason_meta_engineering.utils.congruence_judge import CongruenceFaultError
        def mock_eval(m, s): raise CongruenceFaultError("Score too low")
        monkeypatch.setattr("coreason_meta_engineering.main.evaluate_congruence", mock_eval)
        
        result = runner.invoke(app, ["publish", str(manifest_path)])
        assert result.exit_code != 0 or "Publish blocked by Congruence Judge" in result.stderr or "Publish blocked by Congruence Judge" in result.stdout

def test_publish_command_not_found():
    result = runner.invoke(app, ["publish", "nonexistent.yaml"])
    assert result.exit_code == 1

def test_publish_command_invalid_yaml(tmp_path):
    manifest = tmp_path / "bad.yaml"
    manifest.write_text(":")
    result = runner.invoke(app, ["publish", str(manifest)])
    assert result.exit_code == 1

def test_publish_command_no_server_py(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("urn: test")
    result = runner.invoke(app, ["publish", str(manifest)])
    assert result.exit_code == 1
