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
import shutil
import textwrap
from pathlib import Path
import libcst as cst
from libcst.metadata import PositionProvider
import yaml

class ActuatorExtractor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self):
        super().__init__()
        self.function_node: cst.FunctionDef | None = None
        self.urn_value: str | None = None
        self.class_nodes: list[cst.ClassDef] = []
        self.import_nodes: list[cst.Import | cst.ImportFrom] = []

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        if self.function_node is None:
            self.function_node = node

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.class_nodes.append(node)

    def visit_Import(self, node: cst.Import) -> None:
        self.import_nodes.append(node)

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        self.import_nodes.append(node)

    def visit_Assign(self, node: cst.Assign) -> None:
        for target in node.targets:
            if isinstance(target.target, cst.Attribute) and target.target.attr.value == "__action_space_urn__":
                if isinstance(node.value, cst.SimpleString):
                    self.urn_value = node.value.value.strip("'\"")


def generate_schema_code(import_codes: list[str], class_codes: list[str]) -> str:
    imports = "from coreason_manifest.spec.ontology import CoreasonBaseState\n"
    for imp in import_codes:
        if "fastmcp" not in imp:
            imports += imp + "\n"
    return imports + "\n\n".join(class_codes)

def generate_server_code(func_name: str, func_code: str, class_nodes: list) -> str:
    imports = "from mcp.server.fastmcp import FastMCP\n"
    if class_nodes:
        class_names = [c.name.value for c in class_nodes]
        imports += f"from schema import {', '.join(class_names)}\n"
        
    return f"""\
{imports}
mcp = FastMCP("{func_name}")

{func_code}

if __name__ == "__main__":
    mcp.run()
"""

def package_urn_bundle(source_file_path: str, target_urn: str, urn_authority_dir: str) -> str:
    source_path = Path(source_file_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file {source_file_path} not found.")
    
    authority_path = Path(urn_authority_dir)
    if not authority_path.exists():
        raise FileNotFoundError(f"URN Authority dir {urn_authority_dir} not found.")

    # 1. Parse source code
    source_code = source_path.read_text(encoding="utf-8")
    module = cst.parse_module(source_code)
    wrapper = cst.MetadataWrapper(module)
    extractor = ActuatorExtractor()
    wrapper.visit(extractor)

    if not extractor.function_node:
        raise ValueError("Could not find a function in the source file.")
    
    func_name = extractor.function_node.name.value
    
    # We will extract the exact AST code for the function
    func_code = module.code_for_node(extractor.function_node)
    
    # 2. Extract URN logic
    urn_parts = target_urn.split(":")
    if len(urn_parts) != 6:
        raise ValueError(f"Target URN {target_urn} does not have exactly 6 parts.")
    
    category = urn_parts[3]
    bundle_name = f"{urn_parts[4]}_{urn_parts[5]}"

    bundle_dir = authority_path / "assets" / category / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # 3. Write __init__.py
    init_file = bundle_dir / "__init__.py"
    init_file.write_text(f'__action_space_urn__ = "{target_urn}"\n', encoding="utf-8")

    # 4. Write manifest.yaml
    manifest_data = {
        "urn": target_urn,
        "clearance": "RESTRICTED",
        "epistemic_status": "DRAFT",
        "composition": {
            "topology": "ATOMIC",
            "dependencies": []
        },
        "economics": {
            "license_class": "OPEN_SOURCE",
            "billing_tier": "TIER_0_FREE",
            "compute_profile": "CPU_BOUND"
        },
        "provenance": {
            "author_id": "meta-engineering-forge",
            "created_at": "2026-04-30T10:00:00Z"
        },
        "validation": {
            "test_coverage_pct": 0,
            "latency_ms": 10,
            "cryptographic_hash": None,
            "formal_guarantees": []
        }
    }
    manifest_file = bundle_dir / "manifest.yaml"
    with open(manifest_file, "w", encoding="utf-8") as f:
        yaml.dump(manifest_data, f, sort_keys=False)

    # 5. Write schema.py
    import_codes = [module.code_for_node(i) for i in extractor.import_nodes]
    class_codes = [module.code_for_node(c) for c in extractor.class_nodes]
    if class_codes:
        schema_code = generate_schema_code(import_codes, class_codes)
        (bundle_dir / "schema.py").write_text(schema_code, encoding="utf-8")

    # 6. Write server.py
    server_code = generate_server_code(func_name, func_code, extractor.class_nodes)
    # Inject correct URN into docstring/annotations by replacing the LLM's hallucinated one
    if extractor.urn_value:
        server_code = server_code.replace(extractor.urn_value, target_urn)
    (bundle_dir / "server.py").write_text(server_code, encoding="utf-8")

    # 7. Cleanup Sandbox
    os.remove(source_path)

    return f"Successfully packaged {func_name} into {bundle_dir} and cleaned up local sandbox."
