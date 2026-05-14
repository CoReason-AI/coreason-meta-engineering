# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

"""Tests for topological_validation.py."""

import pytest

from coreason_meta_engineering.utils.topological_validation import (
    verify_cryptographic_urn_boundary,
)

# ═════════════════════════════════════════════════════════════════════════════
# URN Validation
# ═════════════════════════════════════════════════════════════════════════════


class TestURNValidation:
    """verify_cryptographic_urn_boundary must enforce canonical URN format."""

    def test_valid_coreason_urn(self) -> None:
        verify_cryptographic_urn_boundary("urn:coreason:actionspace:solver:clinical_extractor:v1")

    def test_valid_ohdsi_urn(self) -> None:
        verify_cryptographic_urn_boundary("urn:ohdsi:actionspace:oracle:vocab_lookup:v2")

    def test_valid_nlm_urn(self) -> None:
        verify_cryptographic_urn_boundary("urn:nlm:actionspace:oracle:rxnorm_resolver:v1")

    def test_valid_all_categories(self) -> None:
        for cat in ("oracle", "solver", "effector", "substrate", "sensory", "node"):
            verify_cryptographic_urn_boundary(f"urn:coreason:actionspace:{cat}:test:v1")

    def test_invalid_urn_missing_version(self) -> None:
        with pytest.raises(ValueError, match="Invalid URN format"):
            verify_cryptographic_urn_boundary("urn:coreason:actionspace:solver:test")

    def test_invalid_urn_no_prefix(self) -> None:
        with pytest.raises(ValueError, match="Invalid URN format"):
            verify_cryptographic_urn_boundary("finance_ledger_v1")

    def test_invalid_urn_wrong_category(self) -> None:
        with pytest.raises(ValueError, match="Invalid URN format"):
            verify_cryptographic_urn_boundary("urn:coreason:actionspace:widget:test:v1")
