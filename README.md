# coreason-meta-engineering

The Agentic Forge & AST Manipulation Layer

[![CI](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/ci.yml)
[![Publish](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/publish.yml/badge.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/publish.yml)
[![Security](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/security.yml/badge.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/security.yml)
[![PyPI](https://img.shields.io/pypi/v/coreason-meta-engineering.svg)](https://pypi.org/project/coreason-meta-engineering/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/coreason-meta-engineering.svg)](https://pypi.org/project/coreason-meta-engineering/)
[![License: Prosperity 3.0](https://img.shields.io/badge/License-Prosperity_3.0-blue.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/blob/main/LICENSE)
[![Codecov](https://codecov.io/gh/CoReason-AI/coreason-meta-engineering/branch/main/graph/badge.svg)](https://codecov.io/gh/CoReason-AI/coreason-meta-engineering)
[![Downloads](https://img.shields.io/pypi/dm/coreason-meta-engineering.svg)](https://pypi.org/project/coreason-meta-engineering/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub Stars](https://img.shields.io/github/stars/CoReason-AI/coreason-meta-engineering.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/CoReason-AI/coreason-meta-engineering.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/issues)
[![GitHub PRs](https://img.shields.io/github/issues-pr/CoReason-AI/coreason-meta-engineering.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/pulls)

## The Universal Asset Forge
`coreason-meta-engineering` acts as the deterministic mathematical toolchain (EDA) for expanding the CoReason ecosystem. It is an active engineering service rather than a passive library—it strictly parses Python as a Concrete Syntax Tree (`libcst`), rigidly enforces cryptographic URN discovery bounds, and strictly avoids probabilistic AI logic execution when generating code.

For complete architectural rules, agent mandates, and SDK documentation, visit our formal documentation:
**[Read the Docs →](https://CoReason-AI.github.io/coreason_meta_engineering/)**

## Getting Started

### Prerequisites

- Python 3.14+
- uv

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/CoReason-AI/coreason-meta-engineering.git
    cd coreason-meta-engineering
    ```
2.  Install dependencies:
    ```sh
    uv sync --all-extras --dev
    ```

### Usage

-   Run the linter:
    ```sh
    uv run pre-commit run --all-files
    ```
-   Run the tests:
    ```sh
    uv run pytest
    ```
