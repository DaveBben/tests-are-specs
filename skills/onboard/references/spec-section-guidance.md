# Section-by-Section Guidance

Why each section exists and what makes it good versus bad. This guidance is for Claude's
reference while drafting or reviewing — do NOT include this text in the output spec.md.

## Contents

- [Status Field](#status-field)
- [What This Project Does](#what-this-project-does)
- [Why This Project Exists](#why-this-project-exists)
- [Current State](#current-state) ← most important
- [Architecture Overview](#architecture-overview)
- [Testing Strategy](#testing-strategy)
- [Deployment & Infrastructure](#deployment--infrastructure)
- [Boundaries & Constraints](#boundaries--constraints)
- [Ownership](#ownership)
- [Known Issues](#known-issues)
- [Tech Debt](#tech-debt)

---

## Status Field
- **Draft**: Spec is being written or has not been reviewed by the team
- **Active**: Spec is reviewed, accurate, and being used as a reference
- **Needs Update**: A significant change (new feature, architectural shift, removed dependency) has made part of the spec stale — update before relying on it

---

## What This Project Does
- 2-4 sentences maximum
- Must describe the product/purpose, not the technology
- Bad: "A Next.js app with PostgreSQL and Redis" (describes stack, not purpose)
- Good: "A subscription management platform that lets small businesses create, bill, and manage
  recurring customer subscriptions. Used by ~2,000 businesses."

---

## Why This Project Exists
- Focus on the problem being solved, not current sprint work
- If this project is a micro-service or component of a larger system, say so — name the parent system and describe this project's role within it
- Each point should explain motivation — what was broken, costly, or missing before this project
- Bad: "Make the app better" (unmeasurable, no context)
- Good: "Manual invoice processing was costing 20 hours/week — this automates the entire flow"
- Good: "Micro-service within the payments platform — this service owns payment intent creation; the notifications service handles downstream emails"
- This section helps the AI prioritize trade-offs: understanding the root problem prevents solutions that technically work but miss the point

---

## Current State

**This is the most important section.** It tells the reader what is actually working in the repo right now. A developer or AI reading this should immediately understand the current shape of the codebase without digging through code.

### What it should contain
- 2-4 concrete sentences describing what is implemented and working today
- Note anything that is stubbed, in-progress, or intentionally incomplete
- Name the key modules, endpoints, or integrations by their actual path or identifier
- Be specific — "Stripe integration is complete" is less useful than "Stripe integration is complete; see src/integrations/stripe.ts"

### Update trigger
This section **must be updated** whenever:
- A feature ships or is removed
- A module changes its role significantly
- Something moves from "stubbed" to "implemented" (or vice versa)

At the start of a session in a repo with spec.md, check whether Current State still matches what the code actually does. If it's stale, update it before starting new work.

### Examples
- Bad: "This project will support multi-tenant billing." (future tense — describes what will be, not what is)
- Bad: "Work is ongoing on the authentication module." (vague progress language)
- Bad: "The app handles user management." (too abstract — gives no concrete picture)
- Good: "The API accepts invoice submission via POST /invoices and stores them in PostgreSQL.
  Reconciliation runs nightly via a cron job and creates Linear tickets for discrepancies.
  The Stripe integration is complete (src/integrations/stripe.ts); NetSuite integration is
  stubbed with a TODO in src/integrations/netsuite.ts and currently throws NotImplementedError."

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
Every external system this project communicates with should have an entry. The table documents failure behavior and constraints — this is the highest-signal content for AI coders.

**Capability constraints are critical.** Document what the API *can't* do, not just failure modes:
- Context window limits (e.g., ~4K tokens for Foundation Model)
- Output format restrictions (e.g., free-text only, no function-calling/JSON mode)
- Initialization semantics (e.g., instructions set at session init, not per-call)
- Operation limitations (e.g., listFolders returns immediate children only, not recursive)
- Latency characteristics (e.g., each AppleScript call is ~100-500ms IPC roundtrip)

These constraints shape protocol design, algorithm choices, and chunking strategies. Without them, the AI will design solutions that hit invisible walls.

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
- Include framework name, file location conventions, and how to run tests
- Mention any setup requirements (database seeding, env vars, Docker containers)
- State whether mocks or real services are preferred
- **Flag gaps, not just coverage.** Note which test categories exist AND which are missing or thin. A testing strategy that only lists what exists without flagging gaps misleads the AI into thinking coverage is complete.
- Bad: "We have tests" (useless)
- Bad: only listing what exists with no mention of gaps
- Good: "Integration tests use a real PostgreSQL instance via testcontainers. Run
  `pnpm test:integration` — Docker must be running. Unit tests cover the service layer;
  the webhook handler has no tests and is the highest-risk area."

---

## Deployment & Infrastructure
- Describe how code gets from a merged commit to production
- Include CI/CD pipeline, environment names, deploy triggers, and hosting platform
- If there is no CI/CD yet, say so explicitly rather than leaving the section blank
- Bad: "Deploys to AWS." (no useful detail)
- Good: "Deploys to AWS ECS via GitHub Actions on merge to main. Staging environment at staging.example.com deploys on every PR merge to `staging` branch. Production deploy requires manual approval in GitHub Actions. Environment variables managed via AWS Secrets Manager."

---

## Boundaries & Constraints
- The three-tier system (Always/Ask First/Never) prevents the AI from making dangerous changes
- "Never" items are hard stops — the AI must not proceed regardless of context
- "Ask First" items require explicit user approval before proceeding
- "Always" items are habits the AI should maintain without being asked
- Always include: "Update the Current State section in spec.md after significant implementation changes"
- Bad: empty or missing (gives the AI infinite permission)
- Good: specific, actionable boundaries that protect the codebase

---

## Ownership
- Who owns this repo and who to contact when something breaks
- One to three lines: team name, Slack channel or email, on-call rotation if applicable
- If ownership is genuinely unclear, write "Unclear — ask [name or team] before making breaking changes" rather than leaving the section blank
- Bad: leaving blank or writing "TBD"
- Good: "Platform team — #platform-eng on Slack. For production incidents, page via PagerDuty."

---

## Known Issues
- Things that are **currently broken or degraded** in the repo — not historical traps or gotchas
- Each entry: what is broken, severity (blocks work / annoying / minor), and any known workaround
- Write "None known." if the repo is clean rather than leaving the section blank
- Bad: "Hot reload breaks sometimes." (vague, no context)
- Good: "Stripe webhook handler throws 500 on malformed payloads — no validation before JSON.parse(). Severity: medium (only affects malformed webhooks). Workaround: use Stripe CLI's test payloads only. Tracked in issue #42."

---

## Tech Debt
- Deferred work that would improve quality but has been intentionally set aside
- Each entry: what it is, why it was deferred, rough effort estimate if known
- Bad: "Code could be better." (useless)
- Good: "Auth token refresh is implemented inline in every route handler instead of middleware — deferred because there are only 3 routes today. Will need extraction when the admin API is added. ~2 days effort."
- Good: "No database connection pooling — using a single connection. Acceptable at current load (<100 req/min) but will need addressing before scaling. Ticket: #87."
