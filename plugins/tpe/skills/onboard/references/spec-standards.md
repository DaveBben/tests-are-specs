# Project Spec Standards Reference

Last updated: 2026-04-15

---

## Contents

- [Why Project Specs Matter](#why-project-specs-matter) — Philosophy and core insight
- [Key Principles](#key-principles) — Rules for drafting specs
- [Section Rules](#section-rules) — Required sections, ordering, and what makes each good
- [Anti-Patterns](#anti-patterns) — Known failure patterns to catch

---

## Why Project Specs Matter

AI coders make dozens of micro-decisions during implementation. Without a spec, those
decisions are uninformed — the AI guesses at conventions, misunderstands boundaries, and
builds against runtime constraints it doesn't know about. A project spec eliminates this by
documenting the context that code alone cannot convey: what's actually implemented right now,
how it behaves at its edges, and what the AI must never touch.

**The core insight:** The spec answers three questions: "What is this project? What does it
actually do right now? What are the rules?" Everything in the spec should serve one of these
questions. If it doesn't, it belongs in CLAUDE.md, in a change plan, or nowhere.

---

## Key Principles

- **Include only what an AI cannot figure out by reading the code.** If the code makes it
  obvious, the spec shouldn't restate it. The spec's value is in the non-obvious.
- **The spec describes what IS implemented, not what will be.** If a section describes future
  plans, remove it or move it to a change spec. Aspirational content in spec.md actively
  misleads AI coders.
- **Current State is the most important section — and it goes first.** It must be updated
  after every significant implementation change. A stale Current State is the worst failure
  mode — it makes the spec worse than having no spec at all. Front-load it so it survives
  context compression in long sessions.
- **Semantic density over completeness.** Each line in the spec should inform a specific
  agent decision. If you can't complete the sentence "An agent needs this to decide..." —
  the line belongs in human docs, not the spec. Dense, decision-relevant content outperforms
  comprehensive coverage.
- **One real code snippet beats paragraphs of description.** Show the pattern, don't explain
  it in prose.
- **Exact commands, not vague instructions.** `npm run test -- --watch` not "run the tests."
- **Document boundary behavior.** How the system behaves at its edges — external system
  failures, timeouts, retry policies, degraded mode — shapes every implementation decision.
  This is the highest-signal content in the spec.
- **State boundaries as a three-tier system.** Always do / Ask first / Never do — this gives
  the AI clear escalation levels so it knows when to proceed, when to pause, and when to stop.
  Always include "ask first if a pattern or decision isn't covered by this spec" to prevent
  invented conventions.
- **Capability constraints over failure modes.** What an API *can't* do (context window
  limits, no structured output, non-recursive listing) is often more valuable than what it
  can. These constraints shape protocol and algorithm design.
- **Name what's NOT implemented.** Stubs, placeholders, and intentionally incomplete features
  must be listed explicitly in Current State. An agent that assumes a stubbed integration works
  will build against a wall it can't see.

---

## Section Rules

### Root Spec — Sections (in order)

For multi-domain projects, the root spec is a **system-level navigation
layer** (target 60-100 lines). Domain-specific content moves to domain
specs. For single-domain projects, include everything in root (100-200 lines).

| # | Section | Key Rule | Multi-domain note |
|---|---------|----------|-------------------|
| 1 | **Current State** | **Most important. Goes first.** What IS implemented now. No future tense. Includes "Not yet implemented" list. | Root = system summary; domains = domain detail |
| 2 | What This Project Does | 2-4 sentences, product/purpose not technology | Always root |
| 3 | System Context | Optional. Only if: part of larger platform, adjacent services own things this doesn't, or origin prevents a wrong assumption. Omit for standalone projects. | Always root |
| 4 | Architecture Overview | System diagram + inter-domain flows + shared deps + optional decisions | Root = system structure; domain internals go in domain specs |
| 5 | Testing Strategy | Framework, location, how to run, conventions | Root = infrastructure + commands; domains own coverage gaps |
| 6 | Deployment & Infrastructure | CI/CD pipeline, environments, hosting | Always root (unless domains deploy independently) |
| 7 | Boundaries & Constraints | Three-tier: Always Do / Ask First / Never Do. Always include "ask if not covered by this spec." | Root = project-wide rules; domains own domain-specific rules |
| 8 | Gotchas | Optional. Non-obvious traps not derivable from code. Cross-cutting only. | Domain-specific gotchas go in domain specs |
| 9 | Ownership | Team or owner name, contact method | Root = project owner; domains can override |
| 10 | Spec Index | Subsystems + Features tables: spec name, path, one-line description | Always present |
| 11 | Known Issues | Cross-cutting issues only | Domain-specific issues go in domain specs |
| 12 | Tech Debt | Cross-cutting debt only | Domain-specific debt goes in domain specs |

### Subsystem Spec — Sections (for `docs/specs/subsystems/{domain-slug}/spec.md`)

Domain specs are created for projects with 2+ distinct subsystems. They
are loaded via `.claude/rules/` when the agent works in that directory.
Omit sections with no meaningful content — empty sections are worse than
missing ones.

| # | Section | Key Rule |
|---|---------|----------|
| 1 | What This Domain Owns | What it owns AND does NOT own — boundaries are the point |
| 2 | Current State | Present tense, what's implemented in this domain now. Include "Not yet implemented" list. |
| 3 | Domain Conventions | Only conventions that differ from or extend the root |
| 4 | Interface Contracts | Internal (consumed/exposed) + domain-specific external deps |
| 5 | Testing | Coverage gaps and domain-specific test conventions (not framework/commands) |
| 6 | Domain Boundaries | Domain-specific Always/Ask First/Never rules |
| 7 | Known Issues | Broken things in this domain. "None known." if clean |
| 8 | Gotchas | Domain-specific traps — highest-value content |

**Hard cap: 100 lines per domain spec.** Longer means content belongs
in the root spec or the domain needs further splitting.

**No duplication with root spec.** If it applies project-wide, it stays
at root. If it's domain-specific, it goes in the domain spec — not both.

### Optional Subsections (within Architecture Overview)

| Subsection | When to Include |
|------------|-----------------|
| Architecture Decisions table | When significant non-obvious architectural choices have been made |
| Degraded mode paragraph | When key dependencies can be independently unavailable |

### Status Field

The header includes a Status field (`Draft | Active | Stale`). See
`spec-section-guidance.md` for definitions of each value.

---

## Anti-Patterns

While drafting or reviewing, verify the spec does NOT contain:

- **Technology in "What This Project Does."** "A Next.js app with PostgreSQL" describes the
  stack, not the product. Rewrite as "A subscription management platform that lets small
  businesses manage recurring billing."
- **CLAUDE.md duplication.** Tech stack, directory structure, and dev commands belong in
  CLAUDE.md, not here.
- **Future-tense Current State.** "This project will support X" or "we plan to add Y" does
  not belong in Current State. The section describes what works today.
- **Stale Current State.** A Current State section that doesn't match what the code actually
  does. This is the worst failure mode — it actively misleads. After any significant
  implementation, check this section first.
- **Missing "Not Yet Implemented" list.** When the codebase has stubs, placeholders, or
  intentionally incomplete features, they must be listed explicitly. Burying them in prose
  is not enough — a named list prevents agents from assuming capabilities that don't exist.
- **Aspirational NFRs.** "The app should be secure" is not actionable. Only include
  thresholds that are actively enforced or measured.
- **Flat service inventory in External Dependencies.** Listing services without failure
  behavior or constraints is useless — the AI can find what services exist from the code.
  The value is in what happens when they fail and what they *can't* do.
- **Architecture decisions without rationale.** "We use PostgreSQL" states a fact the AI
  can derive from reading the code. "PostgreSQL over MongoDB — relational model needed for
  billing consistency" explains why.
- **Implementation details.** Specific feature implementations belong in change plans, not
  the project spec.
- **Empty placeholder text.** A section with only template placeholder text is worse than
  a missing section — it looks complete but provides no value.
- **Information that changes frequently.** Use references to external docs instead of
  embedding volatile information.
- **Code style rules enforced by a linter.** Never send an LLM to do a linter's job.
- **Standard language conventions.** "Use const instead of let" is TypeScript default
  knowledge — the AI already knows this.
- **Human motivation without decision value.** "This project exists because the ops team
  was spending 20 hours/week on manual processing" is not actionable for an agent. Only
  include origin context when it prevents a wrong technical assumption.
- **Lines that don't inform an agent decision.** Before finalizing any section, ask: "What
  agent decision does this line inform?" If it can't answer, remove the line. Dense,
  decision-relevant content outperforms comprehensive coverage.
- **Domain spec that duplicates the root.** If a domain spec restates project-wide
  boundaries, deployment info, or testing strategy, move that content to root and
  delete it from the domain spec. Duplication means two places to go stale.
- **Domain spec over 100 lines.** The domain is too broad or contains content that
  belongs at the root level. Split the domain or move shared content up.
- **Domain spec without interface contracts.** The primary value of a domain spec
  is documenting how this subsystem communicates with others. A domain spec that
  only lists conventions without interfaces is missing its highest-value content.
