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

_VALID_CATEGORIES = frozenset(
    {"oracle", "solver", "effector", "substrate", "sensory", "node"}
)


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
