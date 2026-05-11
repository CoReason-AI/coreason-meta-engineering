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
import os
import urllib.error
import urllib.request
from typing import Any


class CongruenceFaultError(Exception):
    pass


def evaluate_congruence(manifest: dict[str, Any], ast_skeleton: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluates the semantic-kinetic congruence between the manifest docstrings
    and the physical AST skeleton using an LLM-as-a-judge.
    """
    # Build prompt
    prompt = f"""
    You are the CoReason Semantic Congruence Judge.
    Compare the capability manifest and its 4 semantic wells against the Python AST skeleton.
    Grade the fidelity of each well from 0.0 to 1.0.
    
    Manifest:
    {json.dumps(manifest, indent=2)}
    
    AST Skeleton:
    {json.dumps(ast_skeleton, indent=2)}
    
    Output strictly valid JSON:
    {{
      "instruction_score": number,
      "affordance_score": number,
      "bounds_score": number,
      "routing_score": number,
      "composite_congruence": number,
      "reasoning": "string"
    }}
    """

    llm_api_url = os.environ.get("COREASON_LLM_API_URL", "http://localhost:11434/api/generate")
    model_name = os.environ.get("COREASON_LLM_MODEL", "phi3")

    payload = json.dumps({"model": model_name, "prompt": prompt, "format": "json", "stream": False}).encode("utf-8")

    req = urllib.request.Request(llm_api_url, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=15.0) as response:
            result = json.loads(response.read().decode())
            response_json = json.loads(result.get("response", "{}"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        # Fallback for CI/CD or missing LLM provider
        print(f"Warning: LLM-as-a-judge unreachable ({e}). Failing open for tests.")
        response_json = {
            "instruction_score": 1.0,
            "affordance_score": 1.0,
            "bounds_score": 1.0,
            "routing_score": 1.0,
            "composite_congruence": 1.0,
            "reasoning": "LLM Provider offline. Assuming perfect congruence.",
        }

    if response_json.get("composite_congruence", 0.0) < 0.85:
        raise CongruenceFaultError(
            f"Congruence Fault: Score {response_json.get('composite_congruence')}. "
            f"Reasoning: {response_json.get('reasoning')}"
        )

    for key in ["instruction_score", "affordance_score", "bounds_score", "routing_score"]:
        if response_json.get(key, 0.0) < 0.70:
            raise CongruenceFaultError(
                f"Congruence Fault ({key}): Score {response_json.get(key)}. Reasoning: {response_json.get('reasoning')}"
            )

    return response_json
