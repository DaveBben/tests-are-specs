# Project Spec Template

Copy-paste starting point for spec.md. Fill in each section following the guidance in `spec-section-guidance.md`. Sections marked (optional) can be omitted if not applicable.

**For multi-domain projects** (2+ subsystems): this root spec stays slim and system-level. Domain-specific content (external deps, testing gaps, known issues, tech debt, domain boundaries) moves to `docs/specs/subsystems/{domain-slug}/spec.md`. See `domain-spec-template.md`.

## Contents

- [Current State](#current-state) — most important, load first
- [What This Project Does](#what-this-project-does)
- [System Context](#system-context) — optional
- [Architecture Overview](#architecture-overview) — includes shared external deps
- [Testing Strategy](#testing-strategy)
- [Deployment & Infrastructure](#deployment--infrastructure)
- [Boundaries & Constraints](#boundaries--constraints)
- [Gotchas](#gotchas) — optional
- [Ownership](#ownership)
- [Spec Index](#spec-index)
- [Known Issues](#known-issues)
- [Tech Debt](#tech-debt)

---

```markdown
# [Project Name] — Project Spec

**Last updated**: [YYYY-MM-DD]
**Last verified**: [YYYY-MM-DD]
**Status**: [Draft | Active | Stale] <!-- See spec-section-guidance.md for status definitions -->

> This spec represents current state, not aspirational state. Update it whenever
> implementation changes. The "Current State" section is the most important — keep it accurate.

---

## Table of Contents

- [Current State](#current-state)
- [What This Project Does](#what-this-project-does)
- [System Context](#system-context)
- [Architecture Overview](#architecture-overview)
- [Testing Strategy](#testing-strategy)
- [Deployment & Infrastructure](#deployment--infrastructure)
- [Boundaries & Constraints](#boundaries--constraints)
- [Gotchas](#gotchas)
- [Ownership](#ownership)
- [Spec Index](#spec-index)
- [Known Issues](#known-issues)
- [Tech Debt](#tech-debt)

---

## Current State

<!-- THE MOST IMPORTANT SECTION. A navigation layer, NOT a knowledge dump. Two parts:
1. System summary — 2-4 sentences on what runs end-to-end today and how the pieces connect
   at the system level (the data flow, the entry point, the handoff). No future tense.
2. A "Components" list with EXACTLY ONE line per component:
   `file — entry-point symbol — one-clause role — → feature-spec`. Anchor only the single
   entry-point function (e.g. FreshRSSClient.fetch_articles), never internal symbols, config
   values, or edge cases — those live in the component's feature spec and in the code. If a
   line wants a second sentence, it belongs in that feature spec, not here.
For multi-domain projects: keep this system-level. Each domain spec has its own Current State. -->

[System summary, e.g.:]
The stage-1 pipeline runs end-to-end from the CLI: fetch → dedup → classify → output.
`main()` (`src/__main__.py`) orchestrates a bounded producer/consumer pipeline with
crash-safe verdict-before-seen ordering; survivors hand off to a manual stage-2 review.
CI is green.

**Components** (detail in each feature spec):
- [Fetch — `freshrss.py` (`FreshRSSClient.fetch_articles`): paginates FreshRSS streams, crawl-time window, abort-on-failure. → freshrss-fetch]
- [Classify — `classifier.py` (`Classifier.classify`): forced tool-call KEEP/SKIP via local llama-server, fail-open to unclassified. → llm-classifier]

**Not yet implemented:**
- [e.g., NetSuite integration — stubbed in src/integrations/netsuite.ts, throws NotImplementedError]
- [e.g., Multi-tenant billing — no data model, no routes exist yet]

<!-- Omit "Not yet implemented" if the codebase has no meaningful stubs or incomplete features -->

---

## What This Project Does

[2-4 sentences. What the project is, who uses it, and what it accomplishes. No implementation details. This grounds every decision — if an AI is unsure about something, this section tells it what the project is trying to accomplish.]

---

## System Context

<!-- Optional. Include only if one or more of the following applies:
  - This project is part of a larger platform or micro-service ecosystem
  - Adjacent services own things this project explicitly does NOT own
  - The project's origin prevents a wrong technical assumption (e.g., "built for billing
    consistency — don't optimize for eventual consistency")
Omit this section entirely for standalone projects with no adjacent service boundaries. -->

- **Part of**: [e.g., "Payments platform — this service owns payment intent creation"]
- **Does NOT own**: [e.g., "Email notifications (owned by notifications service), user auth (owned by auth service)"]
- **Key constraint from origin**: [e.g., "Built for strong consistency — avoid eventual consistency patterns"]

---

## Architecture Overview

[High-level description of the major components and how they relate. An ASCII diagram is fine for complex systems. Focus on inter-domain data flows, not domain internals.]

```
[Client] → [API Gateway] → [Service Layer] → [Database]
                                ↓
                          [Event Bus] → [Workers]
```

**Key components:**
- [Component and what it does, e.g., "src/api/ — Express routes, one file per resource"]
- [Component and what it does]

### Shared External Dependencies

[Dependencies used by 2+ domains or the project as a whole. Domain-specific deps go in that domain's spec.md instead.]

| Dependency | Normal Behavior | Failure Behavior | Constraints / Can't Do |
|------------|----------------|------------------|------------------------|
| [e.g., PostgreSQL] | [connection pool, max 20] | [circuit breaker trips after 5 failures, returns 503] | [query timeout: 10s; no full-text search] |

**Degraded mode:** [What the system does when a shared dependency is unavailable.]

### Architecture Decisions (optional)

| Decision | Rationale | Date | Alternatives Considered |
|----------|-----------|------|------------------------|
| [e.g., "PostgreSQL over MongoDB"] | [e.g., "Relational data model, strong consistency needed for billing"] | [YYYY-MM-DD] | [e.g., "MongoDB — rejected due to transaction complexity"] |

---

## Testing Strategy

[Project-wide testing infrastructure only. Domain-specific coverage gaps and conventions go in domain specs.]

**Framework:** [name and version]
**Location:** [where test files live relative to source]
**Naming:** [convention, e.g., "*.test.ts co-located with source files"]

**Test types:**
- **Unit tests**: [how to run them]
- **Integration tests**: [how to run them, any setup needed]
- **E2E tests** (optional): [framework, how to run]

**Coverage summary:** [1-2 lines: which areas are well-tested, which have partial coverage, which have no tests. e.g., "Service layer is well-covered; webhook handler has no tests and is the highest-risk area; E2E tests cover the happy path only."]

**Testing conventions:**
- [e.g., "Use real database for integration tests, not mocks"]

---

## Deployment & Infrastructure

[How the app gets from code to production.]

**CI/CD:** [e.g., "GitHub Actions — tests run on every PR, deploy to staging on merge to `staging`, deploy to production on manual approval after merge to `main`"]

**Environments:**
- **Production**: [URL, hosting platform, e.g., "AWS ECS behind ALB"]
- **Staging**: [URL, how it's triggered]

**Infrastructure:** [Key infra components, e.g., "RDS PostgreSQL, ElastiCache Redis, S3 for file storage, CloudFront CDN"]

**Environment variables:** [How they're managed, e.g., "AWS Secrets Manager — see .env.example for the full list of required variables"]

---

## Boundaries & Constraints

[Project-wide boundaries only. Domain-specific boundaries go in domain specs.]

### Always Do
- [e.g., "Run tests before committing"]
- [e.g., "Update the Current State section in spec.md after significant implementation changes"]

### Ask First
- [e.g., "Before changing database schema or migrations"]
- [e.g., "Before modifying CI/CD configuration"]
- If a pattern, dependency, or architectural decision isn't covered by this spec, ask before inferring — don't invent conventions

### Never Do
- [e.g., "Never commit .env files or secrets"]
- [e.g., "Never modify files in vendor/ or generated/"]

---

## Gotchas

<!-- Optional but high value. Include institutional knowledge that prevents expensive AI mistakes —
things that are non-obvious and not derivable from reading the code. Omit if none exist.
Cross-cutting gotchas only; domain-specific gotchas go in domain specs. -->

- [e.g., "The `amount` field throughout the codebase is in cents, not dollars — no currency conversion helpers exist"]
- [e.g., "Migrations run automatically on deploy — never write a migration that can't run against live data"]
- [e.g., "The job queue is not idempotent — duplicate job submissions will double-process"]

---

## Ownership

- **Team/Owner**: [team name or individual]
- **Contact**: [Slack channel, email, or on-call rotation]

---

## Spec Index

### Subsystems
| Spec | Path | Description |
|------|------|-------------|
| [e.g., Billing] | `docs/specs/subsystems/billing/spec.md` | [e.g., "payment intents, refunds, Stripe integration"] |

### Features
| Spec | Path | Status | Updated | Description |
|------|------|--------|---------|-------------|

Status values: `Waiting Implementation` | `Implemented` | `Superseded` | `Deprecated` | `Needs Revision`.

The `Updated` column tracks the spec lifecycle — it always holds the `YYYY-MM-DD` date of the most recent lifecycle event:
- **Created**: `/spec-monkey:create-spec` adds the row as `Waiting Implementation`, `Updated` = creation date.
- **Updated**: any edit refreshes `Updated`. `/spec-monkey:execute-spec` flips status to `Implemented` when verification passes; a spec needing changes before implementation is set to `Needs Revision`.
- **Deleted**: never remove the row — set status to `Superseded` (replaced by a newer spec) or `Deprecated` (abandoned or feature removed) and refresh `Updated`. Keeping the row preserves the audit trail.

Subsystem specs contain: domain-specific current state, conventions, interface contracts, external deps, testing gaps, boundaries, known issues, and gotchas. Loaded via `.claude/rules/` when working in that directory. Feature specs are created by `/spec-monkey:create-spec` and document individual code changes.

---

## Known Issues

[Cross-cutting issues only. Domain-specific issues go in domain specs. Write "None known." if clean.]

- **[Issue]**: [description, severity, workaround if any]

---

## Tech Debt

[Cross-cutting tech debt only. Domain-specific debt goes in domain specs.]

- [e.g., "No database connection pooling — using a single connection. Acceptable at current load (<100 req/min) but will need addressing before scaling. Ticket: #87."]
```

> **Target: 60-100 lines for multi-domain projects.** The root spec is a navigation layer, not a knowledge dump. Domain-specific content lives in domain specs. For single-domain projects, include all content in the root spec (no domain specs needed) — target 100-200 lines.
