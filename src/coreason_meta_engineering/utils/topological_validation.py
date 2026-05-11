# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")
# A copy of the license is available at <https://prosperitylicense.com/versions/3.0.0>
# For details, see the LICENSE file
# Commercial use beyond a 30-day trial requires a separate license
#
# Source Code: <https://github.com/CoReason-AI/coreason-meta-engineering>

import re

# Canonical URN regex — must stay synchronized with ActionSpaceURNState
# in coreason_manifest.spec.ontology.  Supports multiple namespace authorities
# (e.g. coreason, nlm, ohdsi) and validates the category segment against the
# 6 Universal Asset Categories.
_URN_PATTERN = re.compile(
    r"^urn:[a-z0-9_]+:actionspace:(oracle|solver|effector|substrate|sensory|node):[a-z0-9_]+:v[0-9]+$"
)

_VALID_CATEGORIES = frozenset({"oracle", "solver", "effector", "substrate", "sensory", "node"})


def verify_cryptographic_urn_boundary(action_space_id: str) -> None:
    """Validate that a URN conforms to the ActionSpaceURNState regex.

    Enforces the multi-authority URN format defined in ``coreason-manifest``:
    ``urn:{authority}:actionspace:{category}:{capability_name}:v{version}``

    The authority segment supports any lowercase namespace (e.g. ``coreason``,
    ``nlm``, ``ohdsi``).  The category must be one of the 6 Universal Asset
    Categories defined by ``ActionSpaceCategoryProfile``.

    Args:
        action_space_id: The Uniform Resource Name to validate.

    Raises:
        ValueError: If the URN does not match the canonical regex pattern.
    """
    if not _URN_PATTERN.match(action_space_id):
        raise ValueError(
            f"Invalid URN format. action_space_id must match the pattern "
            f"'urn:{{authority}}:actionspace:{{category}}:{{name}}:v{{version}}' "
            f"where category is one of {sorted(_VALID_CATEGORIES)}. "
            f"Received: {action_space_id}"
        )


class SemanticAmbiguityError(Exception):
    pass


def extract_semantic_wells(docstring: str) -> dict[str, str]:
    """Parse the 4 explicit components from the docstring."""
    wells = {"instruction": "", "affordance": "", "bounds": "", "routing": ""}
    if not docstring:
        return wells

    lines = docstring.split("\n")
    current_well = None

    for line in lines:
        if "AGENT INSTRUCTION:" in line:
            current_well = "instruction"
            wells[current_well] += line.split("AGENT INSTRUCTION:")[1] + "\n"
        elif "CAUSAL AFFORDANCE:" in line:
            current_well = "affordance"
            wells[current_well] += line.split("CAUSAL AFFORDANCE:")[1] + "\n"
        elif "EPISTEMIC BOUNDS:" in line:
            current_well = "bounds"
            wells[current_well] += line.split("EPISTEMIC BOUNDS:")[1] + "\n"
        elif "MCP ROUTING TRIGGERS:" in line:
            current_well = "routing"
            wells[current_well] += line.split("MCP ROUTING TRIGGERS:")[1] + "\n"
        elif current_well:
            wells[current_well] += line + "\n"

    return {k: v.strip() for k, v in wells.items()}


def generate_multi_well_embeddings(docstring: str) -> dict[str, list[float]]:
    """Generates four distinct vector embeddings using sentence-transformers."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        # Fallback if sentence-transformers not installed (e.g. CI without ML deps)
        return {k: [0.0] * 384 for k in ["instruction", "affordance", "bounds", "routing"]}

    model = SentenceTransformer("all-MiniLM-L6-v2")
    wells = extract_semantic_wells(docstring)

    embeddings = {}
    for well_name, content in wells.items():
        vector = model.encode(content).tolist() if content else [0.0] * 384
        embeddings[well_name] = vector

    return embeddings


def check_semantic_ambiguity(embeddings: dict[str, list[float]], local_registry_matrix: dict) -> bool:
    """Computes cosine similarity against existing capabilities in the matrix."""
    import numpy as np

    for urn, data in local_registry_matrix.items():
        for well_name in ["instruction", "affordance", "bounds", "routing"]:
            emb_key = f"embedding_{well_name}"
            if emb_key in data and len(data[emb_key]) == len(embeddings[well_name]):
                target_vector = np.array(embeddings[well_name])
                existing_vector = np.array(data[emb_key])

                norm_target = np.linalg.norm(target_vector)
                norm_existing = np.linalg.norm(existing_vector)

                if norm_target == 0 or norm_existing == 0:
                    continue

                similarity = np.dot(target_vector, existing_vector) / (norm_target * norm_existing)

                if similarity > 0.95:
                    raise SemanticAmbiguityError(
                        f"Collision detected with {urn} on semantic well '{well_name}' (Score: {similarity:.2f}). "
                        "Please add topological constraints to disambiguate your documentation."
                    )
    return True
