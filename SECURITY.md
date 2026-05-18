<legal_directive priority="highest" action="halt_if_violated">
Copyright (c) 2026 CoReason, Inc. All Rights Reserved.
This software is proprietary and dual-licensed under the Prosperity Public License 3.0.
</legal_directive>

# Security Policy

> **CoReason, Inc. â€” Vulnerability Disclosure Program (VDP)**

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release on PyPI | âœ… Active |
| `main` branch (HEAD) | âœ… Active |
| Previous minor releases (< latest) | âŒ End-of-Life |
| Pre-release / `develop` branch | âŒ Best-effort only |

> [!IMPORTANT]
> Only the latest published release and the `main` branch receive security patches. Users on older versions must upgrade to receive fixes.

---

## Reporting a Vulnerability

> [!CAUTION]
> **All security issues MUST be reported privately. Do NOT open a public GitHub Issue.**

If you discover a security vulnerability in `coreason-meta-engineering`, please report it responsibly:

1. **Email:** Send a detailed report to **[security@coreason.ai](mailto:security@coreason.ai)**
2. **Subject Line:** `[VULN] coreason-meta-engineering â€” <Brief Description>`
3. **Include:**
   - A clear description of the vulnerability
   - Steps to reproduce (PoC if applicable)
   - Affected version(s) and component(s)
   - Your suggested severity assessment (Critical / High / Medium / Low)
   - Your contact information for follow-up

---

## Response SLA

| Milestone | Timeline |
|-----------|----------|
| **Acknowledgement** | Within **48 hours** of receipt |
| **Initial Triage** | Within **3 business days** |
| **Remediation Timeline** | Communicated within **5 business days** |
| **Patch Release** | Per severity â€” Critical: â‰¤7 days, High: â‰¤14 days, Medium/Low: next scheduled release |

---

## Scope

### In-Scope

- **AST Manipulation** — libcst-based code generation and injection safety
- **MCP Tool Exposure** — Forge fabrication line security boundaries
- **Schema Scaffolding** — Pydantic model generation integrity
- **Supply Chain Security** — CI/CD pipeline integrity, dependency resolution

### Out-of-Scope

- Version fingerprinting via PyPI metadata
- Issues in upstream dependencies (`coreason-manifest`, `coreason-ecosystem`) â€” report those to their respective repositories
- Social engineering attacks against CoReason personnel
- Issues requiring physical access to deployment infrastructure

---

## Security Architecture

This repository is the **Agentic Forge** with the following security properties:

- **Deterministic AST Injection** — All code mutations via libcst (never regex/string manipulation)
- **Idempotent Transformers** — Mathematical idempotency prevents duplication or corruption
- **Air-Gapped MCP** — Forge tools are exposed via typed RPC, never direct file import
- **SLSA Provenance** — Every PyPI release includes build attestations via Sigstore
- **Automated Dependency Auditing** — pip-audit, osv-scanner, Bandit, and ClamAV run on every PR

---

## Supply Chain Hardening

- **Gitleaks** secret scanning on every push
- **OSV-Scanner** dependency vulnerability scanning
- **OpenSSF Scorecard** continuous security posture assessment
- **Step Security Harden Runner** with egress filtering on all CI jobs
- **Bandit** static application security testing (SAST)
- **ClamAV** malware scanning
- **Trivy** container image scanning

---

## Disclosure Policy

CoReason follows a **coordinated disclosure** model:

1. Reporter submits vulnerability privately via email
2. CoReason acknowledges and triages within the SLA
3. A fix is developed and tested in a private branch
4. A security advisory is published via GitHub Security Advisories
5. The patched release is published to PyPI
6. The reporter is credited (with their consent)

We request that reporters allow a **90-day disclosure window** before publishing details publicly.

---

## Contact

- **Security Reports:** [security@coreason.ai](mailto:security@coreason.ai)
- **General Inquiries:** [info@coreason.ai](mailto:info@coreason.ai)

---

*Copyright (c) 2026 CoReason, Inc. Licensed under the Prosperity Public License 3.0.*

