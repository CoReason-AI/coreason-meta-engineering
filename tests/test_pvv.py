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

import libcst as cst
import pytest
from coreason_manifest.spec import DeliberativeEnvelope, OracleExecutionReceipt
from coreason_urn_authority.crypto.hasher import compute_canonical_hash

from coreason_meta_engineering.pvv import (
    _enforce_topological_bounds,
    _epistemic_strip,
    _generate_receipt,
    _parse_syntax,
    execute_pvv_pipeline,
)
from coreason_meta_engineering.utils.kinetic_guillotine import (
    TopologicalBoundaryViolation,
)

# ═════════════════════════════════════════════════════════════════════════════
# Phase 1: Epistemic Strip
# ═════════════════════════════════════════════════════════════════════════════


class TestEpistemicStrip:
    """The Epistemic Strip must discard the deliberation_trace entirely."""

    def test_extracts_payload(self) -> None:
        envelope = DeliberativeEnvelope[str](
            deliberation_trace="I am thinking very hard about this problem...",
            payload="x = 1\n",
        )
        result = _epistemic_strip(envelope)
        assert result == "x = 1\n"

    def test_discards_deliberation_trace(self) -> None:
        trace = "SECRET INTERNAL REASONING" * 100
        envelope = DeliberativeEnvelope[str](
            deliberation_trace=trace,
            payload="y = 2\n",
        )
        result = _epistemic_strip(envelope)
        assert "SECRET" not in result
        assert result == "y = 2\n"


# ═════════════════════════════════════════════════════════════════════════════
# Phase 2: Syntax Integrity
# ═════════════════════════════════════════════════════════════════════════════


class TestSyntaxIntegrity:
    """The syntax check must parse valid Python and reject invalid syntax."""

    def test_valid_python_parses(self) -> None:
        module = _parse_syntax("def greet(name: str) -> str:\n    return f'Hello, {name}'\n")
        assert isinstance(module, cst.Module)

    def test_invalid_python_raises(self) -> None:
        with pytest.raises(cst.ParserSyntaxError):
            _parse_syntax("def broken(:\n")

    def test_empty_module_parses(self) -> None:
        module = _parse_syntax("")
        assert isinstance(module, cst.Module)


# ═════════════════════════════════════════════════════════════════════════════
# Phase 3: Topological Bounds (Kinetic Guillotine)
# ═════════════════════════════════════════════════════════════════════════════


class TestTopologicalBounds:
    """The Kinetic Guillotine must block forbidden AST nodes."""

    def test_clean_code_passes(self) -> None:
        module = cst.parse_module("x = 1\ny = x + 2\n")
        _enforce_topological_bounds(module)  # Should not raise

    def test_import_os_raises(self) -> None:
        module = cst.parse_module("import os\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_IMPORT.*os"):
            _enforce_topological_bounds(module)

    def test_from_os_import_raises(self) -> None:
        module = cst.parse_module("from os import path\n")
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            _enforce_topological_bounds(module)

    def test_import_http_raises(self) -> None:
        module = cst.parse_module("import http\n")
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            _enforce_topological_bounds(module)

    def test_import_pathlib_raises(self) -> None:
        module = cst.parse_module("import pathlib\n")
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            _enforce_topological_bounds(module)

    def test_call_eval_raises(self) -> None:
        module = cst.parse_module("x = eval('1+1')\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_CALL.*eval"):
            _enforce_topological_bounds(module)

    def test_call_exec_raises(self) -> None:
        module = cst.parse_module("exec('print(1)')\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_CALL.*exec"):
            _enforce_topological_bounds(module)

    def test_call_open_raises(self) -> None:
        module = cst.parse_module("f = open('file.txt')\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_CALL.*open"):
            _enforce_topological_bounds(module)

    def test_call_dunder_import_raises(self) -> None:
        module = cst.parse_module("mod = __import__('os')\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_CALL.*__import__"):
            _enforce_topological_bounds(module)

    def test_call_compile_raises(self) -> None:
        module = cst.parse_module("c = compile('pass', '<string>', 'exec')\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_CALL.*compile"):
            _enforce_topological_bounds(module)

    def test_os_system_call_raises(self) -> None:
        module = cst.parse_module("os.system('ls')\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_ATTR_CALL.*os\.system"):
            _enforce_topological_bounds(module)

    def test_subprocess_run_call_raises(self) -> None:
        module = cst.parse_module("subprocess.run(['ls'])\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_ATTR_CALL.*subprocess\.run"):
            _enforce_topological_bounds(module)

    def test_subprocess_popen_call_raises(self) -> None:
        module = cst.parse_module("subprocess.Popen(['ls'])\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_ATTR_CALL.*subprocess\.Popen"):
            _enforce_topological_bounds(module)

    def test_shutil_rmtree_call_raises(self) -> None:
        module = cst.parse_module("shutil.rmtree('/tmp')\n")
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_ATTR_CALL.*shutil\.rmtree"):
            _enforce_topological_bounds(module)

    def test_safe_function_call_passes(self) -> None:
        module = cst.parse_module("result = my_func(x, y)\n")
        _enforce_topological_bounds(module)  # Should not raise

    def test_safe_attribute_call_passes(self) -> None:
        module = cst.parse_module("result = model.predict(data)\n")
        _enforce_topological_bounds(module)  # Should not raise


# ═════════════════════════════════════════════════════════════════════════════
# Phase 4: Receipt Generation
# ═════════════════════════════════════════════════════════════════════════════


class TestReceiptGeneration:
    """The receipt must contain a valid SHA-256 hash of the payload."""

    def test_receipt_hash_matches(self) -> None:
        payload = "x = 42\n"
        module = cst.parse_module(payload)
        receipt = _generate_receipt(
            module=module,
            solver_urn="urn:coreason:solver:test:v1",
            tokens_burned=100,
        )
        expected_hash = compute_canonical_hash(module.code)
        assert receipt.execution_hash == expected_hash
        assert receipt.solver_urn == "urn:coreason:solver:test:v1"
        assert receipt.tokens_burned == 100

    def test_receipt_is_oracle_execution_receipt(self) -> None:
        module = cst.parse_module("y = 1\n")
        receipt = _generate_receipt(
            module=module,
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
        envelope = DeliberativeEnvelope[str](
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

    def test_malicious_eval_halts_pipeline(self) -> None:
        envelope = DeliberativeEnvelope[str](
            deliberation_trace="I need to dynamically evaluate...",
            payload="result = eval(user_input)\n",
        )
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_CALL.*eval"):
            execute_pvv_pipeline(
                envelope=envelope,
                solver_urn="urn:coreason:solver:claw_developer:v1",
                tokens_burned=500,
            )

    def test_network_call_halts_pipeline(self) -> None:
        envelope = DeliberativeEnvelope[str](
            deliberation_trace="Let me fetch some data...",
            payload="import requests\nr = requests.get('http://evil.com')\n",
        )
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            execute_pvv_pipeline(
                envelope=envelope,
                solver_urn="urn:coreason:solver:claw_developer:v1",
                tokens_burned=200,
            )

    def test_syntax_error_halts_pipeline(self) -> None:
        envelope = DeliberativeEnvelope[str](
            deliberation_trace="Generating code...",
            payload="def broken(:\n",
        )
        with pytest.raises(cst.ParserSyntaxError):
            execute_pvv_pipeline(
                envelope=envelope,
                solver_urn="urn:coreason:solver:claw_developer:v1",
                tokens_burned=100,
            )

    def test_file_open_halts_pipeline(self) -> None:
        envelope = DeliberativeEnvelope[str](
            deliberation_trace="Let me read the .env file...",
            payload="f = open('.env', 'r')\nsecrets = f.read()\n",
        )
        with pytest.raises(TopologicalBoundaryViolation, match=r"FORBIDDEN_CALL.*open"):
            execute_pvv_pipeline(
                envelope=envelope,
                solver_urn="urn:coreason:solver:claw_developer:v1",
                tokens_burned=300,
            )
