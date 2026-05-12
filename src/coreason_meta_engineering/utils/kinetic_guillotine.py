import asyncio
import json
import os
from typing import Any, ClassVar

import libcst as cst
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent


class TopologicalBoundaryViolation(Exception):  # noqa: N818
    """Raised when an autonomous agent attempts to bypass the AST sandbox."""

    def __init__(self, violation_type: str, node_description: str) -> None:
        self.violation_type = violation_type
        self.node_description = node_description
        super().__init__(f"TOPOLOGICAL BOUNDARY VIOLATION: {violation_type} detected at '{node_description}'")


class HighEntropySolverDiffVisitor(cst.CSTVisitor):
    """
    Kinetic Guillotine: Traverses the CST to enforce the 'Hollow Plane' mandate.
    """

    FORBIDDEN_IMPORT_BASES: ClassVar[set[str]] = {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "io",
        "tempfile",
        "glob",
        "httpx",
        "requests",
        "aiohttp",
        "urllib",
        "socket",
        "http",
        "pathlib",
    }

    FORBIDDEN_CALLS: ClassVar[set[str]] = {"eval", "exec", "open", "compile", "__import__"}

    FORBIDDEN_ATTR_CALLS: ClassVar[set[str]] = {
        "os.environ",
        "os.getenv",
        "os.system",
        "shutil.copy",
        "shutil.move",
        "shutil.rmtree",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
    }

    def __init__(self) -> None:
        self.nodes_visited = 0

    def on_visit(self, node: cst.CSTNode) -> bool:
        self.nodes_visited += 1
        return super().on_visit(node)

    def visit_Import(self, node: cst.Import) -> None:  # noqa: N802
        for name_item in node.names:
            dotted_name = self._extract_dotted_name(name_item.name)
            base_module = dotted_name.split(".")[0]
            if base_module in self.FORBIDDEN_IMPORT_BASES:
                raise TopologicalBoundaryViolation("FORBIDDEN_IMPORT", dotted_name)
            if "." in dotted_name:
                # Forbid dotted imports like os.path to satisfy test_dotted_import_forbidden
                raise TopologicalBoundaryViolation("FORBIDDEN_IMPORT", dotted_name)

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:  # noqa: N802
        if node.module:
            dotted_name = self._extract_dotted_name(node.module)
            base_module = dotted_name.split(".")[0]
            if base_module in self.FORBIDDEN_IMPORT_BASES:
                raise TopologicalBoundaryViolation("FORBIDDEN_IMPORT", dotted_name)

    def visit_Call(self, node: cst.Call) -> None:  # noqa: N802
        func = node.func
        if isinstance(func, cst.Name):
            if func.value in self.FORBIDDEN_CALLS:
                raise TopologicalBoundaryViolation("FORBIDDEN_CALL", func.value)
        elif isinstance(func, cst.Attribute):
            dotted_name = self._extract_dotted_name(func)
            if dotted_name in self.FORBIDDEN_ATTR_CALLS:
                raise TopologicalBoundaryViolation("FORBIDDEN_ATTR_CALL", dotted_name)

    @staticmethod
    def _extract_dotted_name(node: cst.CSTNode) -> str:
        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, cst.Attribute):
            base = HighEntropySolverDiffVisitor._extract_dotted_name(node.value)
            attr = node.attr.value
            return f"{base}.{attr}" if base else attr
        return ""


class KineticGuillotineError(Exception):
    pass


def format_violations(response_data: dict[str, Any]) -> str:
    lines = ["Compliance Guillotine Blocked Publish:"]
    lines.extend(
        f" - [{v.get('severity', 'CRITICAL')}] {v.get('rule_name')} in "
        f"{v.get('file_name', 'unknown')}:{v.get('line_number', 0)} "
        f"({v.get('context_snippet', '')})"
        for v in response_data.get("violations", [])
    )
    return "\n".join(lines)


async def execute_guillotine_scan(urn: str, payload_files: list[dict[str, Any]]) -> bool:
    """Connects to coreason-compliance-mcp and requests a scan."""
    # Try to find the scanner.py script
    server_path = os.environ.get(
        "COREASON_COMPLIANCE_SERVER_PATH",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
            "coreason-compliance-mcp",
            "src",
            "coreason_compliance_mcp",
            "scanner.py",
        ),
    )

    mcp_url = os.getenv("COREASON_COMPLIANCE_URL", "stdio")

    if mcp_url != "stdio":
        # SSE logic would go here. For now we use stdio.
        pass

    server_params = StdioServerParameters(
        command="uv",
        args=["run", server_path],
    )

    try:
        async with stdio_client(server_params) as (read, write), ClientSession(read, write) as session:
            await session.initialize()

            try:
                result = await asyncio.wait_for(
                    session.call_tool("evaluate_payload", arguments={"target_urn": urn, "files": payload_files}),
                    timeout=2.0,  # 2000ms SLA
                )
            except TimeoutError as e:
                raise KineticGuillotineError(
                    "ComplianceTimeout: Server took too long to evaluate. Publish aborted."
                ) from e

            response_content = result.content[0]
            if not isinstance(response_content, TextContent):
                raise KineticGuillotineError(
                    f"Invalid response from compliance server: expected TextContent, got {type(response_content)}"
                )
            response_data = json.loads(response_content.text)
            if response_data.get("status") == "CLEAN":
                return True
            raise KineticGuillotineError(format_violations(response_data))
    except Exception as e:
        if isinstance(e, KineticGuillotineError):
            raise
        raise KineticGuillotineError(f"GuillotineConnectionError: Cannot verify payload safety. Details: {e!s}") from e
