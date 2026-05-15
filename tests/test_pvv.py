# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

"""Tests for the PVV Pipeline (pvv.py)."""

import pytest
from coreason_manifest.spec import CognitiveDeliberativeEnvelopeState, OracleExecutionReceipt
from coreason_urn_authority.crypto.hasher import compute_canonical_hash

from coreason_meta_engineering.pvv import (
    _epistemic_strip,
    _generate_receipt,
    _native_validation,
    execute_pvv_pipeline,
)

# ═════════════════════════════════════════════════════════════════════════════
# Phase 1: Epistemic Strip
# ═════════════════════════════════════════════════════════════════════════════


class TestEpistemicStrip:
    """The Epistemic Strip must discard the deliberation_trace entirely."""

    def test_extracts_payload(self) -> None:
        envelope = CognitiveDeliberativeEnvelopeState[str](
            deliberation_trace="I am thinking very hard about this problem...",
            payload="x = 1\n",
        )
        result = _epistemic_strip(envelope)
        assert result == "x = 1\n"

    def test_discards_deliberation_trace(self) -> None:
        trace = "SECRET INTERNAL REASONING" * 100
        envelope = CognitiveDeliberativeEnvelopeState[str](
            deliberation_trace=trace,
            payload="y = 2\n",
        )
        result = _epistemic_strip(envelope)
        assert "SECRET" not in result
        assert result == "y = 2\n"


# ═════════════════════════════════════════════════════════════════════════════
# Phase 2 & 3: Native Validation (Syntax & Schema)
# ═════════════════════════════════════════════════════════════════════════════


class TestNativeValidation:
    """Native validation must catch syntax errors and missing schemas."""

    def test_valid_python_parses(self) -> None:
        payload = "def greet(name: str) -> str:\n    return f'Hello, {name}'\n"
        _native_validation(payload, target_schema=None)  # Should not raise

    def test_invalid_python_raises(self) -> None:
        with pytest.raises(SyntaxError):
            _native_validation("def broken(:\n", target_schema=None)

    def test_empty_module_parses(self) -> None:
        _native_validation("", target_schema=None)


# ═════════════════════════════════════════════════════════════════════════════
# Phase 4: Receipt Generation
# ═════════════════════════════════════════════════════════════════════════════


class TestReceiptGeneration:
    """The receipt must contain a valid SHA-256 hash of the payload."""

    def test_receipt_hash_matches(self) -> None:
        payload = "x = 42\n"
        receipt = _generate_receipt(
            payload=payload,
            solver_urn="urn:coreason:solver:test:v1",
            tokens_burned=100,
        )
        expected_hash = compute_canonical_hash(payload)
        assert receipt.execution_hash == expected_hash
        assert receipt.solver_urn == "urn:coreason:solver:test:v1"
        assert receipt.tokens_burned == 100

    def test_receipt_is_oracle_execution_receipt(self) -> None:
        receipt = _generate_receipt(
            payload="y = 1\n",
            solver_urn="urn:coreason:solver:test:v1",
            tokens_burned=0,
        )
        assert isinstance(receipt, OracleExecutionReceipt)


# ═════════════════════════════════════════════════════════════════════════════
# Full Pipeline Integration
# ═════════════════════════════════════════════════════════════════════════════


class TestFullPipeline:
    """End-to-end tests for the complete PVV pipeline."""

    def test_valid_code_produces_receipt(self) -> None:
        envelope = CognitiveDeliberativeEnvelopeState[str](
            deliberation_trace="Let me think about this carefully...",
            payload="def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        )
        receipt = execute_pvv_pipeline(
            envelope=envelope,
            solver_urn="urn:coreason:solver:claw_developer:v1",
            tokens_burned=1500,
        )
        assert isinstance(receipt, OracleExecutionReceipt)
        assert receipt.tokens_burned == 1500
        assert len(receipt.execution_hash) == 64

    def test_syntax_error_halts_pipeline(self) -> None:
        envelope = CognitiveDeliberativeEnvelopeState[str](
            deliberation_trace="Generating code...",
            payload="def broken(:\n",
        )
        with pytest.raises(SyntaxError):
            execute_pvv_pipeline(
                envelope=envelope,
                solver_urn="urn:coreason:solver:claw_developer:v1",
                tokens_burned=100,
            )
