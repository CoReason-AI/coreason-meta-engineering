# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

"""First-Use Affirmative CLA Acceptance Gate.

Enforces that every operator explicitly accepts the Prosperity Public License 3.0
and CoReason Contributor License Agreement before the Forge scaffolds any capability.

The acceptance is recorded as a persistent marker file in the operator's home
directory (~/.coreason/cla_accepted.json). Once accepted, the gate is transparent
for all subsequent invocations.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from coreason_meta_engineering.utils.logger import logger

# ────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────

_CLA_DIR_NAME = ".coreason"
_CLA_MARKER_FILE = "cla_accepted.json"
_CLA_VERSION = "v1.0"

CLA_ACCEPTANCE_TEXT = (
    "By selecting 'yes', I affirm that I have read and agree to the "
    "CoReason Contributor License Agreement (CLA) v1.0 and the "
    "Prosperity Public License 3.0. I understand that all contributions "
    "and Forge-generated output are copyright-assigned to CoReason, Inc. "
    "unless I hold a separate commercial license agreement."
)


class CLANotAcceptedError(RuntimeError):
    """Raised when the operator has not yet accepted the CLA."""


# ────────────────────────────────────────────────────────────────────
# Marker Path Resolution
# ────────────────────────────────────────────────────────────────────


def _get_cla_marker_path(base_dir: Path | None = None) -> Path:
    """Return the path to the CLA acceptance marker file.

    Args:
        base_dir: Optional override for the marker directory (used in tests).
                  Defaults to ``~/.coreason/``.
    """
    if base_dir is not None:
        return base_dir / _CLA_MARKER_FILE
    return Path.home() / _CLA_DIR_NAME / _CLA_MARKER_FILE


# ────────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────────


def is_cla_accepted(base_dir: Path | None = None) -> bool:
    """Check whether the operator has previously accepted the CLA.

    Args:
        base_dir: Optional override for the marker directory.

    Returns:
        True if a valid CLA acceptance marker exists.
    """
    marker = _get_cla_marker_path(base_dir)
    if not marker.exists():
        return False

    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        return bool(data.get("accepted") is True and data.get("cla_version") == _CLA_VERSION)
    except (json.JSONDecodeError, OSError):
        return False


def record_cla_acceptance(
    operator_id: str = "",
    base_dir: Path | None = None,
) -> Path:
    """Record the operator's affirmative CLA acceptance.

    Args:
        operator_id: Optional identifier for the accepting operator
                     (e.g., GitHub username or DID).
        base_dir: Optional override for the marker directory.

    Returns:
        The path to the written marker file.
    """
    marker = _get_cla_marker_path(base_dir)
    marker.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "accepted": True,
        "cla_version": _CLA_VERSION,
        "accepted_at": datetime.now(UTC).isoformat(),
        "operator_id": operator_id or os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        "acceptance_text": CLA_ACCEPTANCE_TEXT,
    }

    marker.write_text(json.dumps(record, indent=2), encoding="utf-8")
    logger.info(f"CLA acceptance recorded at {marker}")
    return marker


def enforce_cla_gate(base_dir: Path | None = None) -> None:
    """Gate function — raises if the CLA has not been accepted.

    This is called at the top of every Forge scaffolding tool.
    If the environment variable ``COREASON_CLA_ACCEPTED=yes`` is set,
    the gate is bypassed (for CI/CD pipelines where acceptance is
    handled at the infrastructure level).

    Args:
        base_dir: Optional override for the marker directory.

    Raises:
        CLANotAcceptedError: If the CLA has not been accepted.
    """
    # CI/CD bypass — acceptance is handled by the pipeline configuration
    if os.environ.get("COREASON_CLA_ACCEPTED", "").lower() == "yes":
        return

    if is_cla_accepted(base_dir):
        return

    raise CLANotAcceptedError(
        "\n╔══════════════════════════════════════════════════════════════════╗\n"
        "║          CoReason Contributor License Agreement (CLA)          ║\n"
        "╠══════════════════════════════════════════════════════════════════╣\n"
        "║                                                                ║\n"
        "║  Before using the CoReason Forge, you must accept the CLA.    ║\n"
        "║                                                                ║\n"
        f"║  {CLA_ACCEPTANCE_TEXT[:62]}  ║\n"
        "║                                                                ║\n"
        "║  To accept, run:                                              ║\n"
        "║    uv run coreason-forge accept-cla                           ║\n"
        "║                                                                ║\n"
        "║  Or set environment variable:                                 ║\n"
        "║    COREASON_CLA_ACCEPTED=yes                                  ║\n"
        "║                                                                ║\n"
        "║  CLA: https://github.com/CoReason-AI/coreason-documentation/  ║\n"
        "║  docs/05_internal_operations/02_engineering_processes/         ║\n"
        "║  03_contributor_license_agreement.md                          ║\n"
        "║                                                                ║\n"
        "╚══════════════════════════════════════════════════════════════════╝\n"
    )
