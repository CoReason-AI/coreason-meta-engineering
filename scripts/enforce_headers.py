#!/usr/bin/env python3
# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import os
import sys

import libcst as cst

HEADER_LINES = [
    "# Copyright (c) 2026 CoReason, Inc.",
    "#",
    "# This software is proprietary and dual-licensed.",
    '# Licensed under the Prosperity Public License 3.0 (the "License").',
    "# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)",
    "# For details, see the LICENSE file.",
    "# Commercial use beyond a 30-day trial requires a separate license.",
    "#",
    "# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)",
]


class HeaderInjector(cst.CSTTransformer):  # type: ignore[misc]
    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:  # noqa: N802, ARG002
        # Check if already has header
        if updated_node.header:
            for line in updated_node.header:
                if getattr(line, "comment", None) and "CoReason, Inc" in getattr(line.comment, "value", ""):
                    return updated_node

        new_header = list(updated_node.header)
        new_header.extend(cst.EmptyLine(comment=cst.Comment(value=hl), indent=False) for hl in HEADER_LINES)
        return updated_node.with_changes(header=tuple(new_header))


def process_file(filepath: str) -> bool:
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False

    try:
        module = cst.parse_module(content)
        transformer = HeaderInjector()
        new_module = module.visit(transformer)
        new_content = new_module.code

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Added header to {filepath}")
            return True

        return False
    except Exception as e:
        print(f"Error transforming {filepath}: {e}", file=sys.stderr)
        return False


def main() -> None:
    modified = False
    for filepath in sys.argv[1:]:
        if not os.path.isfile(filepath):
            continue
        if process_file(filepath):
            modified = True

    if modified:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
