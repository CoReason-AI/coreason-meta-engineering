import pytest
from coreason_meta_engineering.forge_orchestrator import DynamicForgeOrchestrator, dispatch_agent_generation
from coreason_manifest.spec import CognitiveDeliberativeEnvelopeState
from coreason_meta_engineering.pvv import _compare_schema, _native_validation

@pytest.mark.asyncio
async def test_dispatch_agent_generation_fallback():
    with pytest.raises(NotImplementedError):
        await dispatch_agent_generation("unmatched_prompt_string")

@pytest.mark.asyncio
async def test_scaffold_ast_all_agents_fail(tmp_path):
    target_file = tmp_path / "target.py"
    # Will trigger NotImplementedError -> result is Exception -> hits lines 91-92
    # Since all agents fail, it will hit line 117
    with pytest.raises(RuntimeError, match="SystemFaultEvent: KineticGuillotineViolation"):
        await DynamicForgeOrchestrator.scaffold_ast(
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:test:v1",
            geometric_schema={},
            complexity_score=1,
            prompt_template="unmatched_prompt_string"
        )

@pytest.mark.asyncio
async def test_scaffold_ast_pvv_rejection(tmp_path):
    target_file = tmp_path / "target.py"
    # Will match "actionspace:solver" and return TestModelClass which doesn't have missing_prop
    # This will trigger PVV validation error and then line 113-114
    with pytest.raises(RuntimeError, match="SystemFaultEvent: KineticGuillotineViolation"):
        await DynamicForgeOrchestrator.scaffold_ast(
            target_file_path=str(target_file),
            action_space_id="urn:coreason:actionspace:solver:test:v1",
            geometric_schema={"properties": {"missing_prop": {}}},
            complexity_score=1,
            prompt_template="actionspace:solver"
        )

def test_compare_schema_no_models_dict():
    class DummyModule:
        pass
    with pytest.raises(ValueError, match="No Pydantic models found"):
        _compare_schema(DummyModule(), {"properties": {}})

def test_compare_schema_no_models_list():
    class DummyModule:
        pass
    _compare_schema(DummyModule(), [])

def test_compare_schema_missing_property():
    from pydantic import BaseModel
    class MyModel(BaseModel):
        name: str

    class DummyModule:
        pass
    setattr(DummyModule, "MyModel", MyModel)
    
    with pytest.raises(ValueError, match="Schema mismatch: missing property 'age'"):
        _compare_schema(DummyModule, {"properties": {"name": {}, "age": {}}})

def test_native_validation_spec_none(monkeypatch):
    import importlib.util
    def mock_spec(*args, **kwargs):
        return None
    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec)
    
    with pytest.raises(RuntimeError, match="Failed to create module spec."):
        _native_validation("x = 1", {})
