# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

import asyncio
import json
import typing
from pathlib import Path

from coreason_manifest.spec import CognitiveDeliberativeEnvelopeState

from coreason_meta_engineering.pvv import execute_pvv_pipeline
from coreason_meta_engineering.utils.logger import logger

try:
    from coreason_runtime.execution_plane.fabricator import dispatch_agent_generation
except ImportError:
    # If not running in a full swarm, fallback logic can be placed here or we just raise.
    async def dispatch_agent_generation(prompt_context: str) -> str:
        raise NotImplementedError("Dynamic forge requires coreason_runtime.execution_plane.fabricator.")


class DynamicForgeOrchestrator:
    """
    Orchestrates the dynamic provisioning of agents to scaffold ASTs.
    """

    @staticmethod
    async def scaffold_ast(
        target_file_path: str,
        action_space_id: str,
        geometric_schema: dict[str, typing.Any] | list[dict[str, typing.Any]],
        complexity_score: int,
        prompt_template: str,
    ) -> str:
        """
        Dynamically provisions N agents based on complexity_score, executes them in parallel,
        and merges the first deterministically valid result via the Kinetic Guillotine.
        """
        n_agents = 3 if complexity_score >= 8 else 1

        schema_json = json.dumps(geometric_schema, indent=2)

        prompt_context = (
            f"You are an AST fabrication agent operating under the CoReason Prosperity Protocol.\n"
            f"You must scaffold a Python class or function that mathematically adheres "
            f"to the following JSON Schema bounds:\n"
            f"{schema_json}\n\n"
            f"Do not hallucinate keys outside this schema. Output only valid Python code.\n\n"
            f"{prompt_template}"
        )

        logger.info(f"Provisioning {n_agents} agents for {action_space_id}...")

        tasks = [dispatch_agent_generation(prompt_context) for _ in range(n_agents)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_code = None
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Agent generation failed: {result}")
                continue

            try:
                payload = result if isinstance(result, str) else result.get("payload", "")
                trace = "" if isinstance(result, str) else result.get("deliberation_trace", "")

                envelope = CognitiveDeliberativeEnvelopeState[str](
                    deliberation_trace=trace,
                    payload=payload,
                )

                receipt = execute_pvv_pipeline(
                    envelope=envelope,
                    solver_urn=action_space_id,
                    tokens_burned=0,
                )

                if receipt:
                    valid_code = payload
                    break
            except Exception as e:
                logger.warning(f"Kinetic Guillotine rejected payload: {e}")

        if not valid_code:
            raise RuntimeError(
                f"SystemFaultEvent: KineticGuillotineViolation. All {n_agents} agents failed to generate valid code."
            )

        target_file = Path(target_file_path)
        # Note: In an actual workflow we may want to inject this into the file. For now we overwrite/create.
        if target_file.exists():
            target_file.write_text(valid_code, encoding="utf-8")
        else:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(valid_code, encoding="utf-8")

        return valid_code


def orchestrate_generation(*args: typing.Any, **kwargs: typing.Any) -> str:
    """Synchronous wrapper for MCP."""
    return asyncio.run(DynamicForgeOrchestrator.scaffold_ast(*args, **kwargs))
