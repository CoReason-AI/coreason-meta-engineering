# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

import json
from typing import Any


def generate_server_json(geometric_schema: dict[str, Any] | list[dict[str, Any]]) -> str:
    """
    Generates an MCP Registry server.json file based on the geometric schema.
    This guarantees type isomorphism and prevents LLM hallucination.
    """
    if isinstance(geometric_schema, list):
        geometric_schema = geometric_schema[0] if geometric_schema else {}

    urn = geometric_schema.get("urn", "urn:coreason:actionspace:unknown:v1")

    # Extract components of URN assuming urn:coreason:actionspace:{type}:{name}:{version}
    parts = urn.split(":")
    capability_name = parts[4] if len(parts) >= 6 else "unknown_capability"

    server_json = {
        "name": capability_name,
        "description": geometric_schema.get("description", f"CoReason capabilities for {capability_name}"),
        "version": "1.0.0",
        "mcp_version": "1.0",
        "author": "CoReason, Inc.",
        "license": geometric_schema.get("economics", {}).get("license_class", "PROSPERITY_3.0_COMMERCIAL"),
        "entrypoint": "mcp-server",
        "repository": f"https://github.com/CoReason-AI/{capability_name}",
        "registry_metadata": {
            "urn": urn,
            "epistemic_status": geometric_schema.get("epistemic_status", "DRAFT"),
            "billing_tier": geometric_schema.get("economics", {}).get("billing_tier", "TIER_1_STANDARD"),
            "validation": geometric_schema.get("validation", {}),
        },
    }

    return json.dumps(server_json, indent=2)
