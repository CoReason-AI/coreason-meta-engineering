import sys
from pydantic import BaseModel
import pytest
from coreason_meta_engineering.utils.topological_validation import validate_generated_topology

def test_validate_generated_topology_success(tmp_path):
    f = tmp_path / "valid.py"
    f.write_text("from pydantic import BaseModel\nclass MyClass(BaseModel):\n    name: str\n")
    expected = {"properties": {"name": {"title": "Name", "type": "string"}}, "required": ["name"], "title": "MyClass", "type": "object"}
    assert validate_generated_topology(str(f), "MyClass", expected) is True
    assert "generated_module" not in sys.modules

def test_validate_generated_topology_mismatch(tmp_path):
    f = tmp_path / "valid.py"
    f.write_text("from pydantic import BaseModel\nclass MyClass(BaseModel):\n    age: int\n")
    expected = {"properties": {"name": {"title": "Name", "type": "string"}}, "required": ["name"], "title": "MyClass", "type": "object"}
    assert validate_generated_topology(str(f), "MyClass", expected) is False

def test_validate_generated_topology_not_basemodel(tmp_path):
    f = tmp_path / "valid.py"
    f.write_text("class MyClass:\n    pass\n")
    assert validate_generated_topology(str(f), "MyClass", {}) is False

def test_validate_generated_topology_syntax_error(tmp_path):
    f = tmp_path / "valid.py"
    f.write_text("class MyClass:\n    pass\n    invalid syntax!!!")
    assert validate_generated_topology(str(f), "MyClass", {}) is False

def test_validate_generated_topology_missing_class(tmp_path):
    f = tmp_path / "valid.py"
    f.write_text("class OtherClass:\n    pass\n")
    assert validate_generated_topology(str(f), "MyClass", {}) is False

def test_validate_generated_topology_invalid_spec(tmp_path, monkeypatch):
    import importlib.util
    def mock_spec(*args, **kwargs):
        return None
    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec)
    f = tmp_path / "valid.py"
    f.touch()
    assert validate_generated_topology(str(f), "MyClass", {}) is False

def test_validate_generated_topology_invalid_loader(tmp_path, monkeypatch):
    import importlib.util
    def mock_spec(*args, **kwargs):
        class MockSpec:
            loader = None
        return MockSpec()
    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec)
    f = tmp_path / "valid.py"
    f.touch()
    assert validate_generated_topology(str(f), "MyClass", {}) is False
