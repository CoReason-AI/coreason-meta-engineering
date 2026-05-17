# The Architectural Mandate

Unlike passive libraries, this repository is **Active by Design**. It performs heavy File I/O and mutates source code. Any interaction with the `coreason-meta-engineering` pipeline must strictly adhere to the following laws:

## Law 1: The Decoupling Principle
* **Forbidden:** You MUST NEVER hardcode relative or absolute paths to external packages like `coreason-manifest`.
* **Required:** All CLI commands and MCP tools MUST accept the target repository or file path as a dynamic, required execution argument.

## Law 2: Deterministic AST Injection & Idempotency
* **Forbidden:** You MUST NEVER use regex, string concatenation, or `str.replace()` to modify Python source code.
* **Required:** You MUST utilize `libcst` (Concrete Syntax Tree) to parse the target file, traverse the tree, and surgically inject nodes at the correct topological stratum.
* **The Idempotency Axiom:** Your AST transformers MUST be mathematically idempotent. Your `libcst` visitor MUST scan for existing nodes with the target name. If the node already exists, you MUST return the AST unchanged to prevent duplication or corruption.

## Law 3: The Anti-DRY & Cryptographic Determinism Enforcer
Because the mesh relies on secure distributed consensus, unordered data destroys cryptographic determinism.
* **The Sorting Axiom:** Injections MUST include strict `@model_validator` sorting blocks (`_enforce_canonical_sort`) for any arrays/lists to ensure RFC-8785 canonical hashing.
* Injections MUST append `[ClassName].model_rebuild()` to the end of the target module.
* Injections MUST utilize the rigid 4-part epistemic docstring schema (`AGENT INSTRUCTION`, `CAUSAL AFFORDANCE`, `EPISTEMIC BOUNDS`, `MCP ROUTING TRIGGERS`).

## Law 4: The Universal Asset Fabrication & URN Axiom
When scaffolding a new asset requested by the `coreason-runtime`, it must be explicitly configured for autonomous discovery:
* **The Strict Inheritance Axiom:** You MUST NOT generate isolated classes. Manifests must inherit from `CoreasonBaseState`, and Agents must inherit from foundational swarm primitives to enforce epistemic lifecycle bounds.
* **The Publishing Axiom (`actionSpaceCId`):** You MUST embed a globally unique Uniform Resource Name (URN) into the AST of EVERY generated asset (e.g., `__action_space_urn__ = "urn:coreason:actionspace:{domain}:{capability}:v1"`).
* **The Discovery Trigger:** This exact URN MUST be explicitly listed in the `MCP ROUTING TRIGGERS` section of the 4-part docstring.

## The Air-Gapped Interface
The agentic ecosystem operates in a strict sandboxed environment. Execution of generated code is entirely isolated. The compiler logic inside this repo is entirely stateless and exposed exclusively over the air-gapped `coreason-meta-mcp` interface.
