import ast
from typing import Any


def extract_kinetic_skeleton(filepath: str) -> dict[str, Any]:
    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    skeleton: dict[str, Any] = {
        "imports": [],
        "signatures": [],
        "docstring": "",
    }

    mod_doc = ast.get_docstring(tree)
    if mod_doc:
        skeleton["docstring"] = mod_doc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                skeleton["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                skeleton["imports"].append(node.module)
        elif isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            returns = ast.unparse(node.returns) if node.returns else "None"
            skeleton["signatures"].append(f"def {node.name}({', '.join(args)}) -> {returns}:")
            if not skeleton["docstring"]:
                func_doc = ast.get_docstring(node)
                if func_doc:
                    skeleton["docstring"] = func_doc
        elif isinstance(node, ast.ClassDef) and not skeleton["docstring"]:
            class_doc = ast.get_docstring(node)
            if class_doc:
                skeleton["docstring"] = class_doc

    return skeleton
