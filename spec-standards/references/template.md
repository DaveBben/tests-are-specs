# Project Spec Template

Copy-paste starting point for spec.md. Fill in each section following the guidance in
`section-guidance.md`. Sections marked (optional) can be omitted if not applicable.

---

```markdown
# [Project Name] — Project Spec

**Last updated**: [YYYY-MM-DD]
**Status**: [Draft | Active | Needs Update] <!-- See section-guidance.md for status definitions -->

> This spec represents current state, not aspirational state. Update it whenever
> implementation changes. The "Current State" section is the most important — keep it accurate.

---

## What This Project Does

[2-4 sentences. What the project is, who uses it, and why it exists. No implementation details.
This grounds every decision — if an AI is unsure about something, this section tells it what
the project is trying to accomplish.]

---

## Why This Project Exists

[The problem this project solves and what motivated its creation. If this project is a
micro-service or component of a larger system, describe that context here — what system does
it serve and what role does it play?]

- [e.g., "Manual invoice processing was costing the ops team 20 hours/week and producing errors"]
- [e.g., "Part of the billing platform — this service owns payment intent creation; the
  notifications service handles emails downstream"]

---

## Current State

<!-- THIS IS THE MOST IMPORTANT SECTION. Write 2-4 concrete sentences describing what is
actually implemented and working today. Distinguish what's done from what's stubbed or
in-progress. No future tense. Update this section after every significant implementation change. -->

[e.g., "The API accepts invoice submission via POST /invoices and stores them in PostgreSQL.
Reconciliation runs nightly via a cron job and creates Linear tickets for discrepancies.
The Stripe integration is complete; NetSuite integration is stubbed with a TODO in
src/integrations/netsuite.ts and currently throws NotImplementedError."]

---

## Architecture Overview

[High-level description of the major components and how they relate. An ASCII diagram is
fine for complex systems. Reference real source paths rather than describing them inline.]

```
[Client] → [API Gateway] → [Service Layer] → [Database]
                                ↓
                          [Event Bus] → [Workers]
```

**Key components:**
- [Component and what it does, e.g., "src/api/ — Express routes, one file per resource"]
- [Component and what it does]

### External Dependencies

[Document every external system this project communicates with. Include failure behavior
and constraints — this is the highest-signal content for AI coders.]

| Dependency | Normal Behavior | Failure Behavior | Constraints |
|------------|----------------|------------------|-------------|
| [e.g., Stripe API] | [sync call on checkout] | [retry 3x with exponential backoff, then queue for manual review] | [timeout: 5s, rate limit: 100/min] |
| [e.g., PostgreSQL] | [connection pool, max 20] | [circuit breaker trips after 5 failures, returns 503] | [query timeout: 10s] |

**Degraded mode:** [What the system does when a key dependency is unavailable. e.g., "If
Redis is unavailable, sessions fall back to database-backed sessions. If Stripe is down,
checkout is disabled but browsing continues."]

### Architecture Decisions (optional)

[Significant choices and their rationale. Prevents AI from unknowingly reversing deliberate decisions.]

| Decision | Rationale | Date | Alternatives Considered |
|----------|-----------|------|------------------------|
| [e.g., "PostgreSQL over MongoDB"] | [e.g., "Relational data model, strong consistency needed for billing"] | [YYYY-MM-DD] | [e.g., "MongoDB — rejected due to transaction complexity"] |

---

## Testing Strategy

**Framework:** [name and version]
**Location:** [where test files live relative to source]
**Naming:** [convention, e.g., "*.test.ts co-located with source files"]

**Test types:**
- **Unit tests**: [what they cover, how to run them]
- **Integration tests**: [what they cover, how to run them, any setup needed]
- **E2E tests** (optional): [framework, how to run, any environment requirements]

**Coverage target:** [if any]

**What's well-covered:** [areas with strong test coverage]
**What's missing or thin:** [areas with little or no coverage — be honest]

**Testing conventions:**
- [e.g., "Use real database for integration tests, not mocks"]

---

## Deployment & Infrastructure

[How the app gets from code to production.]

**CI/CD:** [e.g., "GitHub Actions — tests run on every PR, deploy to staging on merge to
`staging`, deploy to production on manual approval after merge to `main`"]

**Environments:**
- **Production**: [URL, hosting platform, e.g., "AWS ECS behind ALB"]
- **Staging**: [URL, how it's triggered]

**Infrastructure:** [Key infra components, e.g., "RDS PostgreSQL, ElastiCache Redis,
S3 for file storage, CloudFront CDN"]

**Environment variables:** [How they're managed, e.g., "AWS Secrets Manager — see
.env.example for the full list of required variables"]

---

## Boundaries & Constraints

[The three-tier boundary system. This is critical — it prevents the AI from making
dangerous or disruptive changes.]

### Always Do
- [e.g., "Run tests before committing"]
- [e.g., "Update the Current State section in spec.md after significant implementation changes"]

### Ask First
- [e.g., "Before changing database schema or migrations"]
- [e.g., "Before adding new dependencies"]
- [e.g., "Before modifying CI/CD configuration"]

### Never Do
- [e.g., "Never commit .env files or secrets"]
- [e.g., "Never modify files in vendor/ or generated/"]
- [e.g., "Never delete migration files"]

---

## Ownership

[Who owns this repo and who to contact when something breaks.]

- **Team/Owner**: [team name or individual]
- **Contact**: [Slack channel, email, or on-call rotation]
- [e.g., "For production incidents, page the platform team via PagerDuty"]

---

## Known Issues

[Things that are currently broken or degraded in this repo. Each entry: what is broken,
severity, and any known workaround. Write "None known." if the repo is clean.]

- **[Issue]**: [description, severity, workaround if any]
- [e.g., "Stripe webhook handler throws 500 on malformed payloads — no validation before
  JSON.parse(). Severity: medium (only affects malformed webhooks). Workaround: use Stripe
  CLI's test payloads only. Tracked in issue #42."]

---

## Tech Debt

[Deferred improvements that would raise codebase quality but haven't been prioritized.
Each entry: what it is and why it was deferred.]

- [e.g., "Auth token refresh is implemented inline in every route handler instead of
  middleware — deferred because there are only 3 routes today. Will need extraction
  when the admin API is added. ~2 days effort."]
- [e.g., "No database connection pooling — using a single connection. Acceptable at current
  load (<100 req/min) but will need addressing before scaling. Ticket: #87."]
```
