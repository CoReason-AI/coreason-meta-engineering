#!/usr/bin/env python3
import os
import sys

HEADER = """# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
"""

def process_file(filepath: str) -> bool:
    try:
        with open(filepath) as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False

    lines = content.splitlines(keepends=True)
    if not lines:
        return False

    has_shebang = lines[0].startswith("#!")

    header_to_check = "".join(lines[1:]) if has_shebang else content
    if header_to_check.startswith(HEADER):
        return False

    start_idx = 1 if has_shebang else 0
    if start_idx < len(lines) and lines[start_idx].startswith("# Copyright"):
        for i in range(start_idx, len(lines)):
            stripped = lines[i].strip()
            if not stripped.startswith("#") and stripped != "":
                start_idx = i
                break
        else:
            start_idx = len(lines)

    new_content = ""
    if has_shebang:
        new_content += lines[0]
    new_content += HEADER + "".join(lines[start_idx:])

    if new_content != content:
        try:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Added header to {filepath}")
            return True
        except Exception as e:
            print(f"Error writing to {filepath}: {e}", file=sys.stderr)
            return False

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
