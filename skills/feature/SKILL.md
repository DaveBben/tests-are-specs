---
name: feature
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[feature description or change request]"
description: >
  Feature planning skill. Takes a feature or change request, researches the
  codebase, produces a plan with real code snippets, then decomposes into
  tasks compatible with /cks:execute. Human reviews the plan before task
  breakdown. Do NOT use for bugs (use /cks:bug). Do NOT use for trivial
  one-line changes (just make the change).
---

# Feature Planner

Three phases: **Scope → Plan → Tasks**. All artifacts written to
`.claude/features/{slug}/`.

```
User describes feature → /cks:feature
  Phase 1: Scope (confirm intent, explore codebase, write plan.md draft)
  Phase 2: Review (user annotates plan, 1-4 cycles)
  Phase 3: Tasks (decompose into task JSONs for /cks:execute)
```

## Input Handling

1. **Existing feature directory**: Resume from last incomplete phase.
2. **Free-form text**: Generate a URL-safe slug, create directory, Phase 1.
3. **No input**: Ask user to describe the feature.

---

## Phase 1: Scope and Plan

### Step 1 — Confirm Intent

Evaluate `$ARGUMENTS` against two questions:
- **What** changes does the user want? (the concrete change)
- **Why** is this change needed? (the motivation)

If both are clear, state your understanding and ask the user to confirm.
If either is unclear, ask for the missing piece. Do not guess at "why."

Then ask: *"Is there context outside this codebase I should know — specs,
other repos, business constraints, URLs? If not, say 'no'."*

If URLs provided, fetch and summarize. If other repo paths, record them
for the `repository` field in task JSONs.

### Step 2 — Five Scope Questions

Generate **5 targeted questions** specific to this feature — things only
the user knows that code cannot answer. Present all 5 at once. Good
questions target: scope boundaries, backwards compatibility, user-facing
vs internal, integration expectations, quality bar.

**Do not use generic questions.** Each must reference this specific feature.

### Step 3 — Codebase Exploration

Read CLAUDE.md and any architecture/spec docs if they exist. Summarize
only the parts relevant to this feature — do not dump full contents into
the plan.

From the user's scope answers, generate **5 exploration questions** that
trace the downstream ripple of the change. Launch Explore agents with
these questions. Each answer MUST include `file:line` evidence or an
explicit "not applicable" with justification. Instruct agents to **stop
searching once they have `file:line` evidence** for a question — do not
continue looking for additional supporting evidence.

Also answer three mandatory questions:
1. Where does this belong? (specific modules, directories, files)
2. Does something similar exist to extend rather than duplicate?
3. Have we solved a related problem whose pattern applies?

If any exploration question lacks a `file:line` answer, launch a
follow-up agent for that specific question before proceeding.

### Step 3b — Identify At-Risk Tests

For every file being modified, trace its test dependents: which existing
tests import, mock, or exercise this code? Record as `atRiskTests` per
task — the single highest-leverage context for preventing regressions.

### Step 4 — Write plan.md

Write `.claude/features/{slug}/plan.md` using the
[plan.md template](references/templates.md#planmd). Key requirements:

- **Actual code snippets** — real signatures, schemas, data shapes. Not
  pseudocode. When a reference implementation exists, paste it alongside
  the proposed change.
- **Omit empty sections** — a shorter, focused plan outperforms a
  comprehensive one. If a template section has no meaningful content,
  leave it out entirely.
- **Impact table** — every file that will be created, modified, or
  deleted, with symbols and reasons.
- **"What NOT to Do"** section with explicit boundaries.
- **Delivery strategy** — under ~500 lines total: single PR. Over: vertical
  slices. Never slice horizontally.
- End with "Do not implement yet."

### Step 5 — Verify Plan

Launch the `plan-verifier` agent. It checks that every `file:line`
reference, type, and function signature in the plan actually exists.
Apply any `@FIX:` corrections before showing the user.

### Step 6 — Present for Review

> "The plan is at `.claude/features/{slug}/plan.md`. You can:
> 1. **Annotate** — add `@NOTE:`, `@FIX:`, or `@REMOVE:` inline, then
>    say 'review'
> 2. **Give feedback in chat**
> 3. **Approve** — say 'approve'"

---

## Phase 2: Annotation Cycle

Process annotations when the user says "review" or gives chat feedback:

1. Re-read the Scope and Constraints sections of `plan.md` first —
   these degrade in attention over long conversations
2. Read the full `plan.md`, find all `@NOTE:` / `@FIX:` / `@REMOVE:` markers
3. Address **every** annotation — do not skip any
4. Remove markers, write updated plan, present what changed

Track cycles with `<!-- annotation-cycle: N/4 -->` in plan.md. After 4
cycles without approval, suggest reconsidering scope.

On "approve": set Status to Approved, proceed to Phase 3.

---

## Phase 3: Task Breakdown

### Task Granularity

- **Single concern** — 1-3 files (hard max 4). Route + controller + types
  = one concern. Auth + schema + frontend = three concerns.
- **Count decisions, not lines.** 200 lines / one decision > 30 lines /
  three decisions. Target under 200 lines per task.
- **Size ceiling**: over 50 tasks means the feature needs splitting.

### Vertical Slices

Assign every task to a slice. Each slice = complete vertical path (DB +
service + API + test), never a horizontal layer. Each must be reviewable
in 15 minutes and have exactly one reason it would be reverted.

### Task Content

Each task MUST contain:
- **files** — explicit paths (1-3 files, hard max 4)
- **symbol** — specific function or type to create/modify
- **reference** — existing pattern to follow (`file:line`)
- **intent** — one sentence: *why* this task exists, so the agent can
  resolve ambiguities at decision points (not what it does — why)
- **atRiskTests** — existing test files/functions that could regress
  from this change (from Step 3b). Empty only if no existing tests
  touch the affected code.
- **blockedBy** — task IDs that must complete first. Set this when a
  task creates a type, interface, or migration that later tasks consume.
- **doNot** — at least one explicit boundary
- **acceptanceCriteria** — GIVEN/WHEN/THEN format
- **verificationCommand** — single runnable command
- **doneWhen** — mechanically verifiable condition

Context constraints (more context degrades execution):
- **testContext**: max 3 entries. Interfaces and types only.
- **implementationContext**: max 3 entries. Pattern references only.

Use RFC 2119 keywords: MUST = hard requirement, SHOULD = strong
preference, MAY = full discretion.

### Steps

1. Write `.claude/features/{slug}/tasks.md` using the
   [tasks.md template](references/templates.md#tasksmd)
2. Write task JSONs to `tasks/` — `plan.json` + `task_{N}.json` per task.
   See [JSON schemas](references/templates.md#task-json-schemas)
3. **Validate** each task JSON:
   - `files` has 1-4 entries. More than 4 is a planning error — split.
   - Every path in `files`, `testContext`, `implementationContext` exists
     on disk or has a matching `relevantFiles` entry with `action: "create"`
   - `doNot`, `acceptanceCriteria` non-empty; `doneWhen` non-empty
   - `intent` is non-empty and explains *why*, not *what*
   - No path appears in both `testContext` and `implementationContext`
   - `verificationCommand` contains a recognizable test runner command
4. Present tasks to the user:
   > "Task breakdown complete — {N} tasks. Review or run
   > `/cks:execute .claude/features/{slug}`"
