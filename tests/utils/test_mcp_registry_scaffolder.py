# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

from pathlib import Path
import pytest
from coreason_meta_engineering.utils.mcp_registry_scaffolder import generate_push_command, publish_mcp_artifact


def test_generate_push_command_basic() -> None:
    """
    Asserts that the wash push command is generated correctly with mandatory annotations.
    """
    component_path = Path("build/test_solver.wasm")
    oci_uri = "ghcr.io/coreason-ai/test-solver:v1"

    command = generate_push_command(component_path, oci_uri)

    assert command == [
        "wash",
        "push",
        "ghcr.io/coreason-ai/test-solver:v1",
        "build/test_solver.wasm",
        "--annotation",
        "org.opencontainers.image.source=https://github.com/coreason-ai/coreason",
    ]


def test_generate_push_command_insecure() -> None:
    """
    Asserts that the --insecure flag is appended correctly for local/untrusted registries.
    """
    component_path = Path("build/test_solver.wasm")
    oci_uri = "localhost:5000/test-solver:v1"

    command = generate_push_command(component_path, oci_uri, insecure=True)

    assert "--insecure" in command
    assert "localhost:5000/test-solver:v1" in command


def test_publish_mcp_artifact_invalid_extension() -> None:
    """
    Asserts that the publisher enforces strict WASI 0.2 component validation (.wasm suffix).
    """
    component_path = Path("src/solver.py")
    oci_uri = "ghcr.io/coreason-ai/test-solver:v1"

    with pytest.raises(ValueError, match="Strict WASI 0.2 enforcement"):
        publish_mcp_artifact(component_path, oci_uri)
