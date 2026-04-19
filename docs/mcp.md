# MCP Server Projection

`coreason-meta-engineering` is air-gapped from `coreason-runtime`. Downstream agents CANNOT import its Python functions directly. Instead, all AST manipulation logic is securely projected over the **Model Context Protocol (MCP)**.

## Launching the Server

The server is implemented using `fastmcp` and can be initialized seamlessly via the CLI. To expose the capability set over stdio for agent interaction, simply run:

```bash
uv run coreason-meta-mcp
```

## Available Tool Projections

The MCP server exposes three strict tools for generating different classifications of assets. Each asset explicitly requires an `action_space_id` conforming to the URN constraints.

### 1. `scaffold_manifest_state`
Used to deterministically inject passive state models into the AST map. 
It requires:
- `state_name`: The class name of the Pydantic state model.
- `geometric_schema`: The raw JSON defining the fields.
- `target_file_path`: Path to the module to mutate.
- `action_space_id`: Uniquely identifiable cryptographic URN.

### 2. `scaffold_logic_actuator`
Used to instantiate an execution function within the runtime domain.
- `actuator_name`: The runtime function to forge.
- `geometric_schema`: The JSON schema defining function parameters.
- `target_file_path`: The module to perform AST node insertion in.
- `action_space_id`: Execution URN boundary mapping.

### 3. `scaffold_epistemic_node`
Used to engineer new Swarm Agent entities constrained to specific cognitive boundaries.
- `node_name`: Name of the Agent Class.
- `cognitive_boundary_directive`: Text defining the bounding epistemic policy.
- `target_file_path`: Output file.
- `action_space_id`: Routing URN to intercept payloads.
