# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

import subprocess
from pathlib import Path

from .logger import logger


def generate_push_command(
    component_path: Path,
    oci_uri: str,
    insecure: bool = False,
) -> list[str]:
    """
    AGENT INSTRUCTION: Generates the deterministic 'wash push' command for OCI artifact publishing.
    This ensures standard WASI 0.2 components are pushed to standard registries with proper annotations.

    CAUSAL AFFORDANCE: Enables the orchestrator to publish artifacts to OCI registries.

    EPISTEMIC BOUNDS: Operates on Path objects and URI strings. Enforces --insecure flag based on policy.
    Injects mandatory OCI annotations for traceability.

    MCP ROUTING TRIGGERS: OCI, WASI, wash, push, registry, artifact
    """
    command = [
        "wash",
        "push",
        oci_uri,
        component_path.as_posix(),
        "--annotation",
        "org.opencontainers.image.source=https://github.com/coreason-ai/coreason",
    ]
    if insecure:
        command.append("--insecure")
    return command


def publish_mcp_artifact(
    component_path: Path,
    oci_uri: str,
    insecure: bool = False,
) -> str:
    """
    AGENT INSTRUCTION: Executes the 'wash push' CLI command to publish a WASI component.
    This is the kinetic layer of artifact distribution.

    CAUSAL AFFORDANCE: Synchronously pushes a local .wasm component to a remote OCI registry.

    EPISTEMIC BOUNDS: Requires the 'wash' CLI to be present in the execution environment.
    Enforces strict .wasm extension check to guarantee WASI 0.2 component integrity.
    Wraps subprocess.run with strict error handling.

    MCP ROUTING TRIGGERS: OCI, WASI, wash, push, registry, artifact, kinetic
    """
    if component_path.suffix != ".wasm":
        raise ValueError(
            f"Strict WASI 0.2 enforcement: Capability artifacts must be compiled .wasm binaries. Got: {component_path.suffix}"
        )

    if not component_path.exists():
        raise FileNotFoundError(f"Component not found at {component_path}")

    command = generate_push_command(component_path, oci_uri, insecure)
    logger.info(f"Publishing artifact to {oci_uri}...")

    try:
        result = subprocess.run(  # noqa: S603
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(f"Successfully pushed {oci_uri}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push {oci_uri}: {e.stderr}")
        raise RuntimeError(f"wash push failed: {e.stderr}") from e
    except FileNotFoundError as e:
        logger.error("The 'wash' CLI was not found in the environment.")
        raise RuntimeError("The 'wash' CLI is required for OCI publishing but was not found.") from e
