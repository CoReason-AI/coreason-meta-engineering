# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

from pathlib import Path

import pytest

from coreason_meta_engineering.pvv import (
    ValidationReceiptEvent,
    accumulate_pvv_signatures,
    broadcast_urn_to_mesh,
    compute_merkle_directory_cid,
    post_scaffold_cid_injection,
)


def test_compute_merkle_directory_cid(tmp_path: Path) -> None:
    # Create some dummy files
    (tmp_path / "file1.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "file2.py").write_text("print('world')", encoding="utf-8")
    (tmp_path / "manifest.yaml").write_text("Should be ignored", encoding="utf-8")

    cid = compute_merkle_directory_cid(tmp_path)
    assert cid.startswith("sha256:")
    assert len(cid) > 10


def test_post_scaffold_cid_injection_success(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("validation:\n  cryptographic_hash: null", encoding="utf-8")

    # Create a target file to pretend it was just scaffolded
    target = tmp_path / "server.py"
    target.touch()

    post_scaffold_cid_injection(target)

    content = manifest.read_text(encoding="utf-8")
    assert "sha256:" in content


def test_post_scaffold_cid_injection_append_validation(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("validation:\n  other_field: 123", encoding="utf-8")
    target = tmp_path / "server.py"
    target.touch()

    post_scaffold_cid_injection(target)
    content = manifest.read_text(encoding="utf-8")
    assert "sha256:" in content


def test_post_scaffold_cid_injection_append_no_validation(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("other: field", encoding="utf-8")
    target = tmp_path / "server.py"
    target.touch()

    post_scaffold_cid_injection(target)
    content = manifest.read_text(encoding="utf-8")
    assert "sha256:" in content


def test_post_scaffold_cid_injection_no_manifest(tmp_path: Path) -> None:
    target = tmp_path / "server.py"
    target.touch()

    # Should not raise
    post_scaffold_cid_injection(target)


def test_broadcast_urn_to_mesh_success(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text('urn: "urn:test"\nvalidation:\n  cryptographic_hash: "sha256:123"', encoding="utf-8")

    with pytest.raises(NotImplementedError):
        broadcast_urn_to_mesh(str(tmp_path))


def test_broadcast_urn_to_mesh_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(NotImplementedError):
        # Even if missing manifest, NotImplementedError is raised first since WASM compilation is at the top
        broadcast_urn_to_mesh(str(tmp_path))


def test_broadcast_urn_to_mesh_missing_dir() -> None:
    with pytest.raises(FileNotFoundError):
        broadcast_urn_to_mesh("/non/existent/dir/12345")


def test_accumulate_pvv_signatures_genesis_override(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text('epistemic_status: "DRAFT"\nconsensus_signatures: []', encoding="utf-8")

    receipt = ValidationReceiptEvent(
        urn="urn:test", cid="sha256:abc", node_id="genesis_node_1", signature_jwt="genesis_jwt_abc", is_approved=True
    )

    result = accumulate_pvv_signatures(str(tmp_path), [receipt])

    assert "Status -> PUBLISHED" in result
    content = manifest.read_text(encoding="utf-8")
    assert "PUBLISHED" in content
    assert "genesis_jwt_abc" in content


def test_accumulate_pvv_signatures_five_signatures(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text('epistemic_status: "DRAFT"', encoding="utf-8")

    receipts = [
        ValidationReceiptEvent(
            urn="urn:test", cid="sha256:abc", node_id=f"node_{i}", signature_jwt=f"jwt_{i}", is_approved=True
        )
        for i in range(5)
    ]

    result = accumulate_pvv_signatures(str(tmp_path), receipts)

    assert "Status -> PUBLISHED" in result
    content = manifest.read_text(encoding="utf-8")
    assert "PUBLISHED" in content
    assert "jwt_0" in content
    assert "jwt_4" in content


def test_accumulate_pvv_signatures_pending(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text('epistemic_status: "DRAFT"', encoding="utf-8")

    receipts = [
        ValidationReceiptEvent(
            urn="urn:test", cid="sha256:abc", node_id=f"node_{i}", signature_jwt=f"jwt_{i}", is_approved=True
        )
        for i in range(3)
    ]

    result = accumulate_pvv_signatures(str(tmp_path), receipts)

    assert "Consensus pending" in result
    content = manifest.read_text(encoding="utf-8")
    assert "DRAFT" in content


def test_accumulate_pvv_signatures_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        accumulate_pvv_signatures(str(tmp_path), [])


def test_post_scaffold_cid_injection_empty_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("", encoding="utf-8")
    target = tmp_path / "server.py"
    target.touch()

    post_scaffold_cid_injection(target)
    content = manifest.read_text(encoding="utf-8")
    assert "sha256:" in content


def test_accumulate_pvv_signatures_empty_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("", encoding="utf-8")

    receipt = ValidationReceiptEvent(
        urn="urn:test", cid="sha256:abc", node_id="genesis_node_1", signature_jwt="genesis_jwt_abc", is_approved=True
    )

    result = accumulate_pvv_signatures(str(tmp_path), [receipt])

    assert "Status -> PUBLISHED" in result
    content = manifest.read_text(encoding="utf-8")
    assert "PUBLISHED" in content
    assert "genesis_jwt_abc" in content
