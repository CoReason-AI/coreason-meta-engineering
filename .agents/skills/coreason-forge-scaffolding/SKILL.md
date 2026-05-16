---
name: coreason-forge-scaffolding
description: "Use this skill to interactively scaffold and etch Pydantic ASTs into the CoReason Manifest using the deterministic coreason-meta-engineering Forge."
---

# Coreason Forge Scaffolding

This skill allows Pi to seamlessly interface with the `coreason-meta-engineering` AST Forge. As an agent, you must strictly follow the "Borrow vs. Build" and "Zero-Waste Engineering" mandates. You cannot write Python files manually using `echo` or `cat`. You MUST use the official MCP toolchain exposed by the Forge.

## Usage Instructions

1. **Identify Epistemic Deficit**: When the user requests a new URN, Schema, or Capability, formalize their intent.
2. **Retrieve Schema Bounds**: Fetch the current `coreason-manifest` schema for the target object.
3. **Execute Scaffold**: Use the `scaffold_manifest_state` or `scaffold_logic_actuator` commands (via MCP) to deterministically generate the AST differential. Do NOT generate the file manually.
4. **Publish URN**: Ensure the output includes the globally unique `__action_space_urn__` required by the `coreason-urn-authority`.

## Constraints

- **DO NOT** use `open()`, `fs.write()`, or standard terminal commands to output Python code.
- **DO NOT** mock tests.
- Ensure the URN string matches the exact CoReason ontology standard: `urn:coreason:actionspace:{category}:{capability}:v1`.
