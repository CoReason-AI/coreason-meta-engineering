# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import sys
from pathlib import Path

import pytest

from coreason_meta_engineering.utils.topological_validation import validate_generated_topology


def test_validate_generated_topology_success(tmp_path: Path) -> None:
    f = tmp_path / "valid.py"
    f.write_text("from pydantic import BaseModel\nclass MyClass(BaseModel):\n    name: str\n")
    expected = {
        "properties": {"name": {"title": "Name", "type": "string"}},
        "required": ["name"],
        "title": "MyClass",
        "type": "object",
    }
    assert validate_generated_topology(str(f), "MyClass", expected) is True
    assert "generated_module" not in sys.modules


def test_validate_generated_topology_mismatch(tmp_path: Path) -> None:
    f = tmp_path / "valid.py"
    f.write_text("from pydantic import BaseModel\nclass MyClass(BaseModel):\n    age: int\n")
    expected = {
        "properties": {"name": {"title": "Name", "type": "string"}},
        "required": ["name"],
        "title": "MyClass",
        "type": "object",
    }
    assert validate_generated_topology(str(f), "MyClass", expected) is False


def test_validate_generated_topology_not_basemodel(tmp_path: Path) -> None:
    f = tmp_path / "valid.py"
    f.write_text("class MyClass:\n    pass\n")
    assert validate_generated_topology(str(f), "MyClass", {}) is False


def test_validate_generated_topology_syntax_error(tmp_path: Path) -> None:
    f = tmp_path / "valid.py"
    f.write_text("class MyClass:\n    pass\n    invalid syntax!!!")
    assert validate_generated_topology(str(f), "MyClass", {}) is False


def test_validate_generated_topology_missing_class(tmp_path: Path) -> None:
    f = tmp_path / "valid.py"
    f.write_text("class OtherClass:\n    pass\n")
    assert validate_generated_topology(str(f), "MyClass", {}) is False


def test_validate_generated_topology_invalid_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.util
    from typing import Any

    def mock_spec(*_args: Any, **_kwargs: Any) -> Any:
        return None

    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec)
    f = tmp_path / "valid.py"
    f.touch()
    assert validate_generated_topology(str(f), "MyClass", {}) is False


def test_validate_generated_topology_invalid_loader(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.util
    from typing import Any

    def mock_spec(*_args: Any, **_kwargs: Any) -> Any:
        class MockSpec:
            loader = None

        return MockSpec()

    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec)
    f = tmp_path / "valid.py"
    f.touch()
    assert validate_generated_topology(str(f), "MyClass", {}) is False
