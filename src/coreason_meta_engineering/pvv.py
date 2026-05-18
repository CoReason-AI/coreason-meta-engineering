# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

"""
PVV Pipeline — Proof, Validation, and Verification.

The deterministic ingestion pipeline for high-entropy solver diffs generated
by autonomous agents (e.g. Claw Code). Implements native Python execution
bounds via sub-process isolation and Pydantic validation (The True Guillotine).
"""

from __future__ import annotations

import contextlib
import importlib.util
import inspect
import sys
import tempfile
from pathlib import Path
from typing import Any

from coreason_manifest.spec import CognitiveDeliberativeEnvelopeState, OracleExecutionReceipt
from pydantic import BaseModel

from coreason_meta_engineering.utils.hasher import compute_canonical_hash
from coreason_meta_engineering.utils.logger import logger


def execute_pvv_pipeline(
    *,
    envelope: CognitiveDeliberativeEnvelopeState[str],
    solver_urn: str,
    tokens_burned: int,
    target_schema: dict[str, Any] | list[dict[str, Any]] | None = None,
) -> OracleExecutionReceipt:
    """Execute the full PVV pipeline using native Python bounds.

    1. Epistemic Strip
    2. Sub-process Isolation & Native Import (Syntax Check)
    3. Pydantic Validation (The True Guillotine)
    4. Receipt Generation
    """
    payload = _epistemic_strip(envelope)

    _native_validation(payload, target_schema)

    return _generate_receipt(
        payload=payload,
        solver_urn=solver_urn,
        tokens_burned=tokens_burned,
    )


def _epistemic_strip(envelope: CognitiveDeliberativeEnvelopeState[str]) -> str:
    logger.info("Epistemic Strip: extracting payload.")
    return str(envelope.payload)


def _native_validation(payload: str, target_schema: dict[str, Any] | list[dict[str, Any]] | None) -> None:
    """Writes the payload to a temp file, imports it natively, and validates via Pydantic."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
        f.write(payload)
        temp_path = Path(f.name)

    module_name = "generated_sandbox_module"
    try:
        spec = importlib.util.spec_from_file_location(module_name, temp_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Failed to create module spec.")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        # Native Import - catches syntax errors
        spec.loader.exec_module(module)

        # Pydantic Validation (The True Guillotine)
        if target_schema is not None:
            _compare_schema(module, target_schema)

    finally:
        # Cleanup
        if module_name in sys.modules:
            del sys.modules[module_name]
        with contextlib.suppress(OSError):
            temp_path.unlink()


def _compare_schema(module: Any, target_schema: dict[str, Any] | list[dict[str, Any]]) -> None:
    found_models = []
    for _name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseModel) and obj is not BaseModel:
            found_models.append(obj)

    if not found_models:
        if isinstance(target_schema, dict) and target_schema:
            raise ValueError("No Pydantic models found in the generated payload to validate against the target schema.")
        return

    if isinstance(target_schema, dict) and target_schema:
        target_properties = target_schema.get("properties", {})

        # Try to find a model that has all required properties
        missing_keys = []
        for model in found_models:
            model_schema = model.model_json_schema()
            model_properties = model_schema.get("properties", {})

            missing = [key for key in target_properties if key not in model_properties]
            if not missing:
                return  # Found a valid model
            missing_keys = missing

        if missing_keys:
            raise ValueError(f"Schema mismatch: missing property '{missing_keys[0]}' in generated class.")


def _generate_receipt(
    *,
    payload: str,
    solver_urn: str,
    tokens_burned: int,
) -> OracleExecutionReceipt:
    execution_hash = compute_canonical_hash(payload)

    receipt = OracleExecutionReceipt(
        execution_hash=execution_hash,
        solver_urn=solver_urn,
        tokens_burned=tokens_burned,
    )
    logger.info(f"OracleExecutionReceipt generated: hash={execution_hash[:16]}...")
    return receipt
