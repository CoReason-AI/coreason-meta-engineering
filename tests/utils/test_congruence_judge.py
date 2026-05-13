# Copyright (c) 2026 CoReason, Inc.
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from coreason_meta_engineering.utils.congruence_judge import (
    CongruenceFaultError,
    evaluate_congruence,
)


class MockLLMHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        content_length = int(self.headers["Content-Length"])
        _post_data = self.rfile.read(content_length)

        # Default success response
        response_data = {
            "response": json.dumps(
                {
                    "instruction_score": 0.95,
                    "composite_congruence": 0.95,
                    "reasoning": "Perfect match",
                }
            )
        }

        # Check for specific triggers in the path or just use global state
        if hasattr(self.server, "response_override"):
            response_data = self.server.response_override

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        # Silencing server logs
        pass


@pytest.fixture
def llm_server():
    server = HTTPServer(("localhost", 0), MockLLMHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield server
    server.shutdown()


def test_evaluate_congruence_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # Use a non-existent local port to trigger fallback
    monkeypatch.setenv("COREASON_LLM_API_URL", "http://localhost:1")

    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}

    # Because of fallback, it will return a perfect score instead of crashing
    res = evaluate_congruence(manifest, ast_skeleton)
    assert res["composite_congruence"] == 1.0


def test_evaluate_congruence_faults(llm_server: HTTPServer, monkeypatch: pytest.MonkeyPatch) -> None:
    # Test that the fault error is raised if scores are too low
    url = f"http://localhost:{llm_server.server_port}/api/generate"
    monkeypatch.setenv("COREASON_LLM_API_URL", url)

    llm_server.response_override = {
        "response": json.dumps(
            {
                "instruction_score": 0.5,  # Below 0.70
                "composite_congruence": 0.80,  # Below 0.85
                "reasoning": "Poor match",
            }
        )
    }

    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}

    with pytest.raises(CongruenceFaultError, match="Congruence Fault"):
        evaluate_congruence(manifest, ast_skeleton)


def test_evaluate_congruence_individual_fault(
    llm_server: HTTPServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"http://localhost:{llm_server.server_port}/api/generate"
    monkeypatch.setenv("COREASON_LLM_API_URL", url)

    llm_server.response_override = {
        "response": json.dumps(
            {
                "instruction_score": 0.5,
                "composite_congruence": 0.95,  # Passes composite
                "reasoning": "Instruction mismatch",
            }
        )
    }

    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}

    with pytest.raises(CongruenceFaultError, match="instruction_score"):
        evaluate_congruence(manifest, ast_skeleton)


def test_evaluate_congruence_invalid_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COREASON_LLM_API_URL", "ftp://invalid-url.local/api/generate")
    manifest = {"urn": "urn:test"}
    ast_skeleton = {"docstring": "test"}

    with pytest.raises(ValueError, match=r"Invalid URL scheme\. Only http/https are allowed\."):
        evaluate_congruence(manifest, ast_skeleton)
