# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_meta_engineering


def verify_cryptographic_urn_boundary(action_space_id: str) -> None:
    """
    Validates that a globally unique URN follows the required 0-Trust prefix.

    Args:
        action_space_id: The Uniform Resource Name to validate.

    Raises:
        ValueError: If the URN does not start with 'urn:coreason:actionspace:'.
    """
    if not action_space_id.startswith("urn:coreason:actionspace:"):
        raise ValueError(
            f"Invalid URN format. action_space_id must start with 'urn:coreason:actionspace:'."
            f" Received: {action_space_id}"
        )
