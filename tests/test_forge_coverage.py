from pathlib import Path

import pytest

from coreason_meta_engineering.forge_orchestrator import DynamicForgeOrchestrator, dispatch_agent_generation
from coreason_meta_engineering.pvv import _compare_schema, _native_validation


@pytest.mark.asyncio
async def test_dispatch_agent_generation_fallback() -> None:
    with pytest.raises(NotImplementedError):
        await dispatch_agent_generation("unmatched_prompt_string")


@pytest.mark.asyncio
async def test_scaffold_ast_all_agents_fail(tmp_path: Path) -> None:
    target_file = tmp_path / "target.py"
    # Will trigger NotImplementedError -> result is Exception -> hits lines 91-92
    # Since all agents fail, it will hit line 117
    with pytest.raises(RuntimeError, match="SystemFaultEvent: KineticGuillotineViolation"):
        await DynamicForgeOrchestrator.scaffold_ast(
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:test:v1",
            geometric_schema={},
            complexity_score=1,
            prompt_template="unmatched_prompt_string",
        )


@pytest.mark.asyncio
async def test_scaffold_ast_pvv_rejection(tmp_path: Path) -> None:
    target_file = tmp_path / "target.py"
    # Will match "actionspace:solver" and return TestModelClass which doesn't have missing_prop
    # This will trigger PVV validation error and then line 113-114
    with pytest.raises(RuntimeError, match="SystemFaultEvent: KineticGuillotineViolation"):
        await DynamicForgeOrchestrator.scaffold_ast(
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:solver:test:v1",
            geometric_schema={"properties": {"missing_prop": {}}},
            complexity_score=1,
            prompt_template="actionspace:solver",
        )


def test_compare_schema_no_models_dict() -> None:
    class DummyModule:
        pass

    with pytest.raises(ValueError, match="No Pydantic models found"):
        _compare_schema(DummyModule(), {"properties": {}})


def test_compare_schema_no_models_list() -> None:
    class DummyModule:
        pass

    _compare_schema(DummyModule(), [])


def test_compare_schema_missing_property() -> None:
    from pydantic import BaseModel

    class MyModel(BaseModel):
        name: str

    class DummyModule:
        pass

    setattr(DummyModule, "MyModel", MyModel)  # noqa: B010

    with pytest.raises(ValueError, match="Schema mismatch: missing property 'age'"):
        _compare_schema(DummyModule, {"properties": {"name": {}, "age": {}}})


def test_native_validation_spec_none(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.util
    from typing import Any

    def mock_spec(*_args: Any, **_kwargs: Any) -> Any:
        return None

    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec)

    with pytest.raises(RuntimeError, match=r"Failed to create module spec\."):
        _native_validation("x = 1", {})


@pytest.mark.asyncio
async def test_scaffold_ast_success_with_license(tmp_path: Path) -> None:
    import os

    from coreason_meta_engineering.forge_orchestrator import DynamicForgeOrchestrator

    target_file = tmp_path / "target_success.py"
    os.environ["AST_GUILLOTINE_ACTIVE"] = "True"

    # Use a prompt that hits a known fallback in dispatch_agent_generation
    # e.g., "actionspace:node:test" -> GeneratedClass
    code = await DynamicForgeOrchestrator.scaffold_ast(
        target_file_path=str(target_file),
        action_space_id="urn:coreason:actionspace:node:test:v1",
        geometric_schema={"properties": {}},
        complexity_score=1,
        prompt_template="actionspace:node:test",
    )

    assert "# Copyright (c) 2026 CoReason, Inc" in code
    assert "class GeneratedClass" in code
    assert target_file.exists()
    assert "# Copyright (c) 2026 CoReason, Inc" in target_file.read_text()


@pytest.mark.asyncio
async def test_scaffold_ast_target_dir_error(tmp_path: Path) -> None:
    from coreason_meta_engineering.forge_orchestrator import DynamicForgeOrchestrator

    target_dir = tmp_path / "a_directory"
    target_dir.mkdir()

    with pytest.raises(ValueError, match="is a directory, not a file"):
        await DynamicForgeOrchestrator.scaffold_ast(
            target_file_path=str(target_dir),
            action_space_id="urn:coreason:actionspace:node:test:v1",
            geometric_schema={"properties": {}},
            complexity_score=1,
            prompt_template="actionspace:node:test",
        )


@pytest.mark.asyncio
async def test_scaffold_ast_workspace_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from coreason_meta_engineering.forge_orchestrator import DynamicForgeOrchestrator

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target_rel_path = "subdir/target.py"

    monkeypatch.setenv("COREASON_WORKSPACE_ROOT", str(workspace))

    await DynamicForgeOrchestrator.scaffold_ast(
        target_file_path=target_rel_path,
        action_space_id="urn:coreason:actionspace:node:test:v1",
        geometric_schema={"properties": {}},
        complexity_score=1,
        prompt_template="actionspace:node:test",
    )

    expected_file = workspace / "subdir" / "target.py"
    assert expected_file.exists()
    assert "class GeneratedClass" in expected_file.read_text()
