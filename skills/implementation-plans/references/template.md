# Plan Templates

Templates for both the unified plan format and the distributed task file format.
Sections marked (required) must always be present. Sections in the Appendix are
required for Medium/Large plans; may be abbreviated for Bug Fix/Small plans per
the Right-Sizing Guide in implementation-plans.

## Contents

**Executor-facing (top of plan):**
- [Header](#header)
- [What We Are Building](#what-we-are-building-required)
- [Why This Exists](#why-this-exists-required)
- [Scope](#scope-required) — In, Out, Constraints
- [Downstream Impact](#downstream-impact-required)
- [Risks & Rollback](#risks--rollback-required)
- [Implementation Tasks](#implementation-tasks) — Task 0 + Task 1+
- [Critical Reminders](#critical-reminders-required--always-the-last-section-before-the-appendix)

**Appendix (requirements reference):**
- [Technical Context](#technical-context)
- [Edge Cases](#edge-cases)
- [Success Criteria](#success-criteria)
- [Dependencies & Assumptions](#dependencies--assumptions)
- [Key Decisions](#key-decisions)
- [Open Questions](#open-questions)

---

```markdown
# [Feature / Change Name] Plan

**Date**: [YYYY-MM-DD]
**Status**: [Draft | Open Questions | Approved | In Progress | Complete]
**Plan Size**: [Bug Fix | Small | Medium | Large]
**Author**: [name]
**Repository**: [repo name or path — if all tasks target the same repo]
**Project Spec**: [path to SPEC.md if it exists]

---

## What We Are Building (required)

[2-4 sentences. A plain, concrete description of what this change delivers — what will
exist or be different when done. No jargon, no implementation details. A non-technical
stakeholder should be able to read this and understand what they are getting.]

---

## Why This Exists (required)

[2-4 sentences. The problem, who has it, and why it matters. No technology. No solution
description. This grounds every decision that follows.]

---

## Scope (required)

### In
- [thing this change builds or fixes]

### Out (explicitly)
- [thing this change does NOT build] — [why if not obvious]
- [thing that could be confused as in-scope but is not]
- [[discussed during planning — deferred because ...]] for items that came up but were postponed

### Constraints (what must NOT change)
- [existing API contract, schema, or interface this change must preserve]
- [behavior callers depend on that must remain unchanged]

---

## Downstream Impact (required)

**Internal consumers**
- [module or code that calls/imports what changes] — [intended or side-effect impact]

**External consumers**
- [services, clients, or integrations outside this repo] — [how they are affected]
  If none: "External: None — this is an internal-only change."

**Implicit contracts**
- [behavior callers assume but isn't enforced in types or tests] — [preserved / changed]

---

## Risks & Rollback (required)

**Risks**
- **[Riskiest part]**: [what could go wrong] — Likelihood: [Low/Med/High], Impact: [Low/Med/High]

**Rollback Plan**
[Concrete steps to revert if this breaks production — deploy prior tag, revert specific
commit, run down-migration, feature flag off, etc. Not "we'll figure it out."]

---

## Implementation Tasks

### Task 0: Define Contracts & Interfaces

**Implementer:** AI | Human

**Covers:** Foundational — enables all tasks

**Relevant Files:**
- `src/[types]/[contracts].ts` <- create

**Context to Read First:**
- `src/[existing-types].ts:NN` — [what specific type/pattern to find and align with]

**Steps:**

1. [ ] Define shared types, API shapes, and interface boundaries
2. [ ] Verify types are consistent across task boundaries
3. [ ] Commit contracts so subsequent tasks can reference them

**Acceptance Criteria:**

- GIVEN the contracts file, WHEN imported by any task, THEN all shared types are
  available and compile without errors
- GIVEN the type definitions, WHEN compiled, THEN no type errors exist

**Verification Command:** `[compile / type-check command — e.g., tsc --noEmit]`

**Scope Boundaries:**
- This task's scope is limited to defining shared contracts, types, and interfaces
- Business logic belongs to subsequent tasks

---

### Task 1: [Complete Feature Unit]

**Implementer:** AI | Human
**Repository:** [repo name — only needed if story spans multiple repos]

**Covers:** AC-01.2, AC-01.4, Edge: [edge case name]

**Relevant Files:**
- `src/[module]/[file].py` <- create/modify
- `tests/[module]/test_[file].py` <- create/modify

**Context to Read First:**
- `src/[types]/[contracts].ts` — contracts defined in Task 0
- `src/[module]/models.py:NN` — [what specific function or pattern to find and reuse]

**Steps:**

1. [ ] Write failing tests based on the acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**

- GIVEN [precondition], WHEN [action], THEN [expected outcome]
- GIVEN [precondition], WHEN [action], THEN [expected outcome]
- GIVEN [precondition], WHEN [action], THEN [expected outcome]

**Verification:** [Prose description of what "done" looks like for this task.]

**Verification Command:** `[single command — e.g., pytest tests/[module]/test_[file].py -v]`

**Do NOT:**
- [Explicit anti-scope — what the implementer must avoid]
- [Work that belongs to a different task]

**Scope Boundaries:**
- This task's scope is limited to [specific concern this task owns]
- [Related concern] belongs to Task N

---

### Task 2: [Another Complete Unit]

**Implementer:** AI | Human
**Repository:** [repo name — only needed if story spans multiple repos]

**Blocked By:** Task N <- only if truly dependent; omit if this task can run in parallel

**Covers:** AC-02.1, AC-02.2

**Relevant Files:**
- `src/[module]/[file].py`
- `tests/[module]/test_[file].py`

**Context to Read First:**
- `src/[types]/[contracts].ts` — contracts defined in Task 0
- `src/[module]/[dependency].py:NN` — [what specific function or pattern to find and reuse]

**Steps:**

1. [ ] Write failing tests based on the acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**

- GIVEN [precondition], WHEN [action], THEN [expected outcome]
- GIVEN [precondition], WHEN [action], THEN [expected outcome]

**Verification:** [Prose description of what "done" looks like for this task.]

**Verification Command:** `[single command — e.g., pytest tests/[module]/test_[file].py -v]`

**Do NOT:**
- [Explicit anti-scope]
- [Work that belongs to a different task]

**Scope Boundaries:**
- This task's scope is limited to [specific concern]
- [Other concern] belongs to Task N

---

## Critical Reminders (required — always the last section before the Appendix)

**For the executor: read this before dispatching any task.**

- **Must not change**: [restate the 2-3 most important Constraints verbatim]
- **Highest risk**: [restate the single most dangerous Risk verbatim]
- **Rollback**: [one-line rollback summary]
- **File boundaries**: Each task ONLY touches its declared Relevant Files. If a step
  would require touching a file not in the task's Relevant Files list, STOP and report.

---

## Appendix: Requirements Detail

*Reference material for planning and review. Executors read tasks above; this appendix
provides the "why" behind them.*

### Technical Context

[Brief description of the technology landscape. Only include what an executing agent
needs to make informed decisions. This is the ONE section where technology names belong.]

- **Platform**: [e.g., iOS/SwiftUI, Rails web app, Node.js CLI]
- **Relevant systems**: [e.g., existing auth middleware, notification service]
- **Constraints**: [version requirements, API boundaries — do not repeat Scope Constraints verbatim]

### [Domain-Specific Section(s)] (optional)

[Include tables, entity descriptions, or domain knowledge that acceptance criteria
reference. Use when the domain has structured data. Not every change needs this.]

### Edge Cases

- **[Boundary condition]**: [expected behavior]
- **[Error scenario]**: [expected behavior]
- **[Unusual input or state]**: [expected behavior]

### Success Criteria

[Measurable outcomes that define "done" beyond feature checkboxes. Every criterion
must include a number or threshold.]

1. [metric] [direction] by [amount] within [timeframe]
2. Zero reported cases of [specific failure]

### Dependencies & Assumptions

**Dependencies**
- [external system, service, or team this depends on]

**Assumptions**
- [thing assumed true that, if false, changes the plan] — if false: [consequence]

### Key Decisions

- **[Decision topic]**: [Chosen approach] — [Why, and what alternatives were rejected]

#### Failed / Rejected Approaches

- **[Approach name]**: Rejected because [specific reason] — [prevents re-exploring this path]

### Open Questions

**All open questions must be resolved before implementation begins.**

- [ ] [question requiring human decision]
  - Context: [why this matters and what depends on the answer]
  - Options considered: [list viable options if known]
  - Decision:
  - Reasoning:
```

---

## Distributed Format Templates

The distributed format splits a plan into individual files. This is the default
output of `/task-decomposition`. The unified template above is used as a transient
artifact for reviewers.

### plan-summary.md Template

Contains all plan-level information. Does NOT contain individual task definitions.

```markdown
# [Feature / Change Name] Plan

**Date**: [YYYY-MM-DD]
**Status**: [Draft | Open Questions | Approved | In Progress | Complete]
**Plan Size**: [Bug Fix | Small | Medium | Large]
**Author**: [name]
**Story**: [story ID — e.g., story_001]
**Repositories**: [list of repo names or paths involved]
**Project Spec**: [path to SPEC.md if it exists]

---

## What We Are Building (required)

[2-4 sentences. Same guidance as unified template.]

---

## Why This Exists (required)

[2-4 sentences. Same guidance as unified template.]

---

## Scope (required)

### In
- [thing this change builds or fixes]

### Out (explicitly)
- [thing this change does NOT build] — [why if not obvious]

### Constraints (what must NOT change)
- [existing API contract, schema, or interface this change must preserve]

---

## Downstream Impact (required)

**Internal consumers**
- [module or code that calls/imports what changes] — [impact]

**External consumers**
- [services, clients, or integrations outside this repo] — [impact]

**Implicit contracts**
- [behavior callers assume but isn't enforced] — [preserved / changed]

---

## Risks & Rollback (required)

**Risks**
- **[Riskiest part]**: [what could go wrong] — Likelihood: [L/M/H], Impact: [L/M/H]

**Rollback Plan**
[Concrete steps — not "we'll figure it out."]

---

## Parallel Execution Schedule

```
Critical path: Task 0 → Task 1 → Task 4 (3 batches minimum)
Batch 1 (parallel): Task 1, Task 2, Task 3
Batch 2 (parallel): Task 4 (blocked by Task 1), Task 5 (blocked by Task 2)
Batch 3: Task 6 (blocked by Task 4, Task 5)

Total: N tasks, M batches
```

---

## Critical Reminders (required)

**For the executor: read this before dispatching any task.**

- **Must not change**: [restate 2-3 most important Constraints verbatim]
- **Highest risk**: [restate single most dangerous Risk verbatim]
- **Rollback**: [one-line summary]
- **File boundaries**: Each task ONLY touches its declared Relevant Files

---

## Appendix: Requirements Detail

### Technical Context
[Same as unified template]

### Edge Cases
[Same as unified template]

### Success Criteria
[Same as unified template]

### Dependencies & Assumptions
[Same as unified template]

### Key Decisions
[Same as unified template]

### Open Questions
[Same as unified template]
```

### task.md Template

One file per task, stored at `tasks/task-N/task.md`.

```markdown
# Task N: [Brief description]

**Status**: Not Started
**Implementer**: AI | Human
**Repository**: [repo name or path]
**Blocked By**: Task M [optional — only if truly dependent]
**Covers**: AC-01.2, AC-01.4, Edge: [edge case name]

**Relevant Files:**
- `src/[module]/[file].py` <- create/modify
- `tests/[module]/test_[file].py` <- create

**Context to Read First:**
- `src/[types]/[contracts].ts` — [specific type/pattern to align with]
- `src/[module]/models.py:NN` — [specific function or pattern to reuse]

**Steps:**
1. [ ] Write failing tests based on acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**
- GIVEN [precondition], WHEN [action], THEN [expected outcome]
- GIVEN [precondition], WHEN [action], THEN [expected outcome]

**Verification:** [Prose description of what "done" looks like for this task. What
compiles, what tests pass, what behavior is observable. Should be concrete enough
that someone can check it without reading the full acceptance criteria.]

**Verification Command:** `[single runnable command]`

**Do NOT:**
- [Explicit anti-scope — what the implementer must avoid doing in this task]
- [Common mistake or temptation to guard against]
- [Work that belongs to a different task — reference which one]

**Scope Boundaries:** [What this task owns] / [Related concerns that belong to Task N]

**Execution Notes:**
[Empty initially — populated during /execute with failure details, retry guidance,
and deviation notes]
```

**Task 0 variant** — uses contract verification steps instead of TDD:

```markdown
# Task 0: Define Contracts & Interfaces

**Status**: Not Started
**Implementer**: AI
**Repository**: [repo name — or omit if single-repo]
**Covers**: Foundational — enables all tasks

**Relevant Files:**
- `src/[types]/[contracts].ts` <- create

**Context to Read First:**
- `src/[existing-types].ts:NN` — [what specific type/pattern to align with]

**Steps:**
1. [ ] Define shared types, API shapes, and interface boundaries
2. [ ] Verify types are consistent across task boundaries
3. [ ] Commit contracts so subsequent tasks can reference them

**Acceptance Criteria:**
- GIVEN the contracts file, WHEN imported by any task, THEN all shared types are
  available and compile without errors

**Verification:** [Prose — e.g., "Module compiles. Protocol and event struct are
importable from other modules. No runtime behavior."]

**Verification Command:** `[compile / type-check command]`

**Do NOT:**
- [e.g., Implement business logic — that belongs to subsequent tasks]
- [e.g., Add dependencies on modules that don't exist yet]

**Scope Boundaries:** Contracts and types only — zero business logic

**Execution Notes:**
```
