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
by autonomous agents (e.g. Claw Code).  Implements the 4-phase verification
loop documented in ``docs/01_core_architecture/02_execution_engine/
25_abstract_syntax_tree_compilation.md``:

1. **Epistemic Strip** — discard the probabilistic ``deliberation_trace``.
2. **Syntax Integrity** — parse the payload with ``libcst.parse_module()``.
3. **Topological Bounds** — traverse via the Kinetic Guillotine visitor.
4. **Receipt Generation** — SHA-256 hash → ``OracleExecutionReceipt``.
"""

from __future__ import annotations

import libcst as cst
from coreason_manifest.spec import DeliberativeEnvelope, OracleExecutionReceipt
from coreason_urn_authority.crypto.hasher import compute_canonical_hash

from coreason_meta_engineering.utils.kinetic_guillotine import (
    HighEntropySolverDiffVisitor,
)
from coreason_meta_engineering.utils.logger import logger


def execute_pvv_pipeline(
    *,
    envelope: DeliberativeEnvelope[str],
    solver_urn: str,
    tokens_burned: int,
) -> OracleExecutionReceipt:
    """Execute the full PVV pipeline on a ``DeliberativeEnvelope``.

    Args:
        envelope: The raw envelope produced by a high-entropy solver.
            The ``payload`` field MUST contain a valid Python source string.
        solver_urn: The fully qualified URN of the solver agent
            (e.g. ``urn:coreason:solver:claw_developer:v1``).
        tokens_burned: The total tokens consumed during the generation.

    Returns:
        An ``OracleExecutionReceipt`` attesting the payload is safe for
        kinetic deployment.

    Raises:
        libcst.ParserSyntaxError: If the payload is not valid Python.
        TopologicalBoundaryViolation: If any forbidden AST node is detected.
    """
    # ── Phase 1: Epistemic Strip ─────────────────────────────────────────
    payload = _epistemic_strip(envelope)

    # ── Phase 2: Syntax Integrity ────────────────────────────────────────
    module = _parse_syntax(payload)

    # ── Phase 3: Topological Bounds (Kinetic Guillotine) ─────────────────
    _enforce_topological_bounds(module)

    # ── Phase 4: Receipt Generation ──────────────────────────────────────
    return _generate_receipt(
        module=module,
        solver_urn=solver_urn,
        tokens_burned=tokens_burned,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Phase Functions
# ─────────────────────────────────────────────────────────────────────────────


def _epistemic_strip(envelope: DeliberativeEnvelope[str]) -> str:
    """Phase 1 — Discard the ``deliberation_trace`` and extract only the payload.

    The heuristic "thoughts" of the agent have zero mathematical bearing on
    the validity of the code and must not contaminate the AST compiler.
    """
    logger.info(
        "Epistemic Strip: discarding deliberation_trace "
        f"({len(envelope.deliberation_trace)} chars), "
        f"extracting payload ({len(envelope.payload)} chars)."
    )
    return envelope.payload


def _parse_syntax(payload: str) -> cst.Module:
    """Phase 2 — Feed the payload into ``libcst.parse_module()``.

    If the solver hallucinated invalid Python syntax the parser fails
    deterministically with ``libcst.ParserSyntaxError``.
    """
    module = cst.parse_module(payload)
    logger.info("Syntax Integrity: payload parsed successfully.")
    return module


def _enforce_topological_bounds(module: cst.Module) -> None:
    """Phase 3 — Traverse the CST via the Kinetic Guillotine visitor.

    Raises:
        TopologicalBoundaryViolation: If any illegal AST node is detected.
    """
    visitor = HighEntropySolverDiffVisitor()
    module.visit(visitor)
    logger.info(
        f"Topological Boundary Enforcement passed: {visitor.nodes_visited} nodes scanned, zero violations detected."
    )


def _generate_receipt(
    *,
    module: cst.Module,
    solver_urn: str,
    tokens_burned: int,
) -> OracleExecutionReceipt:
    """Phase 4 — Hash the verified AST payload and produce the receipt."""

    # Extract the deterministically formatted code (stripping LLM variations)
    canonical_code = module.code

    # Hash using the authoritative ledger crypto
    execution_hash = compute_canonical_hash(canonical_code)

    receipt = OracleExecutionReceipt(
        execution_hash=execution_hash,
        solver_urn=solver_urn,
        tokens_burned=tokens_burned,
    )
    logger.info(f"OracleExecutionReceipt generated: hash={execution_hash[:16]}...")
    return receipt
