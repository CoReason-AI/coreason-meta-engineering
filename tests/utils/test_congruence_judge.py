# Copyright (c) 2026 CoReason, Inc.
from typing import Any

import pytest

from coreason_meta_engineering.utils.congruence_judge import (
    CongruenceFaultError,
    evaluate_congruence,
)


def test_evaluate_congruence_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock environment to ensure fallback is hit or LLM returns quickly
    monkeypatch.setenv("COREASON_LLM_API_URL", "http://invalid-url.local/api/generate")

    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}

    # Because of fallback, it will return a perfect score instead of crashing
    res = evaluate_congruence(manifest, ast_skeleton)
    assert res["composite_congruence"] == 1.0


def test_evaluate_congruence_faults(monkeypatch: pytest.MonkeyPatch) -> None:
    # Test that the fault error is raised if scores are too low
    import json
    import urllib.request

    class MockResponse:
        def read(self) -> bytes:
            return json.dumps(
                {
                    "response": json.dumps(
                        {
                            "instruction_score": 0.5,  # Below 0.70
                            "composite_congruence": 0.80,  # Below 0.85
                            "reasoning": "Poor match",
                        }
                    )
                }
            ).encode()

        def __enter__(self) -> "MockResponse":
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

    def mock_urlopen(_req: Any, _timeout: float = 15.0) -> MockResponse:
        return MockResponse()

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}

    with pytest.raises(CongruenceFaultError, match="Congruence Fault"):
        evaluate_congruence(manifest, ast_skeleton)


def test_evaluate_congruence_individual_fault(monkeypatch: pytest.MonkeyPatch) -> None:
    import json
    import urllib.request

    class MockResponse:
        def read(self) -> bytes:
            return json.dumps(
                {
                    "response": json.dumps(
                        {
                            "instruction_score": 0.5,
                            "composite_congruence": 0.95,  # Passes line 73
                            "reasoning": "Instruction mismatch",
                        }
                    )
                }
            ).encode()

        def __enter__(self) -> "MockResponse":
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

    def mock_urlopen(_req: Any, _timeout: float = 15.0) -> MockResponse:
        return MockResponse()

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}

    with pytest.raises(CongruenceFaultError, match="instruction_score"):
        evaluate_congruence(manifest, ast_skeleton)
