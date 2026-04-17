# The Tripartite Fabrication Lines

The **Universal Asset Forge** categorizes all capabilities within the CoReason ecosystem into three distinct ontological categories: **Passive Data**, **Active Logic**, and **Autonomous Entities**. 

To physically "etch" these concepts into the Python codebase, the compiler utilizes three highly specialized `libcst` Functors. These Functors traverse the target module's Abstract Syntax Tree (AST), resolve dependencies dynamically, and inject the requested assets.

---

## 1. The Passive Data Fab
**Target Asset:** `State`, `Intent`, `Manifest`, `Receipt`
**Underlying Functor:** `StateInjectionFunctor`
**CLI Command:** `scaffold-manifest-state`

Passive data structures form the "Hollow Data Plane" of the CoReason ecosystem. They define the rigid geometries that active agents operate upon.

### Core Mechanics:
* **JSON Schema Translation:** The Functor ingests a standard JSON Schema (`geometric_schema`) and deterministically parses it into highly bounded Pydantic `Field` definitions. For example, a JSON string definition with a maximum length is mapped to `Annotated[str, StringConstraints(max_length=...)]`.
* **Strict Inheritance Axiom:** Standard `pydantic.BaseModel` inheritance is mathematically forbidden. The Functor forces all new states to inherit from `CoreasonBaseState` (or a registered descendant) to guarantee RFC-8785 canonical hashing.
* **The Sorting Guillotine:** If the JSON Schema defines an array or list, the Functor autonomously generates a `_enforce_canonical_sort` method with a `@model_validator(mode="after")` decorator. This ensures distributed mesh consensus by physically preventing unordered sets.

---

## 2. The Active Logic Fab
**Target Asset:** `Actuator`, `Oracle` (MCP Tools)
**Underlying Functor:** `LogicInjectionFunctor`
**CLI Command:** `scaffold-logic-actuator`

Active logic dictates how agents interact with the external world or perform kinetic compute. In the CoReason ecosystem, all executable functions are bounded by the Model Context Protocol (MCP).

### Core Mechanics:
* **Decorator Injection:** The Functor scaffolds a pure Python `cst.FunctionDef` and injects the mandatory `@mcp.tool()` boundary decorator.
* **Dynamic Import Resolution:** When parsing the input schema, the Functor identifies advanced type requirements. During the `leave_Module` traversal phase, it scans the top of the file. If it detects missing types (e.g., `typing.Any`, `typing.Annotated`, `pydantic.StringConstraints`), it natively builds `cst.ImportFrom` nodes and injects them to prevent `NameError` crashes at runtime.
* **URN Attribute Publishing:** To ensure the Master MCP registry can discover the tool zero-shot, the Functor injects a `__action_space_urn__` assignment immediately following the function definition.

---

## 3. The Autonomous Entity Fab
**Target Asset:** `Epistemic Node`, `Cognitive Entity` (Swarm Agents)
**Underlying Functor:** `EpistemicNodeInjectionFunctor`
**CLI Command:** `scaffold-epistemic-node`

Autonomous entities are the sovereign reasoning engines of the swarm. They require both data bounds and executable authority.

### Core Mechanics:
* **Cognitive Boundary Construction:** The Functor ingests the `cognitive_boundary_directive` (the system prompt) and securely encapsulates it within the class geometry.
* **Pydantic Immutability Bypass:** CoReason agents inherit from frozen states (`ConfigDict(frozen=True)`). Standard list assignments for `authorized_tools` would cause Pydantic to crash with an `Instance is frozen` error. The Functor circumvents this by generating a low-level `object.__setattr__(self, "authorized_tools", sorted(...))` bypass, permitting the initial assignment while preserving immutability thereafter.
* **Epistemic Docstring:** The Functor weaves the required 4-part docstring (`AGENT INSTRUCTION`, `CAUSAL AFFORDANCE`, `EPISTEMIC BOUNDS`, `MCP ROUTING TRIGGERS`) directly into the class AST, preparing the agent for dense-vector retrieval.

---

## Shared Compiler Behaviors

Regardless of which Fab Line is triggered, all Functors share the following zero-trust behaviors:

1. **The Idempotency Guard:** Every Functor scans the AST for its target name before injection. If the class or function already exists, injection is aborted.
2. **Model Rebuilding:** All structural injections trigger a trailing `.model_rebuild()` AST generation to ensure Pydantic forward references resolve deterministically.
3. **URN Semantic Validation:** All Fab Lines are protected by the `validate_action_space_urn` gateway, immediately rejecting any URN that lacks the `urn:coreason:actionspace:` prefix.
