# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

import os
import shutil
import sys
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

    with pytest.raises(ValueError, match=r"Strict WASI 0\.2 enforcement"):
        publish_mcp_artifact(component_path, oci_uri)


def test_publish_mcp_artifact_not_found(tmp_path: Path) -> None:
    """
    Asserts that a FileNotFoundError is raised when a .wasm component does not exist.
    """
    non_existent = tmp_path / "missing.wasm"
    oci_uri = "ghcr.io/coreason-ai/test-solver:v1"

    with pytest.raises(FileNotFoundError, match="Component not found at"):
        publish_mcp_artifact(non_existent, oci_uri)


def test_publish_mcp_artifact_execution_missing_cli(tmp_path: Path) -> None:
    """
    Asserts that missing wash CLI raises a descriptive RuntimeError when the component exists.
    """
    dummy_wasm = tmp_path / "dummy.wasm"
    dummy_wasm.write_bytes(b"\x00asm\x01\x00\x00\x00")
    oci_uri = "localhost:5000/test-solver:v1"

    # Save original PATH and temporarily strip wash CLI path to force a missing CLI failure
    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = ""
    try:
        with pytest.raises(RuntimeError, match="The 'wash' CLI is required"):
            publish_mcp_artifact(dummy_wasm, oci_uri, insecure=True)
    finally:
        os.environ["PATH"] = old_path


def test_publish_mcp_artifact_execution_failure(tmp_path: Path) -> None:
    """
    Asserts that CalledProcessError from a failing wash push command is handled and re-raised cleanly.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    if sys.platform == "win32":
        shutil.copy2(sys.executable, bin_dir / "wash.exe")
        push_script = Path("push")
        push_script.write_text("import sys\nsys.stderr.write('error message\\n')\nsys.exit(1)\n", encoding="utf-8")
    else:
        wash_script = bin_dir / "wash"
        wash_script.write_text("#!/bin/sh\necho error message >&2\nexit 1\n", encoding="utf-8")
        wash_script.chmod(0o755)
        push_script = None

    dummy_wasm = tmp_path / "dummy.wasm"
    dummy_wasm.write_bytes(b"\x00asm\x01\x00\x00\x00")
    oci_uri = "localhost:5000/test-solver:v1"

    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
    try:
        with pytest.raises(RuntimeError, match="wash push failed: error message"):
            publish_mcp_artifact(dummy_wasm, oci_uri, insecure=True)
    finally:
        os.environ["PATH"] = old_path
        if push_script and push_script.exists():
            push_script.unlink()


def test_publish_mcp_artifact_execution_success(tmp_path: Path) -> None:
    """
    Asserts that a successful wash push command returns the standard output cleanly.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    if sys.platform == "win32":
        shutil.copy2(sys.executable, bin_dir / "wash.exe")
        push_script = Path("push")
        push_script.write_text("import sys\nprint('success message')\nsys.exit(0)\n", encoding="utf-8")
    else:
        wash_script = bin_dir / "wash"
        wash_script.write_text("#!/bin/sh\necho success message\nexit 0\n", encoding="utf-8")
        wash_script.chmod(0o755)
        push_script = None

    dummy_wasm = tmp_path / "dummy.wasm"
    dummy_wasm.write_bytes(b"\x00asm\x01\x00\x00\x00")
    oci_uri = "localhost:5000/test-solver:v1"

    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
    try:
        res = publish_mcp_artifact(dummy_wasm, oci_uri, insecure=True)
        assert "success message" in res
    finally:
        os.environ["PATH"] = old_path
        if push_script and push_script.exists():
            push_script.unlink()
