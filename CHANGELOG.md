# Changelog

## [0.7.4](https://github.com/CoReason-AI/coreason-meta-engineering/compare/v0.7.3...v0.7.4) (2026-05-13)


### Features

* add kinetic_guillotine utility for resource management ([d35207d](https://github.com/CoReason-AI/coreason-meta-engineering/commit/d35207d96917173300ceac862d438879789dad40))
* **chaos-mesh:** introduce Kubernetes CRD scaffold functor ([d2ef9a0](https://github.com/CoReason-AI/coreason-meta-engineering/commit/d2ef9a0c0d487ba4c9d629eec8a8d3ef80b97be4))
* implement automated release and documentation deployment workflow and update version manifestation ([91eb9df](https://github.com/CoReason-AI/coreason-meta-engineering/commit/91eb9dfff2ef310e8dea44d912472f5beb883cd0))
* implement kinetic_guillotine utility for managing task termination processes ([8ec095e](https://github.com/CoReason-AI/coreason-meta-engineering/commit/8ec095ec8b0e03841cb042c93830df13e3b0224a))
* implement mcp server and pvv verification pipeline with upgraded dependency versions ([2e26731](https://github.com/CoReason-AI/coreason-meta-engineering/commit/2e26731e3d0165e8038a7ec3e9a9565dfc712cfc))
* implement meta-engineering schema, LibCST-based node scaffolding, and agent injection utilities ([123d709](https://github.com/CoReason-AI/coreason-meta-engineering/commit/123d70974a529979d48f360aafb3ad91a8fe71d5))
* implement scaffolding CLI for epistemic nodes, states, and logic actuators with cryptographic licensing support ([13fc768](https://github.com/CoReason-AI/coreason-meta-engineering/commit/13fc768e248689d48920df7f7ca84a1607a2b39c))
* integrate kinetic-guillotine compliance scanning into scaffolding workflow ([17192f2](https://github.com/CoReason-AI/coreason-meta-engineering/commit/17192f27e5e5ca82b04926a76001c6a0a856be0b))
* introduce node scaffolding utilities and licensing header management tools ([de6a83d](https://github.com/CoReason-AI/coreason-meta-engineering/commit/de6a83d96e28569a9984ea98e018709812295964))


### Bug Fixes

* add mypy type annotations to all test functions for CI compliance ([8577907](https://github.com/CoReason-AI/coreason-meta-engineering/commit/8577907ff77c61d24f123ff1a9aef5b9c77b85cc))
* **ci:** allow prereleases in pyproject.toml and upgrade dependencies to resolve CI test failures ([03ee4f3](https://github.com/CoReason-AI/coreason-meta-engineering/commit/03ee4f301eedf56e32c584376c7d74f828901643))
* **ci:** fetch workspace dependencies directly to resolve test failures ([46839b0](https://github.com/CoReason-AI/coreason-meta-engineering/commit/46839b03c2970f53e2c9845563f11e4190eb27a6))
* **ci:** format python files to pass ruff linting ([b62d1e1](https://github.com/CoReason-AI/coreason-meta-engineering/commit/b62d1e1e977838efbffdb97fb9fb557bdb653f2e))
* **ci:** ignore missing imports for coreason_urn_authority in mypy config ([6eebbcb](https://github.com/CoReason-AI/coreason-meta-engineering/commit/6eebbcb45d3ef67844984d19749a40c8e6782786))
* **ci:** ignore transitive dependency coreason_manifest for deptry ([0671e18](https://github.com/CoReason-AI/coreason-meta-engineering/commit/0671e1827497bb2e59c31ca74bfb955dd9d540db))
* **ci:** pin sigstore action to commit hash for security ([3c502e0](https://github.com/CoReason-AI/coreason-meta-engineering/commit/3c502e0ca845b03d2ef6e13d33f1ab4aa497667f))
* resolve formatting and dependabot vulnerabilities for PR 53 ([ea8c5b0](https://github.com/CoReason-AI/coreason-meta-engineering/commit/ea8c5b0fb04a29aac439b7c92872c6231194581d))
* resolve linting errors in meta-engineering ([2f2888a](https://github.com/CoReason-AI/coreason-meta-engineering/commit/2f2888ab1c6f1bf195945a112cb12a7f25131f4c))
* revert timeout param rename in congruence mock — caller passes it as keyword arg ([cdb7475](https://github.com/CoReason-AI/coreason-meta-engineering/commit/cdb74758e71cefca7e93054122e5d6c6082ef8e5))


### CI/CD

* exclude macOS 3.14t from extended tests — tokenizers Rust crate lacks cpython-314t-darwin wheel ([a9cfd6f](https://github.com/CoReason-AI/coreason-meta-engineering/commit/a9cfd6ff79d679b223f399c68d19265d61510d99))
* fix release-please action and target branch ([1780d02](https://github.com/CoReason-AI/coreason-meta-engineering/commit/1780d0261253f3024df30838827e60212663b8bd))
* fix release-please workflow and add missing config-file ([549328a](https://github.com/CoReason-AI/coreason-meta-engineering/commit/549328a0cd4d8b18b54c360a7baad7d5dc9ebb22))


### Tests

* add 100% coverage for kubernetes crd scaffold ([f6c9268](https://github.com/CoReason-AI/coreason-meta-engineering/commit/f6c9268bf93dbdc80390431df21498ab876cde26))
* add comprehensive test suite for AST operations, congruence evaluation, and kinetic guillotine security scans ([1fa8848](https://github.com/CoReason-AI/coreason-meta-engineering/commit/1fa884810cf53b7c8adbaa0456256751d44e62b3))
* add comprehensive unit tests for node scaffolds, compliance scanning, and publish command workflows ([aa91025](https://github.com/CoReason-AI/coreason-meta-engineering/commit/aa910251d53d493d10823015dec2179f0b9e44ae))
* add unit tests for congruence evaluation and semantic topological validation utilities ([de408a3](https://github.com/CoReason-AI/coreason-meta-engineering/commit/de408a3529979d5796d5c32fdaa741af079356ce))
