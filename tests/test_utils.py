# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

"""Tests for topological_validation.py and kinetic_guillotine.py."""

from unittest.mock import MagicMock

import libcst as cst
import pytest

from coreason_meta_engineering.utils.kinetic_guillotine import (
    HighEntropySolverDiffVisitor,
    TopologicalBoundaryViolation,
)
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


# ═════════════════════════════════════════════════════════════════════════════
# TopologicalBoundaryViolation Exception
# ═════════════════════════════════════════════════════════════════════════════


class TestTopologicalBoundaryViolation:
    """The exception must carry structured violation metadata."""

    def test_exception_is_exception(self) -> None:
        exc = TopologicalBoundaryViolation("FORBIDDEN_IMPORT", "import os")
        assert isinstance(exc, Exception)

    def test_exception_attributes(self) -> None:
        exc = TopologicalBoundaryViolation("FORBIDDEN_CALL", "eval()")
        assert exc.violation_type == "FORBIDDEN_CALL"
        assert exc.node_description == "eval()"
        assert "TOPOLOGICAL BOUNDARY VIOLATION" in str(exc)


# ═════════════════════════════════════════════════════════════════════════════
# HighEntropySolverDiffVisitor
# ═════════════════════════════════════════════════════════════════════════════


class TestHighEntropySolverDiffVisitor:
    """The visitor must detect all forbidden patterns in the Forbidden Node Matrix."""

    def test_nodes_visited_counter(self) -> None:
        code = "x = 1\ny = 2\nz = x + y\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        module.visit(visitor)
        assert visitor.nodes_visited >= 0

    def test_import_star_does_not_crash(self) -> None:
        code = "from typing import *\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        module.visit(visitor)  # Should not raise

    def test_safe_import_passes(self) -> None:
        """Cover the return-None path after the for-loop completes without violation."""
        code = "import json\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        module.visit(visitor)  # Should not raise
        assert visitor.nodes_visited >= 1

    def test_dotted_import_forbidden(self) -> None:
        code = "import os.path\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            module.visit(visitor)

    def test_safe_method_call_on_object(self) -> None:
        code = "result = my_model.predict(data)\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        module.visit(visitor)  # Should not raise

    def test_import_io_raises(self) -> None:
        code = "import io\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            module.visit(visitor)

    def test_import_tempfile_raises(self) -> None:
        code = "import tempfile\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            module.visit(visitor)

    def test_import_glob_raises(self) -> None:
        code = "import glob\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            module.visit(visitor)

    def test_from_sys_import_raises(self) -> None:
        code = "from sys import argv\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            module.visit(visitor)

    def test_httpx_import_raises(self) -> None:
        code = "import httpx\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            module.visit(visitor)

    def test_aiohttp_import_raises(self) -> None:
        code = "import aiohttp\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_IMPORT"):
            module.visit(visitor)

    def test_os_environ_attr_call_raises(self) -> None:
        code = "os.environ()\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_ATTR_CALL"):
            module.visit(visitor)

    def test_os_getenv_attr_call_raises(self) -> None:
        code = "os.getenv('KEY')\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_ATTR_CALL"):
            module.visit(visitor)

    def test_shutil_copy_raises(self) -> None:
        code = "shutil.copy('a', 'b')\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_ATTR_CALL"):
            module.visit(visitor)

    def test_shutil_move_raises(self) -> None:
        code = "shutil.move('a', 'b')\n"
        module = cst.parse_module(code)
        visitor = HighEntropySolverDiffVisitor()
        with pytest.raises(TopologicalBoundaryViolation, match="FORBIDDEN_ATTR_CALL"):
            module.visit(visitor)

    def test_extract_dotted_name_fallback(self) -> None:
        """Cover the fallback return '' in _extract_dotted_name for unexpected node types."""
        result = HighEntropySolverDiffVisitor._extract_dotted_name(cst.Integer("42"))
        assert result == ""

    def test_visit_import_star_branch(self) -> None:
        """Cover the ImportStar branch in visit_Import via direct method call."""
        visitor = HighEntropySolverDiffVisitor()
        mock_node = MagicMock(spec=cst.Import)
        mock_node.names = cst.ImportStar()
        result = visitor.visit_Import(mock_node)
        assert result is None
        assert visitor.nodes_visited == 1
