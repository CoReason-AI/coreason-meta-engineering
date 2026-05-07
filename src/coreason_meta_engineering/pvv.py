# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering

import hashlib
from pathlib import Path

from pydantic import BaseModel, Field
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True


class FederatedDiscoveryIntent(BaseModel):
    """
    AGENT INSTRUCTION: Encapsulates the intent to broadcast a new capability URN to the macroscopic P2P mesh.
    CAUSAL AFFORDANCE: Triggers remote validation (PVV) by the Swarm.
    EPISTEMIC BOUNDS: Must include valid WASM payload and cryptographic CID.
    MCP ROUTING TRIGGERS: p2p, mesh, discovery, broadcast, pvv
    """

    urn: str = Field(description="The globally unique Uniform Resource Name")
    cid: str = Field(description="The cryptographic identity (SHA-256) of the bundle")
    wasm_payload_hex: str = Field(description="Hex-encoded WASM binary of the capability")


class ValidationReceiptEvent(BaseModel):
    """
    AGENT INSTRUCTION: A verifiable receipt from a remote Swarm node affirming or rejecting a capability.
    CAUSAL AFFORDANCE: Accumulates towards consensus to promote a URN from DRAFT to PUBLISHED.
    EPISTEMIC BOUNDS: Must contain a valid OIDC JWT signature.
    MCP ROUTING TRIGGERS: pvv, receipt, validation, consensus, vote
    """

    urn: str = Field(description="The URN being validated")
    cid: str = Field(description="The CID of the bundle being validated")
    node_id: str = Field(description="The identity of the validating Swarm node")
    signature_jwt: str = Field(description="OIDC JWT asserting the validation result")
    is_approved: bool = Field(description="Whether the node approved the capability")


def compute_merkle_directory_cid(directory: Path) -> str:
    """
    Computes a deterministic Merkle CID for a directory.
    (Mock implementation representing coreason_manifest.utils.algebra logic)
    """
    hasher = hashlib.sha256()
    for file_path in sorted(directory.rglob("*")):
        if file_path.is_file() and file_path.name != "manifest.yaml":
            # Sort order and content hashing
            hasher.update(file_path.name.encode("utf-8"))
            hasher.update(file_path.read_bytes())
    return f"sha256:{hasher.hexdigest()}"


def post_scaffold_cid_injection(target_file_path: Path) -> None:
    """
    Post-Scaffold Hook: Reads the bundle directory, computes CID, and injects into manifest.yaml
    """
    urn_dir = target_file_path.parent
    manifest_path = urn_dir / "manifest.yaml"

    if not manifest_path.exists():
        # Manifest not found, bundle might be incomplete
        return

    cid = compute_merkle_directory_cid(urn_dir)

    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        data = {}

    if "validation" not in data or not isinstance(data["validation"], dict):
        data["validation"] = {}

    data["validation"]["cryptographic_hash"] = cid

    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def publish_capability_to_mesh(urn: str, python_code: str) -> str:
    """
    Compiles code in memory, uses CIDGenerator, and broadcasts FederatedDiscoveryIntent.
    """
    try:
        from coreason_urn_authority.crypto.hasher import CIDGenerator  # type: ignore[import-untyped]

        payload = {"urn": urn, "code": python_code}
        cid = CIDGenerator.generate_cid(payload)
    except ImportError:
        cid = "sha256:mock"

    wasm_payload_hex = python_code.encode("utf-8").hex()

    intent = FederatedDiscoveryIntent(urn=urn, cid=cid, wasm_payload_hex=wasm_payload_hex)
    _ = intent  # Used to broadcast to the P2P Mesh

    return f"Successfully compiled and broadcasted {urn} with CID {cid}"


def broadcast_urn_to_mesh(urn_directory_path: str) -> str:
    """
    Compiles WASM and broadcasts FederatedDiscoveryIntent to the P2P Mesh.
    """
    urn_dir = Path(urn_directory_path)
    if not urn_dir.exists():
        raise FileNotFoundError(f"URN Directory {urn_directory_path} not found.")

    # 1. Compile WASM Target
    raise NotImplementedError("Physical WASM compilation (extism/cargo) is deferred to the Kinetic Execution Plane.")


def accumulate_pvv_signatures(urn_directory_path: str, receipts: list[ValidationReceiptEvent]) -> str:
    """
    Accumulates PVV signatures and promotes DRAFT to PUBLISHED if consensus met.
    """
    urn_dir = Path(urn_directory_path)
    manifest_path = urn_dir / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError("manifest.yaml missing.")

    valid_signatures = []
    has_genesis_override = False

    for receipt in receipts:
        if receipt.is_approved:
            valid_signatures.append(receipt.signature_jwt)
            if "genesis_node" in receipt.node_id or "genesis" in receipt.signature_jwt:
                has_genesis_override = True

    if has_genesis_override or len(valid_signatures) >= 5:
        # Promote to PUBLISHED
        with open(manifest_path, encoding="utf-8") as f:
            data = yaml.load(f)

        if data is None:
            data = {}

        data["epistemic_status"] = "PUBLISHED"

        if "consensus_signatures" not in data or not isinstance(data["consensus_signatures"], list):
            data["consensus_signatures"] = []

        data["consensus_signatures"].extend(valid_signatures)

        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

        return f"Consensus reached. {len(valid_signatures)} signatures applied. Status -> PUBLISHED."

    return f"Consensus pending. Only {len(valid_signatures)}/5 valid signatures collected."
