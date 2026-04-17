# Development & Contributor Guide

Welcome, Human Architect. 

Modifying `coreason-meta-engineering` requires extreme rigor. Because this repository acts as the **Universal Asset Forge**, a single bug in an AST Functor will autonomously propagate syntax errors across the entire CoReason ecosystem.

To prevent cascading failures, all development within this repository is governed by strict verification gates.

---

## 1. The 100% Coverage Floor

Because we are generating code via `libcst` manipulation, uncovered logic is considered a critical vulnerability.

**The Law:** You MUST maintain exactly **100.00% statement and branch coverage**. 

If you add a new conditional branch to an AST Functor (e.g., handling an `Optional` field or a specific `pydantic` constraint), you must write a corresponding unit test that triggers that exact branch. The CI/CD pipeline (`codecov`) will fail your pull request if coverage drops to 99.9%.

## 2. Testing AST Functors (Targeted Mocking)

When writing tests for new Functors in `tests/ast/`, you must adhere to the **Atomic Implementation** principle.

* **Forbidden:** You must never test AST generation by mutating actual physical `.py` files on disk.
* **Required:** Pass raw strings of Python code into the `libcst` parser, apply your transformer, and assert against the resulting string.

**Example Test Pattern:**
```python
import libcst as cst
from coreason_meta_engineering.ast.state_scaffold import StateInjectionFunctor

def test_state_injection_idempotency() -> None:
    # 1. Define the mock initial state as a string
    source = "class ExistingState:\n    pass\n"
    module = cst.parse_module(source)
    
    # 2. Instantiate your Functor
    functor = StateInjectionFunctor(
        state_name="ExistingState", 
        geometric_schema={}, 
        action_space_id="urn:test"
    )
    
    # 3. Visit the tree
    modified_module = module.visit(functor)
    
    # 4. Assert the result (Idempotency should leave it unchanged)
    assert modified_module.code.count("class ExistingState") == 1
```

## 3. Pre-Flight Verification Gates

Before committing code or opening a Pull Request, you must execute the local validation pipeline. The ecosystem utilizes `uv` as the primary package manager.

Run the following commands from the root directory:

### Formatting & Linting
Ensure all code complies with the strict `ruff` configuration.
```bash
uv run ruff format .
uv run ruff check . --fix
```

### Strict Typing
We rely heavily on precise type definitions for `libcst` nodes. `Any` is generally forbidden in AST logic.
```bash
uv run mypy . --strict
```

### Coverage Audit
Verify your test coverage locally before pushing.
```bash
uv run pytest --cov
```

## 4. Adding a New Fabrication Line

If the CoReason ecosystem requires a fundamentally new ontological asset (e.g., a new type of execution environment or specialized orchestrator), you must build a new Fabrication Line.

Follow this exact order of operations:
1. **Build the Functor:** Create `src/coreason_meta_engineering/ast/[asset]_scaffold.py` extending `cst.CSTTransformer`.
2. **Write the Tests:** Create `tests/ast/test_[asset]_scaffold.py` and achieve 100% coverage on the Functor alone.
3. **Expose the CLI:** Add a new `@app.command()` in `main.py` utilizing the `validate_action_space_urn` guard.
4. **Expose the MCP Endpoint:** Add a new `@mcp.tool()` endpoint in `mcp_server.py`.
5. **Update Tests:** Update `test_main.py` and `test_mcp_server.py` to cover the new routing endpoints.
