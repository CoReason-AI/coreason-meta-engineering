import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class KineticGuillotineError(Exception):
    pass


def format_violations(response_data: dict) -> str:
    lines = ["Compliance Guillotine Blocked Publish:"]
    lines.extend(
        f" - [{v.get('severity', 'CRITICAL')}] {v.get('rule_name')} in "
        f"{v.get('file_name', 'unknown')}:{v.get('line_number', 0)} "
        f"({v.get('context_snippet', '')})"
        for v in response_data.get("violations", [])
    )
    return "\n".join(lines)


async def execute_guillotine_scan(urn: str, payload_files: list) -> bool:
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

            response_data = json.loads(result.content[0].text)
            if response_data.get("status") == "CLEAN":
                return True
            raise KineticGuillotineError(format_violations(response_data))
    except Exception as e:
        if isinstance(e, KineticGuillotineError):
            raise
        raise KineticGuillotineError(f"GuillotineConnectionError: Cannot verify payload safety. Details: {e!s}") from e
