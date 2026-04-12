---
name: spec-standards
description: >
  Provides the standards, validation rules, anti-patterns, and template for project-level
  specs (spec.md). Use when creating or reviewing spec.md files. Do NOT invoke directly —
  this is a reference consumed by spec-authoring and spec-review workflows.
user-invocable: false
disable-model-invocation: true
---

# Project Spec Standards Reference

Last updated: 2026-04-11

---

## Contents

- [Why Project Specs Matter](#why-project-specs-matter) — Philosophy and core insight
- [Key Principles](#key-principles) — Rules for drafting specs
- [Section Rules](#section-rules) — Required sections, ordering, and what makes each good
- [Anti-Patterns](#anti-patterns) — Known failure patterns to catch

### Supporting Files

- [Template](references/template.md) — Copy-paste starting point for spec.md
- [Section Guidance](references/section-guidance.md) — Why each section exists, with bad/good examples

---

## Why Project Specs Matter

AI coders make dozens of micro-decisions during implementation. Without a spec, those
decisions are uninformed — the AI guesses at conventions, misunderstands boundaries, and
builds against runtime constraints it doesn't know about. A project spec eliminates this by
documenting the context that code alone cannot convey: why the project exists, what's
actually implemented right now, how it behaves at its edges, and what the AI must never touch.

**The core insight:** The spec answers three questions: "What is this project? What does it
actually do right now? What are the rules?" Everything in the spec should serve one of these
questions. If it doesn't, it belongs in CLAUDE.md, in a change plan, or nowhere.

### What Belongs in spec.md vs CLAUDE.md

| spec.md | CLAUDE.md |
|---------|-----------|
| Why the project exists | Tech stack |
| Current state — what's actually implemented | Directory structure |
| Architecture overview and external dependencies | Development commands |
| Deployment & infrastructure | Build/test/lint commands |
| Testing strategy (what exists and what's missing) | Package manager |
| Boundaries & constraints | Environment setup |
| Ownership, known issues, tech debt | |

Do not duplicate content between the two. The spec covers context that goes deeper than what
CLAUDE.md provides.

---

## Key Principles

- **Include only what an AI cannot figure out by reading the code.** If the code makes it
  obvious, the spec shouldn't restate it. The spec's value is in the non-obvious.
- **The spec describes what IS implemented, not what will be.** If a section describes future
  plans, remove it or move it to a change spec. Aspirational content in spec.md actively
  misleads AI coders.
- **Current State is the most important section.** It must be updated after every significant
  implementation change. A stale Current State is the worst failure mode — it makes the spec
  worse than having no spec at all.
- **One real code snippet beats paragraphs of description.** Show the pattern, don't explain
  it in prose.
- **Exact commands, not vague instructions.** `npm run test -- --watch` not "run the tests."
- **Document boundary behavior.** How the system behaves at its edges — external system
  failures, timeouts, retry policies, degraded mode — shapes every implementation decision.
  This is the highest-signal content in the spec.
- **State boundaries as a three-tier system.** Always do / Ask first / Never do — this gives
  the AI clear escalation levels so it knows when to proceed, when to pause, and when to stop.
- **Capability constraints over failure modes.** What an API *can't* do (context window
  limits, no structured output, non-recursive listing) is often more valuable than what it
  can. These constraints shape protocol and algorithm design.

---

## Section Rules

### Mandatory Sections (in order)

| # | Section | Key Rule |
|---|---------|----------|
| 1 | What This Project Does | 2-4 sentences, product/purpose not technology |
| 2 | Why This Project Exists | Problem being solved; role in larger system if applicable |
| 3 | **Current State** | **Most important.** 2-4 concrete sentences about what IS implemented now. No future tense. Update after every significant change. |
| 4 | Architecture Overview | Key components + External Dependencies table (failure behavior + constraints) + optional Architecture Decisions table |
| 5 | Testing Strategy | Framework, location, how to run, what's well-covered AND what's missing |
| 6 | Deployment & Infrastructure | CI/CD pipeline, environments, hosting, deploy trigger |
| 7 | Boundaries & Constraints | Three-tier: Always Do / Ask First / Never Do |
| 8 | Ownership | Team or owner name, contact method |
| 9 | Known Issues | Currently broken things with severity and workaround. "None known." if clean. |
| 10 | Tech Debt | Deferred improvements with reason for deferral |

### Optional Subsections (within Architecture Overview)

| Subsection | When to Include |
|------------|-----------------|
| Architecture Decisions table | When significant non-obvious architectural choices have been made |
| Degraded mode paragraph | When key dependencies can be independently unavailable |

### Status Field

The header includes a Status field (`Draft | Active | Needs Update`). See
`references/section-guidance.md` for definitions of each value.

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
- **Aspirational NFRs.** "The app should be secure" is not actionable. Only include
  thresholds that are actively enforced or measured.
- **Flat service inventory in External Dependencies.** Listing services without failure
  behavior or constraints is useless — the AI can find what services exist from the code.
  The value is in what happens when they fail and what they can't do.
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
