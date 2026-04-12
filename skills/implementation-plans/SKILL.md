---
name: implementation-plans
description: >
  Provides the standards, validation rules, and templates for implementation plans
  (both unified plan.md files and distributed task files). Use when creating or
  reviewing plans. Preloaded by task-decomposition, execute, and review agents.
  Do NOT invoke directly — this is a reference consumed by other skills.
user-invocable: false
disable-model-invocation: true
---

# Implementation Plan Standards

Last updated: 2026-04-10

---

## Contents

- [Why Plans Matter](#why-plans-matter) — Philosophy and core insight
- [Key Principles — Requirements](#key-principles--requirements) — Rules for the requirements half
- [Key Principles — Tasks](#key-principles--tasks) — Rules for the implementation half
- [Anti-Patterns](#anti-patterns) — Known failure patterns to catch
- [Specificity Calibration](#specificity-calibration) — Too Vague vs Just Right
- [Right-Sizing Guide](#right-sizing-guide) — How much plan for each change type
- [Task Sizing](#task-sizing) — How big each task should be
- [TDD Cycle](#tdd-cycle) — The RED/GREEN pattern every task follows
- [Validation Checklist](#validation-checklist) — Pre-finalization gate
- [Special Cases](#special-cases) — Exploration, refactor, and bug fix plans
- [Distributed Task Storage](#distributed-task-storage) — Individual task files vs unified plan

### Supporting Files

- [Template](references/template.md) — Copy-paste starting point for plan.md
- [Section-by-Section Guidance](references/section-guidance.md) — Why each section exists, with bad/good examples
- [Worked Example](examples/notification-unsubscribe.md) — Complete filled-in plan
- [Pipeline Overview](references/pipeline-overview.md) — Where plans fit in the multi-stage pipeline

---

## Why Plans Matter

AI coders make dozens of micro-decisions during implementation. Without a plan, those decisions
are arbitrary — the AI guesses at scope, invents edge cases, and builds features nobody asked
for. A change plan eliminates this by making requirements explicit, scope binary, and success
measurable. The magic is not in writing plans — it is in using the interview process to discover
what the requirements actually are.

**The core insight:** "You would debug the blueprint, not the actual app. Fix/debug the plan,
not the code being written."

A plan combines both WHAT/WHY (requirements, scope, edge cases) and HOW (implementation task
breakdown). The requirements sections are technology-agnostic. The task sections ground those
requirements in real code. Plans can be stored as a single unified file or as distributed
task files (see [Distributed Task Storage](#distributed-task-storage)).

### When a Plan Is Needed

Use a change plan when the change would take more than 5 minutes to explain to a new team
member — that complexity threshold is where undocumented requirements start causing bugs.

### When to Skip

- Trivial one-line fixes where the change is obvious
- Hot fixes in production emergencies (document retroactively after)
- Pure exploratory/spike work (write an "Exploration Plan" instead — see Special Cases)

---

## Key Principles — Requirements

- **"Why" comes first.** The opening states the problem and its real-world impact — no
  technology, no solution description.
- **Scope is binary.** If something is not listed as In, the AI must not build it. If something
  could be confused as In, list it explicitly as Out. The Out section is as important as the In.
- **Technology-aware context, technology-agnostic requirements.** The plan's Technical Context
  section may name the platform, frameworks, and relevant existing systems — this grounds the
  plan in reality. But acceptance criteria, edge cases, and success criteria
  describe WHAT and WHY in behavioral terms, never HOW. No technology names in ACs. No
  framework choices in edge cases. Implementation details surface in the task sections.
- **Acceptance criteria use GIVEN/WHEN/THEN.** Each AC follows "GIVEN [precondition], WHEN
  [action], THEN [expected outcome]" — this maps directly to test cases and eliminates
  ambiguity about what "working" means.
- **Edge cases are explicit.** The happy path is obvious. Edge cases are where silent bugs live.
  Every edge case in the plan becomes a test scenario.
- **Success criteria have numbers.** Not feature checkboxes. "Zero reported cases of X" and
  "30% reduction in Y within 60 days" define done in a way that survives scope creep.
- **Open Questions are blockers.** Any non-trivial product or scope decision must be
  surfaced as an open question for the human to investigate and decide — do not make these
  choices silently. Architecture and code decisions also surface as open questions when they
  cannot be resolved without human input.

---

## Key Principles — Tasks

- **One task, one concern.** Each task has a clear, focused scope with an explicit set of
  files it touches. Each task's Relevant Files list defines its boundary — no file should
  appear in multiple tasks unless necessary for a declared dependency.

- **Contract-first: Task 0 is mandatory.** Every plan starts its task section with Task 0
  that defines shared boundaries — API shapes, type definitions, interface contracts, config
  schemas. Without this, agents guess at interfaces and produce incompatible code.

- **Every task is a complete TDD cycle.** Each task (except Task 0) writes its own failing
  tests AND implements the code to make them pass. RED then GREEN within the same task.
  Never split tests and implementation across separate tasks.

- **Zero-context readability.** Use explicit file paths (`create src/utils/helpers.ts` not
  `create a utility file`). List files to read before starting each task. Document WHY each
  context file matters.

- **No design decisions inside tasks.** If a task requires choosing between approaches,
  that choice must be resolved in Key Decisions or Open Questions before the task is written.

- **Scope Boundaries prevent scope creep.** Every task must have a Scope Boundaries section
  that states what this task owns and where adjacent concerns live, using positive framing.

- **Verification describes "done" in prose.** Every task includes a `**Verification:**`
  section — a plain prose description of what "done" looks like (e.g., "Module compiles.
  Watcher detects new .m4a files in a temp directory. Tests pass."). More concrete than
  acceptance criteria alone.

- **Do NOT guards against common mistakes.** Every task includes a `**Do NOT:**` section
  listing explicit anti-scope — what the implementer must avoid doing (e.g., "Do NOT
  implement actual monitoring — that's Task 1.2"). References which task owns excluded work.

- **Implementer labels control execution.** Every task includes `**Implementer:** AI | Human`.
  Default to `AI`. `/execute` dispatches AI tasks to code-writer agents and pauses at Human
  tasks for the engineer to complete manually.

- **Context budget awareness.** Keep under 15 tasks. If more are needed, split into multiple
  plan directories that execute sequentially.

---

## Anti-Patterns

While drafting or reviewing, verify the plan does NOT contain:

- **Solution masquerading as a requirement.** "Use PostgreSQL to store preferences" is
  architecture. "User preferences persist across sessions and devices" is a requirement.
  Technology names belong in the Technical Context section, not in acceptance criteria.
- **Vague acceptance criteria.** "The feature works correctly" is not testable. Rewrite until
  every AC has a yes/no verification.
- **Missing Out section.** A plan with no Out section has infinite scope. Always list what is
  NOT being built.
- **No edge cases.** A plan with only happy path produces software that only works on the happy
  path.
- **Problem statement that describes the solution.** "Build a notification preferences page" is
  a solution. "Users are disengaging because they receive too many irrelevant notifications" is
  a problem.
- **Unstated assumptions.** If something is assumed true, say so in Dependencies & Assumptions.
- **Missing or thin Open Questions.** If the change is complex enough to need a plan, it almost
  certainly has open questions. An empty Open Questions section usually means the author did not
  think hard enough about ambiguities.
- **Silently resolved product decisions.** Non-trivial product or scope decisions that
  appear as settled requirements when they were never explicitly decided.
- **Hidden intra-task dependencies.** If Task 3 silently depends on Task 2's output but
  does not declare `Blocked By: Task 2`, the executor may run them out of order.
- **Untraced requirements.** Every acceptance criterion must map to at least one task's
  `Covers:` annotation. If a requirement has no task covering it, create one or defer it
  explicitly.
- **Oversized tasks.** A task titled "Add user preferences API" may actually be three tasks.
  Count the "ands" in the description.
- **Missing Constraints section.** A plan with no Constraints gives the executing agent
  freedom to change interfaces, schemas, or contracts that other code depends on. Always
  state what must not change.
- **Missing Downstream Impact.** Failing to name who calls or depends on the changed code
  means the executing agent has no signal to stop if it is about to break a consumer.
- **Missing Verification Command per task.** Without a single runnable command per task,
  the agent decides for itself when the task is done. Correctness is not declared — it is
  verified.

---

## Specificity Calibration

| Too Vague | Just Right |
|---|---|
| "Handle errors gracefully" | "If the save fails, revert the toggle and show an error toast within 3 seconds" |
| "Support multiple user types" | "Admin users see all categories; regular users see only subscribed categories" |
| "Fast page load" | "Landing page renders in < 2 seconds on 3G connections" |
| "Secure authentication" | "Unsubscribe links use signed tokens that expire after 30 days" |
| "Good user experience" | "Toggling a category takes one click; confirmation appears without page reload" |

If a requirement reads like the left column, rewrite it until it reads like the right column.

---

## Right-Sizing Guide

Set `**Plan Size**` in the plan header to match. If the plan exceeds the line ceiling
for its size, delete prose — not file paths.

### Bug Fix (Plan Size: Bug Fix) — 20-60 lines total
Include: What, Why, Scope, Risks & Rollback, Tasks, Critical Reminders
Appendix: Include a "Bug Description" section (reproduction steps + expected vs actual)
Skip: Domain sections, Downstream Impact (unless external consumers are affected)
Line ceiling: 60 lines. Trim if over.

### Small Feature (Plan Size: Small) — 60-120 lines total
Include: All required sections
Minimize: Appendix ACs (2-3 per task), Open Questions (resolve during interview)
Line ceiling: 120 lines. Trim if over.

### Medium Feature (Plan Size: Medium) — 120-250 lines total
Include: All sections
Add: Domain-specific tables as needed, 4-5 ACs per task, more edge cases
Line ceiling: 250 lines. Trim if over.

### Architecture Change (Plan Size: Large) — 150-350 lines total
Include: All sections with extra depth
Add: Detailed Downstream Impact, migration steps, rollback criteria in detail
Success criteria: both behavioral metrics AND operational metrics
Line ceiling: 350 lines. Trim if over.

---

## Task Sizing

### Target: 50-200 lines per task

Each task should produce a small, focused, independently reviewable change:
- **Above 200 lines:** actively look for a natural split
- **Above 400 lines:** split is mandatory — no exceptions

| Too Big | Just Right |
|---------|------------|
| "Implement the user preferences feature" | "Add preference repository with CRUD operations" |
| "Build the API and write tests" | "Add GET /preferences endpoint returning user prefs as JSON" |
| "Set up the frontend page with all interactions" | "Add preference toggle component with optimistic update" |

Split a task if: it would produce more than 200 lines, the description contains "and" more
than once, or completing it would require making an undiscussed architectural choice.

---

## TDD Cycle

Every task (except Task 0) follows this exact four-step sequence — no exceptions:

```
1. [ ] Write failing tests based on the acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)
```

**Task 0 is the exception.** It defines contracts and interfaces verified by compilation
or type checking, not TDD.

**The Nyquist Rule:** Every task must have an automated verification command. If no test
infrastructure exists, add a prerequisite task that creates it.

---

## Validation Checklist

### Must-Pass Gate (print each result before presenting plan to user)

These 9 items are hard gates. For each one, print: `[PASS]` or `[FAIL — reason]`.
If any item is FAIL, fix it before proceeding. Do not present a plan with any FAIL.

```
1. [ ] Every AC in the Appendix uses GIVEN/WHEN/THEN format
2. [ ] Every task has a single runnable Verification Command (not "run the tests")
3. [ ] Every task has Relevant Files with explicit, full paths
4. [ ] Constraints section is non-empty (lists what must NOT change)
5. [ ] Downstream Impact section is non-empty (names at least one consumer)
6. [ ] Every task has a Covers: annotation linking it to at least one AC or edge case
7. [ ] Critical Reminders section exists as the last section before the Appendix
8. [ ] Every task has an Implementer: AI | Human label
9. [ ] Repository field present (header-level if single repo, per-task if multi-repo)
10. [ ] Every task has a Verification: section (prose description of done)
11. [ ] Every task has a Do NOT: section (explicit anti-scope)
```

### Should Also Verify (reference — check where time permits)

- "Why This Exists" describes the problem, not the solution
- Scope has In, Out, and Constraints subsections
- Downstream Impact covers internal, external, and implicit contracts
- ACs are behavioral (no technology names, no framework references)
- Edge cases are explicit with expected behaviors
- Success criteria have numbers confirmed by the user
- Risks & Rollback names specific risks and a concrete rollback plan
- Task 0 defines all shared contracts and interfaces
- Every task (except Task 0) is a complete TDD cycle — tests AND implementation
- Every task has Scope Boundaries (positive framing — what this task owns)
- Every task has Context to Read First with file:line references
- Every task targets 50-200 lines (hard ceiling: 400)
- Total tasks do not exceed 15
- Failed / Rejected Approaches documented where alternatives were evaluated
- Open Questions section exists in the Appendix

---

## Special Cases

### Exploration Plan
For spike/research work, write a lightweight plan that defines:
- What are we trying to learn?
- What is the time box? (e.g., "2 hours maximum")
- What constitutes a successful exploration? (e.g., "We know whether approach X is feasible")
- What happens after? (e.g., "Write a proper plan for the implementation")

### Refactor Plan
For refactoring, the plan should:
- State what is wrong with the current code and why it matters (not "it's messy" — quantify)
- Define the desired end state in behavioral terms (same behavior, different structure)
- List what must NOT change (external interfaces, test behavior, API contracts)
- Include a success criterion: "All existing tests pass without modification"

### Bug Fix Plan
For bug fixes, the plan should:
- Describe the bug with reproduction steps
- State the expected vs actual behavior
- Define the fix criteria (what "fixed" looks like)
- List related edge cases that should be tested while fixing

---

## Distributed Task Storage

Plans can be stored in two formats: **unified** (single file) or **distributed**
(individual task files). The distributed format is the default output of
`/task-decomposition`. The unified format is used as a transient artifact for
reviewers and as a legacy/convenience reference.

### Distributed Format (default)

Tasks are stored as individual JSON files in the artifacts directory:

```
~/.claude/backlog-driven-development/artifacts/
  stories/story_NNN.json             # story artifact
  plan-summaries/plan_NNN.json       # plan-level information (keyed to story number)
  tasks/task_NNN.1.json              # Task 1
  tasks/task_NNN.2.json              # Task 2, etc.
```

**plan_NNN.json** contains all plan-level sections: Header, What We Are Building,
Why This Exists, Scope, Downstream Impact, Risks & Rollback, Parallel Execution
Schedule, Critical Reminders, and the full Appendix. It does NOT contain individual
task definitions.

**task_NNN.N.json** contains one task with all task-level fields: status, implementer,
repository, blockedBy, covers, relevantFiles, contextToReadFirst, changes, tests,
doneWhen, verificationCommand, and doNot.

### Unified Format (transient / legacy)

A single file at `.claude/implementation-plans/{slug}.md` containing both plan-level
sections and all tasks inline. This format is:
- Assembled temporarily by `/task-decomposition` for plan-reviewer and
  test-reviewer consumption
- Optionally kept as a convenience reference after task files are written
- The format used by plans created before the distributed format was introduced

### Task Status Field

Each task JSON includes a `status` field tracking execution progress:
- `Not Started` — initial state after `/task-decomposition`
- `In Progress` — set by `/execute` when the task begins
- `Done` — set by `/execute` after verification passes
- `Blocked` — set when a dependency fails
- `Failed` — set when the task itself fails

### Execution Notes

Each `task-N/task.md` includes an **Execution Notes** section at the bottom, initially
empty. During `/execute`, failure details and retry guidance are appended here. This
persists across session resumptions so future attempts skip known dead ends.

### Validation

The Validation Checklist (Must-Pass Gate) applies equally to both formats. When
validating distributed tasks, check across `plan-summary.md` + all `task-N/task.md`
files as a whole.
