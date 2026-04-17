# Welcome to the Universal Asset Forge

**`coreason-meta-engineering`** is the air-gapped Electronic Design Automation (EDA) toolchain and Universal Asset Forge for the CoReason ecosystem. 

It is designed to solve one of the most critical vulnerabilities in autonomous, multi-agent systems: the unsafe, probabilistic generation of executable code.

---

## The Problem: The Neurosymbolic Chasm

Large Language Models (LLMs) are probabilistic, high-entropy reasoning engines operating in continuous vector spaces. Secure, verifiable software systems operate in discrete, deterministic, topological spaces.

Bridging this "Neurosymbolic Chasm" using standard text generation is catastrophic. If an autonomous agent is granted the ability to use standard `fs.write()` or `open(..., 'w')` to generate its own tools or capabilities, the system inevitably suffers from:
1. **Syntax Fracturing:** Hallucinated indentation, missing imports, and broken Python syntax.
2. **Cryptographic Corruption:** Unordered arrays and missing validation blocks that destroy RFC-8785 canonical hashing.
3. **Semantic Drift:** The creation of overlapping, poorly named tools that pollute the context window.

## The Solution: Intent-Based Capability Generation

To solve this, the CoReason architecture strictly enforces **Intent-Based Capability Generation**. 

The probabilistic reasoning engine (`coreason-runtime`) is physically decoupled from file-system execution. When a swarm identifies a gap in its capability matrix, it is mathematically forbidden from writing the Python file itself. Instead, it formulates a structured topological blueprint (a JSON Schema) and projects it over an air-gapped Model Context Protocol (MCP) boundary to this compiler.

`coreason-meta-engineering` acts as a **Structure-Preserving Functor**. It treats Python source code strictly as a mutable mathematical graph (Concrete Syntax Tree via `libcst`), never as flat text. It deterministically "etches" the requested logic into the repository, perfectly applying necessary boilerplate, zero-trust constraints, and cryptographic proofs of order.

---

## The Tripartite Fabrication Lines

The Forge translates dynamic AI intent into the strict, immutable vocabulary of the platform through three specialized AST Functors:

### 1. Passive Data Fab (`scaffold_manifest_state`)
**Target:** Declarative Geometries and Epistemic Ledgers.
* Ensures all new data structures strictly inherit from `CoreasonBaseState`.
* Mechanically injects `_enforce_canonical_sort` validators to guarantee distributed mesh consensus.

### 2. Active Logic Fab (`scaffold_logic_actuator`)
**Target:** Kinetic Execution endpoints exposed over the mesh.
* Bounds executable Python functions with the `@mcp.tool()` decorator.
* Autonomously resolves and injects missing advanced typing imports (`typing.Any`, `Annotated`, `StringConstraints`) directly into the module's Abstract Syntax Tree.

### 3. Autonomous Entity Fab (`scaffold_epistemic_node`)
**Target:** Sovereign Epistemic Nodes (Swarm Agents).
* Scaffolds the `cognitive_boundary_directive` system prompts.
* Safely bypasses Pydantic immutability (`frozen=True`) during instantiation using low-level `object.__setattr__` generation for dynamic tool arrays.

---

## Navigating this Documentation

This documentation site is designed for both **Human Architects** and **Autonomous Agents**:

* **[Architecture & Mechanics](architecture.md):** Deep dive into the physical laws of the compiler, including the Idempotency and Sorting Axioms.
* **[Fabrication Lines](fabrication_lines.md):** Detailed breakdowns of the three `libcst` Functors.
* **[Security & Zero-Trust](security_and_zero_trust.md):** How the compiler utilizes URN Semantic Validation and Epistemic Docstrings to prevent capability "Dark Matter."
* **[AI Directives](agents.md):** The machine-readable `AGENTS.md` file dictating the physical laws LLMs must obey when operating within this repository.
