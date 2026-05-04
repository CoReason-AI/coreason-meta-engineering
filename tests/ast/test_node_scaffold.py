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

from coreason_meta_engineering.ast.node_scaffold import EpistemicNodeInjectionFunctor


def test_agent_inject_transformer_basic() -> None:
    source = "class ExistingAgent:\n    pass\n"
    module = cst.parse_module(source)
    transformer = EpistemicNodeInjectionFunctor(
        node_name="MyNewAgent",
        cognitive_boundary_directive="This is a test agent.",
        action_space_id="urn:coreason:actionspace:node:agent:v1",
        base_class="CoreasonBaseAgent",
    )
    new_module = module.visit(transformer)
    code = new_module.code
    print("CODE OUTPUT:")
    print(code)

    assert "class MyNewAgent(CoreasonBaseAgent):" in code
    assert '__action_space_urn__ = "urn:coreason:actionspace:node:agent:v1"' in code
    assert 'system_prompt: str = """This is a test agent."""' in code
    assert "authorized_tools: list[Any] = []" in code
    assert "from typing import Any, Self" in code
    assert "from pydantic import model_validator" in code
    assert "def _enforce_canonical_sort(self) -> Self:" in code
    assert 'object.__setattr__(self, "authorized_tools", sorted(self.authorized_tools))' in code
    assert '@model_validator(mode = "after")' in code
    assert "MCP ROUTING TRIGGERS: urn:coreason:actionspace:node:agent:v1" in code
    assert "MyNewAgent.model_rebuild()" in code


def test_agent_inject_transformer_idempotency() -> None:
    source = "class MyNewAgent:\n    pass\n"
    module = cst.parse_module(source)
    transformer = EpistemicNodeInjectionFunctor(
        node_name="MyNewAgent",
        cognitive_boundary_directive="Test",
        action_space_id="urn:val",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    assert code.count("class MyNewAgent") == 1
    assert "system_prompt" not in code


def test_agent_inject_existing_import() -> None:
    source = "from typing import Any, Self\nfrom pydantic import model_validator\n"
    module = cst.parse_module(source)
    transformer = EpistemicNodeInjectionFunctor(
        node_name="MyNewAgent",
        cognitive_boundary_directive="Test",
        action_space_id="urn:val",
    )
    new_module = module.visit(transformer)
    code = new_module.code

    assert code.count("from typing import Any, Self") == 1
    assert code.count("from pydantic import model_validator") == 1
