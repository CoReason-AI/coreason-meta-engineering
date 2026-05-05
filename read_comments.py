import json

with open("comments.json", encoding="utf-8-sig") as f:
    comments = json.load(f)

for c in comments:
    path = c.get("path", "unknown")
    line = c.get("line", "unknown")
    body = c.get("body", "")
    print(f"{path}:{line} - {body}")
