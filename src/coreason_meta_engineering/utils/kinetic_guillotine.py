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
Kinetic Guillotine — Zero-Trust AST Boundary Enforcement.

This module contains the strict ``libcst.CSTVisitor`` that traverses
agent-proposed code diffs and enforces the Forbidden Node Matrix.
Any violation triggers a fatal ``TopologicalBoundaryViolation``,
halting the PVV pipeline and marking the execution receipt as FALSIFIED.

The Forbidden Node Matrix
-------------------------
- **File I/O:** ``open()``, ``read()``, ``write()``, ``os.path``
- **System Execution:** ``os.system``, ``subprocess.run``, ``subprocess.Popen``, ``shlex``
- **Network Egress:** ``requests``, ``urllib``, ``socket``, ``http``
- **Dynamic Execution:** ``eval()``, ``exec()``, ``__import__()``
"""

from __future__ import annotations

import libcst as cst

__all__ = [
    "HighEntropySolverDiffVisitor",
    "TopologicalBoundaryViolation",
]


# ─────────────────────────────────────────────────────────────────────────────
# The Forbidden Node Matrix
# ─────────────────────────────────────────────────────────────────────────────

_FORBIDDEN_IMPORT_MODULES: frozenset[str] = frozenset(
    {
        # System Execution
        "os",
        "subprocess",
        "shlex",
        "shutil",
        "sys",
        # Network Egress
        "requests",
        "urllib",
        "socket",
        "http",
        "httpx",
        "aiohttp",
        # File I/O (low-level)
        "io",
        "tempfile",
        "glob",
        "pathlib",
    }
)

_FORBIDDEN_CALL_NAMES: frozenset[str] = frozenset(
    {
        # Dynamic Execution
        "eval",
        "exec",
        "compile",
        "__import__",
        # File I/O
        "open",
    }
)

_FORBIDDEN_ATTR_CALLS: frozenset[tuple[str, str]] = frozenset(
    {
        ("os", "system"),
        ("os", "popen"),
        ("os", "exec"),
        ("os", "execvp"),
        ("os", "spawn"),
        ("os", "remove"),
        ("os", "unlink"),
        ("os", "rename"),
        ("os", "mkdir"),
        ("os", "makedirs"),
        ("os", "rmdir"),
        ("os", "listdir"),
        ("os", "walk"),
        ("os", "environ"),
        ("os", "getenv"),
        ("subprocess", "run"),
        ("subprocess", "call"),
        ("subprocess", "check_output"),
        ("subprocess", "Popen"),
        ("shutil", "copy"),
        ("shutil", "move"),
        ("shutil", "rmtree"),
    }
)


# ─────────────────────────────────────────────────────────────────────────────
# Exception
# ─────────────────────────────────────────────────────────────────────────────


class TopologicalBoundaryViolation(Exception):  # noqa: N818
    """Fatal exception raised when the Kinetic Guillotine detects a forbidden AST node.

    When this exception fires, the PVV process halts immediately.
    The WASM container's execution receipt is marked as FALSIFIED.
    """

    def __init__(self, violation_type: str, node_description: str) -> None:
        self.violation_type = violation_type
        self.node_description = node_description
        super().__init__(
            f"TOPOLOGICAL BOUNDARY VIOLATION [{violation_type}]: "
            f"Forbidden AST node detected — {node_description}. "
            f"The PVV pipeline has been halted. "
            f"The execution receipt is FALSIFIED."
        )


# ─────────────────────────────────────────────────────────────────────────────
# The Kinetic Guillotine Visitor
# ─────────────────────────────────────────────────────────────────────────────


class HighEntropySolverDiffVisitor(cst.CSTVisitor):
    """A strict CSTVisitor for High-Entropy Solver Diffs.

    Traverses the entire parsed CST and raises ``TopologicalBoundaryViolation``
    the instant it encounters any node matching the Forbidden Node Matrix.

    This visitor enforces the following security constraints:
        - No File I/O operations (open, read, write, os.path)
        - No OS module commands (os.system, subprocess)
        - No network calls (requests, urllib, socket)
        - No dynamic execution (eval, exec, __import__)
    """

    def __init__(self) -> None:
        self.nodes_visited: int = 0

    # ── Import Statements ────────────────────────────────────────────────

    def visit_Import(self, node: cst.Import) -> bool | None:  # noqa: N802
        """Check ``import X`` statements."""
        self.nodes_visited += 1
        if isinstance(node.names, cst.ImportStar):
            return None
        for alias in node.names:
            module_name = self._extract_dotted_name(alias.name)
            root_module = module_name.split(".")[0]
            if root_module in _FORBIDDEN_IMPORT_MODULES:
                raise TopologicalBoundaryViolation(
                    violation_type="FORBIDDEN_IMPORT",
                    node_description=f"import {module_name}",
                )
        return None

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool | None:  # noqa: N802
        """Check ``from X import Y`` statements."""
        self.nodes_visited += 1
        if node.module is not None:
            module_name = self._extract_dotted_name(node.module)
            root_module = module_name.split(".")[0]
            if root_module in _FORBIDDEN_IMPORT_MODULES:
                raise TopologicalBoundaryViolation(
                    violation_type="FORBIDDEN_IMPORT",
                    node_description=f"from {module_name} import ...",
                )
        return None

    # ── Function Calls ───────────────────────────────────────────────────

    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        """Check direct function calls (eval, exec, open, __import__)."""
        self.nodes_visited += 1
        func = node.func

        # Direct calls: eval(...), exec(...), open(...)
        if isinstance(func, cst.Name) and func.value in _FORBIDDEN_CALL_NAMES:
            raise TopologicalBoundaryViolation(
                violation_type="FORBIDDEN_CALL",
                node_description=f"{func.value}()",
            )

        # Attribute calls: os.system(...), subprocess.run(...)
        if isinstance(func, cst.Attribute):
            obj = func.value
            attr = func.attr
            if isinstance(obj, cst.Name) and isinstance(attr, cst.Name):
                pair = (obj.value, attr.value)
                if pair in _FORBIDDEN_ATTR_CALLS:
                    raise TopologicalBoundaryViolation(
                        violation_type="FORBIDDEN_ATTR_CALL",
                        node_description=f"{obj.value}.{attr.value}()",
                    )
        return None

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _extract_dotted_name(node: cst.BaseExpression) -> str:
        """Recursively extract dotted module names (e.g., ``os.path``)."""
        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, cst.Attribute):
            prefix = HighEntropySolverDiffVisitor._extract_dotted_name(node.value)
            if isinstance(node.attr, cst.Name):
                return f"{prefix}.{node.attr.value}"
        return ""
