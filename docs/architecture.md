# Architecture & Physical Laws

Unlike traditional code generators that rely on string templates (like Jinja) or Large Language Model (LLM) probabilistic output, the **Universal Asset Forge** operates as a mathematically rigid, structure-preserving Functor. 

To guarantee that the CoReason ecosystem remains deterministically stable, the `coreason-meta-engineering` compiler strictly adheres to four foundational architectural laws.

---

## 1. The AST Manifold (Strict LibCST Manipulation)

Treating Python source code as flat text is a critical vulnerability in autonomous systems. Regex replacements and f-string concatenations are brittle and prone to syntax fracturing when manipulated by non-deterministic LLMs.

**The Law:** The Forge treats all target Python files exclusively as a mutable mathematical graph—specifically, a **Concrete Syntax Tree (CST)**.

* **Mechanics:** The compiler utilizes `libcst` to parse the target file into a full fidelity tree, preserving all whitespace and comments. 
* **Injection:** When a swarm requests a new asset (like a new `CoreasonBaseState`), the compiler constructs pure `cst.ClassDef`, `cst.FunctionDef`, or `cst.Assign` nodes and surgically inserts them at the correct topological stratum within the module's `body`.
* **Zero String Manipulation:** `str.replace()` and regex are physically banned from the injection pathways.

## 2. The Idempotency Axiom

In a decentralized swarm, multiple agents might attempt to resolve the same epistemic deficit simultaneously, leading to race conditions or duplicate tool generation.

**The Law:** Every AST Functor (fabrication line) must be mathematically idempotent. 

* **Mechanics:** During the `leave_Module` traversal phase, the compiler actively scans the existing abstract syntax tree for the requested asset name (e.g., `scaffold_logic_actuator` scanning for a `cst.FunctionDef` matching `tool_name`).
* **Execution:** If the asset already exists in the graph, the compiler instantly halts the injection and returns the AST completely unchanged. `f(f(x)) = f(x)`. This mechanically prevents code duplication and namespace corruption.

## 3. Cryptographic Determinism (The Sorting Axiom)

The CoReason ecosystem relies on a distributed Merkle-DAG to maintain the Epistemic Ledger. For distributed consensus to function, equivalent data structures must produce the exact same SHA-256 hash across different operating systems and memory states.

**The Law:** The compiler must physically enforce **RFC-8785 Canonical JSON Serialization** rules on all generated passive data structures.

* **Mechanics:** Unordered arrays destroy cryptographic determinism. If an agent requests a state model containing a `list`, the Forge autonomously generates and injects a `_enforce_canonical_sort` method.
* **Pydantic Immutability:** Because CoReason states use `ConfigDict(frozen=True)`, standard assignment fails. The compiler safely bypasses this during instantiation by generating low-level `object.__setattr__` assignments mapped to Pydantic `@model_validator(mode="after")` decorators.
* **Model Rebuilding:** Every class injection automatically appends a `[ClassName].model_rebuild()` call to the end of the module to resolve forward references deterministically.

## 4. The Decoupling Principle

To remain a Universal Forge, the compiler must never assume the shape or location of the deployment environment. 

**The Law:** Zero hardcoded paths. The compiler must act purely as an air-gapped execution engine.

* **Mechanics:** `coreason-meta-engineering` has no hardcoded references to `coreason-manifest`, `coreason-runtime`, or `coreason-ecosystem`. 
* **Execution:** The target repository or file path (`target_file_path`) is a mandatory, dynamic argument passed via the Typer CLI or the Model Context Protocol (MCP) server. The orchestrator providing the intent must also provide the coordinate.
