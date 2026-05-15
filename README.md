# coreason-meta-engineering (The Agentic Forge)

[![PyPI - Version](https://img.shields.io/pypi/v/coreason-meta-engineering.svg)](https://pypi.org/project/coreason-meta-engineering/)
[![CI](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CoReason-AI/coreason-meta-engineering/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub_Pages-blue.svg)](https://coreason-ai.github.io/coreason-meta-engineering/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/coreason-meta-engineering.svg)](https://pypi.org/project/coreason-meta-engineering/)
[![Downloads](https://img.shields.io/pypi/dm/coreason-meta-engineering.svg)](https://pypi.org/project/coreason-meta-engineering/)
[![License: Prosperity 3.0](https://img.shields.io/badge/License-Prosperity_3.0-blue.svg)](https://prosperitylicense.com/versions/3.0.0)
[![Codecov](https://codecov.io/gh/CoReason-AI/coreason-meta-engineering/branch/main/graph/badge.svg)](https://codecov.io/gh/CoReason-AI/coreason-meta-engineering)
<br>
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Forks](https://img.shields.io/github/forks/CoReason-AI/coreason-meta-engineering.svg)](https://github.com/CoReason-AI/coreason-meta-engineering/network/members)
[![Powered By: AI](https://img.shields.io/badge/Powered%20By-CoReason%20AI-FF4500.svg)](https://coreason.ai)

**The deterministic Agentic Forge & AST Manipulation Layer of the CoReason ecosystem.**

`coreason-meta-engineering` acts as the deterministic mathematical toolchain (EDA) for expanding the CoReason ecosystem. It is an active engineering service that translates agentic intent into rigid, verifiable Python source code via Concrete Syntax Tree (`libcst`) manipulation.

## The Universal Asset Forge
`coreason-meta-engineering` acts as the deterministic mathematical toolchain (EDA) for expanding the CoReason ecosystem. It is an active engineering service rather than a passive library—it strictly parses Python as a Concrete Syntax Tree (`libcst`), rigidly enforces cryptographic URN discovery bounds, and strictly avoids probabilistic AI logic execution when generating code.

For complete architectural rules, agent mandates, and SDK documentation, visit our formal documentation:
**[Read the Docs →](https://CoReason-AI.github.io/coreason-meta-engineering/)**

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
