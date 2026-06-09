# Section-by-Section Guidance

Why each section exists and what makes it good versus bad. This guidance is for Claude's
reference while drafting or reviewing — do NOT include this text in the output spec.md.

## Contents

- [Status Field](#status-field)
- [**Current State**](#current-state) ← most important, goes first
- [What This Project Does](#what-this-project-does)
- [System Context](#system-context)
- [Architecture Overview](#architecture-overview)
- [Testing Strategy](#testing-strategy)
- [Deployment & Infrastructure](#deployment--infrastructure)
- [Boundaries & Constraints](#boundaries--constraints)
- [Gotchas](#gotchas)
- [Ownership](#ownership)
- [Known Issues](#known-issues)
- [Tech Debt](#tech-debt)

---

## Status Field

This is the *reference-document* status for a subsystem/project spec —
it describes whether the doc is accurate. It is distinct from the
*work-item* lifecycle status (`Waiting Implementation` … `Needs
Revision`) that feature and bug specs carry in the Spec Index. Keep
the two vocabularies separate: a reference doc goes `Stale`; a
work-item spec goes `Needs Revision`.

- **Draft**: Spec is being written or has not been reviewed by the team
- **Active**: Spec is reviewed, accurate, and being used as a reference
- **Stale**: A significant change (new feature, architectural shift, removed dependency) has made part of the spec out of date — update before relying on it

## Last Verified Date

The `Last verified` field records when a human last confirmed the spec
matches reality. Update it whenever you review the spec for accuracy —
even if no content changed.

**Staleness threshold**: If `Last verified` is more than 30 days old,
tools that consume the spec (e.g., `/specd:execute-spec` pre-flight) should
warn that the spec may be stale. The Codified Context research found
that specification staleness is a silent failure mode — agents trust
documentation absolutely, so outdated specs cause them to generate
code that conflicts with recent refactors.

---

## Current State

**This is the most important section. It goes first in the spec.** It tells the reader what
is actually working in the repo right now. A developer or AI reading this should immediately
understand the current shape of the codebase without digging through code.

Front-loading Current State also makes the spec resilient to context compression: in long
sessions where older context gets summarized or dropped, the highest-density content survives
because it appeared first.

### Split behavior (multi-domain projects)
- **Root spec**: 2-4 sentence system-level summary. What the system does as a whole.
- **Domain specs**: 2-3 sentence domain-level detail. What this specific subsystem does.
- The root should not repeat domain-level detail — point to domain specs instead.

### What it should contain
- 2-4 concrete sentences describing what is implemented and working today
- A named **"Not yet implemented"** list for any stubs, placeholders, or intentionally
  incomplete features — do not bury these in prose
- Reference key modules, endpoints, or integrations by their actual path, identifier,
  and entry-point function — e.g., `PipelineController.processNext()` not just
  `PipelineController`. Including the symbol name eliminates search time when an
  agent needs to find where behavior originates. Research shows agents spend 60-80%
  of their tokens locating relevant code; naming the entry point collapses that cost.
- Be specific — "Stripe integration is complete" is less useful than "Stripe integration is
  complete (src/integrations/stripe.ts:createPaymentIntent())"

### The "Not Yet Implemented" list

This is a first-class subsection, not an afterthought. List every stub, placeholder, and
intentionally incomplete feature by name and location. An agent that assumes a stubbed
integration works will build against a wall it can't see.

- **Bad**: "Some integrations are still being built." (vague, doesn't name them)
- **Good**:
  ```
  **Not yet implemented:**
  - NetSuite integration — stubbed in src/integrations/netsuite.ts, throws NotImplementedError
  - Multi-tenant billing — no data model or routes exist yet
  ```
- Omit the subsection entirely if the codebase has no meaningful stubs or incomplete features

### Update trigger
This section **must be updated** whenever:
- A feature ships or is removed
- A module changes its role significantly
- Something moves from "stubbed" to "implemented" (or vice versa)

At the start of a session in a repo with spec.md, check whether Current State still matches
what the code actually does. If it's stale, update it before starting new work.

### Examples
- Bad: "This project will support multi-tenant billing." (future tense — describes what will be, not what is)
- Bad: "Work is ongoing on the authentication module." (vague progress language)
- Bad: "The app handles user management." (too abstract — gives no concrete picture)
- Good: "The API accepts invoice submission via POST /invoices and stores them in PostgreSQL.
  Reconciliation runs nightly via a cron job and creates Linear tickets for discrepancies.
  The Stripe integration is complete (src/integrations/stripe.ts).

  **Not yet implemented:**
  - NetSuite integration — stubbed in src/integrations/netsuite.ts, throws NotImplementedError"

---

## What This Project Does
- 2-4 sentences maximum
- Must describe the product/purpose, not the technology
- Bad: "A Next.js app with PostgreSQL and Redis" (describes stack, not purpose)
- Good: "A subscription management platform that lets small businesses create, bill, and manage
  recurring customer subscriptions. Used by ~2,000 businesses."

---

## System Context

**Optional section.** Include only when one or more of the following applies:

1. **This project is part of a larger platform or micro-service ecosystem** — name the platform
   and describe this project's role. Name what adjacent services own that this project does NOT.
2. **Adjacent services own things this project explicitly does NOT own** — this prevents agents
   from adding code to the wrong service.
3. **The project's origin prevents a wrong technical assumption** — e.g., "built for strong
   billing consistency — don't optimize for eventual consistency."

**Omit entirely for standalone projects** with no adjacent service boundaries. Do not include
organizational motivation ("manual processing cost 20 hours/week") unless it directly prevents
a wrong technical choice.

- Bad: "This project was created because the ops team needed a better solution." (human motivation with no decision value)
- Bad: "Part of the platform" (too vague to constrain decisions)
- Good: "Part of the payments platform. This service owns payment intent creation and refund processing. Email notifications are owned by the notifications service — never add email-sending code here."
- Good: "Built for strong financial consistency — Stripe webhooks must be idempotent and all payment state transitions must be atomic. Don't apply eventual consistency patterns to payment records."

---

## Architecture Overview

Describes how the major components relate and what external systems this project communicates with. This section has three subsections:

### Main overview
- High-level description of the major components and how they relate
- ASCII diagrams are fine for complex systems — keep them simple
- Reference real source paths rather than describing components in prose
- For pipelines or multi-stage systems: document what data flows between stages. A brief table like "Stage 1 emits transcript + file URL; Stage 2 emits destination + extracted fields" prevents the AI from having to read multiple source files to understand handoff contracts. Include ownership semantics (e.g., "returning true keeps the lock held; Stage 2 must explicitly call releaseLock()")
- Bad: describing every function in the codebase
- Good: "Repository pattern for database access (src/lib/repos/), all repos extend BaseRepository"

### External Dependencies (subsection)

**Split behavior**: In multi-domain projects, only *shared* dependencies (used by 2+
domains) stay in the root spec. Domain-specific dependencies (e.g., Stripe in billing)
move to that domain's spec.md. This prevents an agent working in auth from loading
billing's Stripe constraints into its context.

Every external system this project communicates with should have an entry. The table documents
failure behavior and capability constraints — this is the highest-signal content for AI coders.

**The "Constraints / Can't Do" column is critical.** Document what the API *can't* do, not just
failure modes:
- Context window limits (e.g., ~4K tokens for Foundation Model)
- Output format restrictions (e.g., free-text only, no function-calling/JSON mode)
- Initialization semantics (e.g., instructions set at session init, not per-call)
- Operation limitations (e.g., listFolders returns immediate children only, not recursive)
- Latency characteristics (e.g., each AppleScript call is ~100-500ms IPC roundtrip)

These constraints shape protocol design, algorithm choices, and chunking strategies. Without
them, the AI will design solutions that hit invisible walls.

- Bad: just listing what services exist (that's a flat inventory, not boundary behavior)
- Bad: "Uses Foundation Model framework" (states a fact — doesn't mention the ~4K token limit or free-text-only output that shape every design decision)
- Good: "Foundation Model API — instructions set at session init (not per-call), ~4K token context window, free-text output only (no function-calling/JSON mode). Parse responses with heuristics and fallback handling."
- Good: "AppleScript/Notes — each call is ~100-500ms IPC roundtrip. listFolders returns immediate children only. Batch where possible to avoid N+1."
- The "Degraded mode" paragraph prevents the AI from assuming all-or-nothing availability

### Architecture Decisions (optional subsection)
- Include only when significant non-obvious choices have been made
- Each entry must include the rationale (the "why"), not just the choice
- The "Alternatives Considered" column prevents revisiting settled debates
- Bad: "We use PostgreSQL" (states a fact the AI can derive from reading the code)
- Good: "PostgreSQL over MongoDB — relational model needed for billing transaction consistency; MongoDB evaluated Q1 2024 and rejected"

---

## Testing Strategy

**Split behavior**: In multi-domain projects, the root spec keeps framework name,
runner commands, and project-wide conventions. Coverage gaps and domain-specific
test conventions (e.g., "use Stripe test clock" for billing) move to domain specs.
This way the agent gets the right testing context for the domain it's working in.

- Include framework name, file location conventions, and how to run tests
- Mention any setup requirements (database seeding, env vars, Docker containers)
- State whether mocks or real services are preferred
- **Flag gaps, not just coverage.** Note which test categories exist AND which are missing or thin. A testing strategy that only lists what exists without flagging gaps misleads the AI into thinking coverage is complete.
- **Include a coverage summary** — a 1-2 line statement of which areas are well-tested,
  which have partial coverage, and which have no tests. This is the single most actionable
  context for an agent writing verification commands. Research (ORACLE-SWE) shows that
  reproduction/verification context is the #1 most valuable signal for coding agents —
  knowing where tests exist (and don't) directly determines whether verification can rely
  on existing tests or needs new ones.
- Bad: "We have tests" (useless)
- Bad: only listing what exists with no mention of gaps
- Good: "Integration tests use a real PostgreSQL instance via testcontainers. Run
  `pnpm test:integration` — Docker must be running. Unit tests cover the service layer;
  the webhook handler has no tests and is the highest-risk area."
- Good coverage summary: "Pipeline stages are well-covered in CoreTests; UI view models
  have partial coverage (SettingsRoutingModelTests only); AppleScript integration tests
  exist but are local-only (skipped in CI)."

---

## Deployment & Infrastructure
- Describe how code gets from a merged commit to production
- Include CI/CD pipeline, environment names, deploy triggers, and hosting platform
- If there is no CI/CD yet, say so explicitly rather than leaving the section blank
- Bad: "Deploys to AWS." (no useful detail)
- Good: "Deploys to AWS ECS via GitHub Actions on merge to main. Staging environment at staging.example.com deploys on every PR merge to `staging` branch. Production deploy requires manual approval in GitHub Actions. Environment variables managed via AWS Secrets Manager."

---

## Boundaries & Constraints

**Split behavior**: In multi-domain projects, project-wide rules (never commit
secrets, always run tests) stay at root. Domain-specific rules (never call Stripe
without idempotency keys, always use the billing connection pool) move to domain
specs. An agent in billing gets billing's boundaries loaded automatically via
`.claude/rules/` — it doesn't need to parse project-wide boundaries to find the
billing-specific ones.

- The three-tier system (Always/Ask First/Never) prevents the AI from making dangerous changes
- "Never" items are hard stops — the AI must not proceed regardless of context
- "Ask First" items require explicit user approval before proceeding
- "Always" items are habits the AI should maintain without being asked
- Always include in Ask First: "If a pattern, dependency, or architectural decision isn't covered by this spec, ask before inferring — don't invent conventions"
- Always include in Always: "Update the Current State section in spec.md after significant implementation changes"
- Bad: empty or missing (gives the AI infinite permission)
- Good: specific, actionable boundaries that protect the codebase

---

## Gotchas

**Optional but highest-value content.** Include institutional knowledge that prevents
expensive AI mistakes — things that are non-obvious, not derivable from reading the code,
and that a competent engineer would know from experience but a new agent would not.

Include only cross-cutting gotchas here. Domain-specific gotchas (e.g., "Stripe amount is
in cents") go in domain specs.

Omit this section entirely if no genuine gotchas exist — don't pad it.

### What belongs here
- Naming or convention traps that exist project-wide (e.g., "all `amount` fields are cents")
- Implicit dependencies between systems that aren't visible from code structure
- Operations that look safe but have hidden side effects in this project
- Things that have caused production incidents that aren't yet fixed by a linter or test

### Examples
- Bad: "Be careful when making changes." (not actionable)
- Bad: "Always handle errors." (standard practice, not a project-specific gotcha)
- Good: "The job queue is not idempotent — duplicate submissions will double-process. Always check for existing jobs before enqueuing."
- Good: "Migrations run automatically on deploy with no dry-run step — never write a migration that can't run against live production data without downtime."
- Good: "The `config` object is mutated by middleware during request processing — never cache a reference to it across async boundaries."

---

## Ownership
- Who owns this repo and who to contact when something breaks
- One to three lines: team name, Slack channel or email, on-call rotation if applicable
- If ownership is genuinely unclear, write "Unclear — ask [name or team] before making breaking changes" rather than leaving the section blank
- Bad: leaving blank or writing "TBD"
- Good: "Platform team — #platform-eng on Slack. For production incidents, page via PagerDuty."

---

## Known Issues

**Split behavior**: In multi-domain projects, issues go in the domain spec where
they live. A billing webhook bug belongs in billing's spec, not root. Root keeps
only cross-cutting issues that span domains. This prevents an agent in auth from
loading billing's known issues into context.

- Things that are **currently broken or degraded** in the repo — not historical traps or gotchas
- Each entry: what is broken, severity (blocks work / annoying / minor), and any known workaround
- Write "None known." if the repo is clean rather than leaving the section blank
- Bad: "Hot reload breaks sometimes." (vague, no context)
- Good: "Stripe webhook handler throws 500 on malformed payloads — no validation before JSON.parse(). Severity: medium (only affects malformed webhooks). Workaround: use Stripe CLI's test payloads only. Tracked in issue #42."

---

## Tech Debt

**Split behavior**: Same as Known Issues — domain-specific debt goes in domain
specs. Root keeps only cross-cutting debt (e.g., no connection pooling project-wide).

- Deferred work that would improve quality but has been intentionally set aside
- Each entry: what it is, why it was deferred, rough effort estimate if known
- Bad: "Code could be better." (useless)
- Good: "Auth token refresh is implemented inline in every route handler instead of middleware — deferred because there are only 3 routes today. Will need extraction when the admin API is added. ~2 days effort."
- Good: "No database connection pooling — using a single connection. Acceptable at current load (<100 req/min) but will need addressing before scaling. Ticket: #87."
