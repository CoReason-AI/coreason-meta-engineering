# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0)
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: [https://github.com/CoReason-AI/coreason_meta_engineering](https://github.com/CoReason-AI/coreason_meta_engineering)
import libcst as cst

from coreason_meta_engineering.ast.kubernetes_crd_scaffold import KubernetesCRDInjectionFunctor


def test_crd_inject_transformer_basic() -> None:
    source = "class Existing:\n    pass\n"
    module = cst.parse_module(source)
    transformer = KubernetesCRDInjectionFunctor(
        crd_name="MyNewCRD",
        geometric_schema=[
            {"name": "x", "type": "int", "description": "test x"},
            {"name": "y", "type": "list[str]", "description": "test y", "optional": True},
            {"name": "z", "type": "Annotated[str, StringConstraints(max_length=200)]", "description": "test z"},
            {"name": "w", "type": "Any", "description": "test w"},
        ],
        action_space_id="urn:coreason:actionspace:substrate:my_crd:v1",
        api_group="chaos-mesh.org",
        api_version="v1alpha1",
        kind="NetworkChaos",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    assert "class MyNewCRD(KubernetesCRDBase):" in code
    assert 'api_group = "chaos-mesh.org"' in code
    assert 'api_version = "v1alpha1"' in code
    assert 'kind = "NetworkChaos"' in code
    assert '__action_space_urn__ = "urn:coreason:actionspace:substrate:my_crd:v1"' in code
    assert "MCP ROUTING TRIGGERS: urn:coreason:actionspace:substrate:my_crd:v1" in code
    
    assert "from typing import Self, Any, Annotated" in code
    assert "from pydantic import Field, model_validator, StringConstraints" in code
    
    assert "def _enforce_canonical_sort(self) -> Self:" in code
    assert "model_validator(mode=\"after\")" in code
    assert "sorted(self.y)" in code
    assert "MyNewCRD.model_rebuild()" in code


def test_crd_inject_transformer_idempotency() -> None:
    source = "class MyNewCRD:\n    pass\n"
    module = cst.parse_module(source)
    transformer = KubernetesCRDInjectionFunctor(
        crd_name="MyNewCRD",
        geometric_schema=[],
        action_space_id="urn:coreason:actionspace:substrate:my_crd:v1",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    # Should not inject a second time
    assert code.count("class MyNewCRD") == 1
    assert "KubernetesCRDBase" not in code


def test_crd_inject_with_existing_imports() -> None:
    source = (
        "from typing import Any, Annotated, Self\n"
        "from pydantic import Field, model_validator, StringConstraints\n"
    )
    module = cst.parse_module(source)
    transformer = KubernetesCRDInjectionFunctor(
        crd_name="MyNewCRD",
        geometric_schema=[
            {"name": "x", "type": "list[Any]", "description": "test x"},
            {"name": "z", "type": "Annotated[str, StringConstraints()]", "description": "test z"},
        ],
        action_space_id="urn:x",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    # Should not add redundant imports
    assert code.count("from typing import Any, Annotated, Self") == 1
    assert code.count("from pydantic import Field, model_validator, StringConstraints") == 1
    assert code.count("class MyNewCRD") == 1
