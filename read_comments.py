# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import json

with open("comments.json", encoding="utf-8-sig") as f:
    comments = json.load(f)

for c in comments:
    path = c.get("path", "unknown")
    line = c.get("line", "unknown")
    body = c.get("body", "")
    print(f"{path}:{line} - {body}")
