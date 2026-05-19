# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

"""Tests for the CLA first-use acceptance gate."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from coreason_meta_engineering.utils.cla_gate import (
    CLA_ACCEPTANCE_TEXT,
    CLANotAcceptedError,
    _get_cla_marker_path,
    enforce_cla_gate,
    is_cla_accepted,
    record_cla_acceptance,
)


class TestIsCLAAccepted:
    """Tests for the is_cla_accepted function."""

    def test_not_accepted_when_no_marker(self, tmp_path: Path) -> None:
        assert is_cla_accepted(tmp_path) is False

    def test_accepted_after_recording(self, tmp_path: Path) -> None:
        record_cla_acceptance(operator_id="test-user", base_dir=tmp_path)
        assert is_cla_accepted(tmp_path) is True

    def test_rejected_when_marker_is_corrupt_json(self, tmp_path: Path) -> None:
        marker = tmp_path / "cla_accepted.json"
        marker.write_text("not valid json", encoding="utf-8")
        assert is_cla_accepted(tmp_path) is False

    def test_rejected_when_accepted_is_false(self, tmp_path: Path) -> None:
        marker = tmp_path / "cla_accepted.json"
        marker.write_text(json.dumps({"accepted": False, "cla_version": "v1.0"}), encoding="utf-8")
        assert is_cla_accepted(tmp_path) is False

    def test_rejected_when_wrong_version(self, tmp_path: Path) -> None:
        marker = tmp_path / "cla_accepted.json"
        marker.write_text(json.dumps({"accepted": True, "cla_version": "v0.9"}), encoding="utf-8")
        assert is_cla_accepted(tmp_path) is False


class TestRecordCLAAcceptance:
    """Tests for the record_cla_acceptance function."""

    def test_creates_marker_file(self, tmp_path: Path) -> None:
        result = record_cla_acceptance(operator_id="test-user", base_dir=tmp_path)
        assert result.exists()

    def test_marker_content_is_valid(self, tmp_path: Path) -> None:
        record_cla_acceptance(operator_id="test-user", base_dir=tmp_path)
        marker = tmp_path / "cla_accepted.json"
        data = json.loads(marker.read_text(encoding="utf-8"))
        assert data["accepted"] is True
        assert data["cla_version"] == "v1.0"
        assert data["operator_id"] == "test-user"
        assert data["acceptance_text"] == CLA_ACCEPTANCE_TEXT
        assert "accepted_at" in data

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "nested"
        record_cla_acceptance(operator_id="test-user", base_dir=nested)
        assert (nested / "cla_accepted.json").exists()

    def test_default_operator_id_from_env(self, tmp_path: Path) -> None:
        record_cla_acceptance(base_dir=tmp_path)
        marker = tmp_path / "cla_accepted.json"
        data = json.loads(marker.read_text(encoding="utf-8"))
        # Should pick up USERNAME or USER from env, or fallback to "unknown"
        assert isinstance(data["operator_id"], str)
        assert len(data["operator_id"]) > 0


class TestEnforceCLAGate:
    """Tests for the enforce_cla_gate function."""

    def test_raises_when_not_accepted(self, tmp_path: Path) -> None:
        # Ensure env var is not set
        old_val = os.environ.pop("COREASON_CLA_ACCEPTED", None)
        try:
            with pytest.raises(CLANotAcceptedError):
                enforce_cla_gate(tmp_path)
        finally:
            if old_val is not None:
                os.environ["COREASON_CLA_ACCEPTED"] = old_val

    def test_passes_when_accepted(self, tmp_path: Path) -> None:
        old_val = os.environ.pop("COREASON_CLA_ACCEPTED", None)
        try:
            record_cla_acceptance(operator_id="test-user", base_dir=tmp_path)
            # Should not raise — exercises the is_cla_accepted(base_dir) path
            enforce_cla_gate(tmp_path)
        finally:
            if old_val is not None:
                os.environ["COREASON_CLA_ACCEPTED"] = old_val

    def test_passes_with_env_var_bypass(self, tmp_path: Path) -> None:
        old_val = os.environ.get("COREASON_CLA_ACCEPTED")
        os.environ["COREASON_CLA_ACCEPTED"] = "yes"
        try:
            # Should not raise even without marker file
            enforce_cla_gate(tmp_path)
        finally:
            if old_val is not None:
                os.environ["COREASON_CLA_ACCEPTED"] = old_val
            else:
                os.environ.pop("COREASON_CLA_ACCEPTED", None)

    def test_env_var_case_insensitive(self, tmp_path: Path) -> None:
        old_val = os.environ.get("COREASON_CLA_ACCEPTED")
        os.environ["COREASON_CLA_ACCEPTED"] = "YES"
        try:
            enforce_cla_gate(tmp_path)
        finally:
            if old_val is not None:
                os.environ["COREASON_CLA_ACCEPTED"] = old_val
            else:
                os.environ.pop("COREASON_CLA_ACCEPTED", None)

    def test_error_message_contains_instructions(self, tmp_path: Path) -> None:
        old_val = os.environ.pop("COREASON_CLA_ACCEPTED", None)
        try:
            with pytest.raises(CLANotAcceptedError, match="coreason-forge accept-cla"):
                enforce_cla_gate(tmp_path)
        finally:
            if old_val is not None:
                os.environ["COREASON_CLA_ACCEPTED"] = old_val


class TestGetCLAMarkerPath:
    """Tests for the default marker path resolution."""

    def test_default_path_uses_home_dir(self) -> None:
        from pathlib import Path as P

        result = _get_cla_marker_path(None)
        assert result == P.home() / ".coreason" / "cla_accepted.json"

    def test_override_path(self, tmp_path: Path) -> None:
        result = _get_cla_marker_path(tmp_path)
        assert result == tmp_path / "cla_accepted.json"
