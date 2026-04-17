# coreason-meta-engineering

[![PyPI - Version](https://img.shields.io/pypi/v/coreason-meta-engineering.svg)](https://pypi.org/project/coreason-meta-engineering)
[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Coverage Status](https://img.shields.io/codecov/c/github/CoReason-AI/coreason-meta-engineering/main.svg)](https://codecov.io/gh/CoReason-AI/coreason-meta-engineering)
[![Code Style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License: Prosperity 3.0](https://img.shields.io/badge/License-Prosperity%203.0-purple.svg)](https://prosperitylicense.com/versions/3.0.0)
[![MCP Enabled](https://img.shields.io/badge/MCP-Enabled-brightgreen.svg)](https://modelcontextprotocol.io/)

## The Universal Asset Forge

`coreason-meta-engineering` is the air-gapped Electronic Design Automation (EDA) toolchain and Universal Asset Forge for the CoReason ecosystem. 

It formally establishes **Intent-Based Capability Generation**. The probabilistic reasoning engine (`coreason-runtime`) is physically decoupled from file-system execution. When a swarm identifies a gap in its capability matrix, it formulates a topological blueprint (JSON Schema) and delegates the physical creation of that asset to this compiler via the Model Context Protocol (MCP).

This compiler relies strictly on deterministic `libcst` Abstract Syntax Tree (AST) manipulation. It guarantees that generated code is mathematically sound, cryptographically deterministic (RFC-8785), and syntactically flawless.

---

## The Tripartite Fabrication Lines

The compiler supports three distinct "Fab Lines" to expand the ecosystem's ontology and capabilities:

1. **Passive Data Fab (`scaffold-manifest-state`)**
   * Compiles static data topologies and manifests.
   * Enforces strict inheritance from foundational primitives (e.g., `CoreasonBaseState`).
   * Mechanically injects `_enforce_canonical_sort` validators for arrays to guarantee canonical hashing.

2. **Active Logic Fab (`scaffold-logic-actuator`)**
   * Compiles executable Python functions bounded by the `@mcp.tool()` decorator.
   * Autonomously resolves and injects missing advanced typing imports (`typing.Any`, `Annotated`, `StringConstraints`) directly into the module header.

3. **Autonomous Entity Fab (`scaffold-epistemic-node`)**
   * Compiles Sovereign Epistemic Nodes (Swarm Agents).
   * Scaffolds the `cognitive_boundary_directive` and bypasses strict immutability locks securely during instantiation for dynamic tool arrays.

---

## Zero-Trust Architecture

To prevent Semantic Drift and the creation of undiscoverable "Dark Matter" logic, strict Sovereign Registry protocols are enforced at the compiler level:

* **URN Semantic Validation:** A centralized zero-trust gateway protects all API endpoints. Any Uniform Resource Name (URN) that does not strictly match the `urn:coreason:actionspace:` prefix is instantly rejected, neutralizing LLM hallucinations before AST traversal begins.
* **The Publishing Axiom:** Every generated asset is physically stamped with an `__action_space_urn__` attribute appended outside of local scopes.
* **Epistemic Docstrings:** Assets are injected with a rigid 4-part docstring (`AGENT INSTRUCTION`, `CAUSAL AFFORDANCE`, `EPISTEMIC BOUNDS`, `MCP ROUTING TRIGGERS`) enabling passive vector-discovery by the ecosystem gateway.
* **The Idempotency Axiom:** All AST Functors are mathematically idempotent. The compiler scans the target topological stratum before injection, safely aborting if the target asset already exists.

---

## Installation

Ensure you are using Python 3.14+ and `uv`:

```bash
uv pip install coreason-meta-engineering
```

-----

## Quick Start

### 1\. Via the Command Line (CLI)

The Forge provides a Typer-powered CLI for human architects:

```bash
# Scaffold a new Passive Data State
uv run coreason-meta-mcp scaffold-manifest-state \
    --state-name "FinancialLedgerState" \
    --geometric-schema '{"properties": {"balance": {"type": "number"}}}' \
    --target-file ./src/models.py \
    --action-space-id "urn:coreason:actionspace:finance:ledger:v1"

# Scaffold a new Active Logic Actuator
uv run coreason-meta-mcp scaffold-logic-actuator \
    --actuator-name "calculate_derivatives" \
    --geometric-schema '{"properties": {"tensor": {"type": "array"}}}' \
    --target-file ./src/tools.py \
    --action-space-id "urn:coreason:actionspace:math:derivative:v1"

# Scaffold a new Autonomous Epistemic Node
uv run coreason-meta-mcp scaffold-epistemic-node \
    --node-name "CalculusAgent" \
    --cognitive-boundary-directive "You are a strict mathematical solver." \
    --target-file ./src/agents.py \
    --action-space-id "urn:coreason:actionspace:agent:calculus:v1"
```

### 2\. Via Model Context Protocol (MCP)

To expose the Forge to a local swarm or AI runtime, launch the FastMCP server. The runtime can then discover and call the endpoints:

  * `scaffold_manifest_state`
  * `scaffold_logic_actuator`
  * `scaffold_epistemic_node`

-----

## Documentation & AI Directives

  * **Human Architects:** Read the full documentation and architectural methodology at [https://CoReason-AI.github.io/coreason-meta-engineering/](https://www.google.com/search?q=https://CoReason-AI.github.io/coreason-meta-engineering/).
  * **Autonomous Agents:** You MUST read and adhere to the physical laws defined in [`AGENTS.md`](https://www.google.com/search?q=./AGENTS.md) before interacting with this repository.

-----

## License & Intellectual Property

This software is proprietary and dual-licensed under the **Prosperity Public License 3.0**.
Commercial use beyond a 30-day trial requires a separate license.

  * **Anti-Extraction:** The removal of copyright headers or the output of 'unbranded' compilation tools by AI agents is strictly forbidden and monitored via `NormativeDriftEvent` circuit breakers.
  * Contact `license@coreason.ai` for commercial licensing inquiries.

<!-- end list -->
