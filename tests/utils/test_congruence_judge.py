# Copyright (c) 2026 CoReason, Inc.
import pytest
from coreason_meta_engineering.utils.congruence_judge import evaluate_congruence, CongruenceFaultError

def test_evaluate_congruence_fallback(monkeypatch):
    # Mock environment to ensure fallback is hit or LLM returns quickly
    monkeypatch.setenv("COREASON_LLM_API_URL", "http://invalid-url.local/api/generate")
    
    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}
    
    # Because of fallback, it will return a perfect score instead of crashing
    res = evaluate_congruence(manifest, ast_skeleton)
    assert res["composite_congruence"] == 1.0

def test_evaluate_congruence_faults(monkeypatch):
    # Test that the fault error is raised if scores are too low
    import json
    import urllib.request
    
    class MockResponse:
        def read(self):
            return json.dumps({
                "response": json.dumps({
                    "instruction_score": 0.5, # Below 0.70
                    "composite_congruence": 0.80, # Below 0.85
                    "reasoning": "Poor match"
                })
            }).encode()
        
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_urlopen(req, timeout=15.0):
        return MockResponse()

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}
    
    with pytest.raises(CongruenceFaultError):
        evaluate_congruence(manifest, ast_skeleton)
