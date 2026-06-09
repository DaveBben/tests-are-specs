# CLAUDE.md Format

This document defines the standard section structure and guidance for CLAUDE.md files.

## Contents

1. [Template](#template) — the five-section skeleton
2. [Project Identity](#1-project-identity) — what, why, who
3. [Tech Stack and Codebase Map](#2-tech-stack-and-codebase-map) — language, framework, layout
4. [Operational Commands](#3-operational-commands) — exact shell commands
5. [Critical Constraints](#4-critical-constraints) — hard MUST / MUST NOT rules
6. [Pointers to Deeper Docs](#5-pointers-to-deeper-docs) — file path references

## Template

The generated CLAUDE.md should contain these five sections in this order. Omit a section entirely if it would be empty and no placeholder is warranted:

```markdown
## Project Identity

<!-- 1-3 sentences: what this project does, why it exists, and who it serves -->

## Tech Stack and Codebase Map

<!-- Language, framework versions, package manager, directory layout -->

## Operational Commands

<!-- Exact shell commands for build, test, lint, format, run -->

## Critical Constraints

<!-- Things that MUST or MUST NOT happen in this project -->

## Pointers to Deeper Docs

<!-- Descriptive file references — e.g., `spec.md` — product requirements and acceptance criteria -->
```

---

## Section-by-Section Guidance

### 1. Project Identity

1-3 sentences covering what the project does, why it exists, and who it serves. This is the "elevator
pitch" that gives Claude the context to make decisions aligned with the project's purpose.

**Good:**
> Internal billing reconciliation service that pulls invoices from Stripe and NetSuite nightly,
> detects discrepancies, and opens tickets in Linear for the finance team to review. Exists because
> manual reconciliation was missing ~3% of mismatches each quarter.

**Bad:**
> This is a Python project that uses AWS CDK and boto3.

The bad example describes *how* (technology), not *what* or *why*. Technology belongs in Tech Stack.

---

### 2. Tech Stack and Codebase Map

List the primary language and framework with versions, the package manager, and a brief directory
layout. This section helps Claude locate code and understand the toolchain.

**Include:**
- Language and version (e.g., "Python 3.11")
- Framework and version if applicable (e.g., "AWS CDK 2.198.0")
- Package manager (e.g., "uv", "npm", "pnpm", "cargo")
- Top-level directory tree with one-line purposes
- Code generation tools if any (e.g., "XcodeGen generates .xcodeproj from project.yml")

**Good:**
```markdown
- Language: Python 3.11
- Infrastructure: AWS CDK 2.198.0 (via aws-cdk-lib)
- Package Manager: uv (with uv.lock, workspace mode)
- Formatting: black (line-length 88), isort
- Linting: flake8, ruff
- Testing: unittest, coverage

### Directory Layout
**Good:**
- `infra/` — CDK infrastructure definitions
- `src/functions/` — Lambda function handlers
- `src/layers/python/` — Shared Lambda layers
- `test/unit/` — Unit tests
- `test/integration/` — Integration tests
- `scripts/` — Utility scripts
- `bin/` — Shell scripts (deploy, test, lint, format)
- `app.py` — CDK app entry point
```

**Bad:**
```markdown
We use Python and AWS. The code is in src/.
```

The bad example lacks versions, omits the package manager, and gives no useful directory information.

Keep the directory layout to top-level directories only. Claude can explore subdirectories on its own.

---

### 3. Operational Commands

Exact, copy-pasteable shell commands for the most common operations. One command per line with a brief
description. These are the commands Claude will actually run.

**Include:** build, test, lint, format, run/deploy — whatever applies to the project.

**Good:**
```markdown
- `uv sync` — install dependencies
- `./bin/test.sh` — run linting + unit tests with coverage
- `./bin/test.sh -s` — run unit tests only (skip linting)
- `./bin/lint.sh` — run black (check), isort (check), flake8
- `./bin/format.sh` — auto-format with black + isort
- `coverage run -m unittest discover -v -s ./test/unit` — run unit tests directly
- `coverage report -m --omit="./test/*"` — show coverage report
```

**Bad:**
```markdown
- Run the tests before committing
- Make sure linting passes
- Install dependencies first
```

The bad example describes *what to do*, not *how to do it*. Claude needs exact commands, not
instructions to figure them out.

---

### 4. Critical Constraints

Hard rules that MUST or MUST NOT be followed in this project. These are the guardrails — things that
would cause real damage if violated. Only include constraints that are universally applicable and
not already enforced by tooling.

**Good:**
- Never commit `.env` files or credentials
- All database migrations must be reversible
- Public API endpoints require authentication — no anonymous access
- Do not modify files in `vendor/` — they are managed by the dependency tool

**Bad:**
- Write good code
- Follow best practices
- Be careful with the database

The bad examples are vague and unverifiable. If you cannot write a test or check for it, it is not
a constraint — it is a wish.

If you have no hard constraints, leave the HTML comment placeholder. An empty section is better than
a section full of vague guidance.

---

### 5. Pointers to Deeper Docs

One line per document: file path + dash + purpose. These point Claude to authoritative references
without copying their content into CLAUDE.md.

**Good:**
```markdown
- `docs/specs/spec.md` — project spec, architecture, and spec index for all subsystem/feature specs
- `docs/architecture.md` — system architecture and component design
- `docs/api.md` — REST API endpoint reference
- `CONTRIBUTING.md` — pull request process and code review standards
```

**Bad:**
```markdown
- See the docs folder for more information
```

The bad example gives no specific paths and no descriptions. Claude cannot efficiently find what it
needs without concrete pointers.

Only list docs that exist. Do not list aspirational documents.
