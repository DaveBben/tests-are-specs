---
name: execute
disable-model-invocation: true
effort: high
argument-hint: "[feature or bug directory path or slug]"
model: opus
description: >
  Implements approved tasks from /cks:feature or /cks:bug. For each task:
  dispatches a single implementation agent.
  After all tasks: full test suite, finalize. Does not
  commit, push, or create PRs.
---

# Plan Executor

Execute approved tasks. For each task: implement.
After all tasks: full tests → finalize.

### Supporting Files

- [PR Templates](references/pr-templates.md) — Feature and bugfix PR body templates
- [Resumption](references/resumption.md) — Checkpoint format and session resumption
- [Error Handling](references/error-handling.md) — Plan deviation responses
- [Design Decisions](references/design-decisions.md) — Rationale for single-agent and no-TDD choices

## Execution Model

```
Main session:
  ├── Input resolution → load plan.json + task JSONs
  ├── Pre-flight (branch, validate, test baseline)
  ├── For each task (sequential):
  │   ├── Pre-task check
  │   ├── Implementation agent (single agent — reads task, implements, verifies)
  │   └── Update task status
  ├── Full test suite + lint
  └── Finalize (user handles push + PR)
```

---

## Input Resolution

Resolve `$ARGUMENTS`:

1. **Feature/bug directory path**: Verify `tasks/plan.json` exists.
2. **Slug**: Try `.claude/features/{slug}/` then `.claude/bugs/{slug}/`.
3. **No input**: Glob for available plans, present choices.

Determine source type from path (`feature` or `bugfix`) for branch naming.

Load `plan.json` + all `task_*.json` files sorted by numeric ID. If
`execution-state.json` exists, follow
[resumption procedure](references/resumption.md).

---

## Pre-flight

### Branch Safety (hard stop)

If on `main`/`master`: create `feature/{slug}` or `bugfix/{slug}`. If on
another branch: confirm with user. Never execute on main.

### Validate Task JSONs

For each task:
- `files` paths exist (modify) or don't exist (create)
- `testContext` and `implementationContext` paths exist
- `doNot`, `acceptanceCriteria` non-empty; `doneWhen` non-empty
- `verificationCommand` is syntactically valid

Critical violations → report and ask. Minor issues → warn and continue.

### Test Baseline

Run full test suite. Record passing count and known failures. During
execution, the agent only needs to ensure: new tests pass + baseline
tests still pass + known failures are ignored.

### Spec Freshness Check

If the project has a root `spec.md`, check its `Last verified` date.
If older than 30 days: warn the user that the spec may be stale and
recommend running `/cks:onboard` to refresh before executing.

If any task touches files in a directory with its own domain `spec.md`,
check that domain spec's `Last verified` date too. Stale domain specs
are a silent failure mode — agents trust them absolutely.

Do not block execution on stale specs — warn and continue.

### Gate Check

- `plan.json` status is `Approved`
- Read `constraints` and `criticalReminders` — passed to every agent

---

## Fast Path (Small Plans)

If the plan has **≤3 tasks** and total estimated size is **under 200
lines**, skip task-by-task execution:

1. Dispatch a single implementation agent with the full plan context
   (all task JSONs, plan constraints, all atRiskTests merged)
2. If agent returns DONE and all regressionChecks pass: proceed to Post-Implementation
3. If agent STOPs or exceeds 200 lines: fall back to standard
   task-by-task execution below

This avoids the per-task overhead (dispatch, status update)
when the total work fits comfortably in a single agent context.

---

## Task Execution

Create TodoWrite entries for all tasks for user visibility.

### Slice-Aware Execution

If `totalSlices > 1`: process sequentially. Each slice = branch →
tasks → post-implementation → finalize. Slice 1 branches from main;
subsequent slices branch from previous (stacked PRs).

### Complexity Tier

Before dispatching each task, classify it:

| Tier | Criteria | Agent Config |
|------|----------|-------------|
| **Simple** | 1 file, clear reference, no interface changes | maxTurns: 20, model: haiku |
| **Standard** | 2-3 files, or 1 file with interface changes | maxTurns: 50, model: sonnet (default) |
| **Complex** | 4 files, or touches shared interfaces/types | maxTurns: 75, model: sonnet, also pass `evidence.md` and full interface files (ignore testContext/implementationContext caps) |

If a Simple task agent STOPs or hits maxTurns, retry once at Standard
tier before marking BLOCKED.

### For Each Task

#### Step 1: Pre-task Check

- Do `relevantFiles` paths match expected state (exist/not-exist)?
- Is `git status` clean?
- If `blockedBy` lists tasks that aren't DONE, skip and report.

If assumptions violated, ask the user.

#### Step 2: Implement

Dispatch the `code-implementor` agent via Agent tool
(`subagent_type: "code-implementor"`). Pass it:
- Task JSON path
- Plan JSON path (for constraints)
- Test baseline (known failures to ignore)
- Plan constraints verbatim
- Task's `doNot` and `dependencyChain` fields verbatim
- Instruction: after completing edits but before running verification,
  re-read the task's `doNot` and plan `constraints` to check compliance.
  This counters instruction fade-out over long implementation runs.

If agent returns STOPPED: mark task `BLOCKED`, record reason in
`executionNotes`, ask user how to proceed.

If succeeded, **trust-but-verify**: run the task's `regressionCheck`
command (if non-empty) from the orchestrator — do not rely solely on
the agent's self-reported test results. If at-risk tests fail: send
the agent back to fix. If still failing after one retry: mark task
`BLOCKED`, record which tests broke.

#### Step 3: Size Check

```
git diff --stat HEAD
```

If task exceeds 200 lines: note in `executionNotes`, inform user.
If cumulative slice diff exceeds 500 lines: warn user, ask whether to
continue or split.

#### Step 4: Drift Check

If the agent used **>80% of its maxTurns** (e.g. >40 of 50), flag the
task: "High turn count — possible drift or difficulty."

#### Step 5: Update Status

Set task to `DONE` (or `BLOCKED`). Update `execution-state.json`.
Mark TodoWrite entry completed.

#### Step 6: Observation Masking

After updating status, mentally discard the full agent output and diff
stats from completed tasks. Retain only a one-line summary per prior
task: `"Task N: DONE|BLOCKED, X files, Y lines"`. Keep the **last 2
tasks'** full results for continuity. This prevents stale observation
tokens from crowding out the current task's context.

### Context Pause Gate

After every **6 completed tasks**, pause: report progress, tasks
remaining. Ask user to check `/context` and either continue or start
a fresh session (resumption picks up automatically).

### Blocked Tasks

If any agent STOPs: record reason, set `BLOCKED`, check `blockedBy`
dependents, ask user whether to continue with unblocked tasks or stop.

---

## Post-Implementation

Run only when ALL tasks in the current slice are complete.

### Step 1: Full Test Suite + Lint

Run full tests and linting. Fix any failures.

### Step 2: Update spec.md

If `spec.md` exists and feature changes capabilities in `## Current State`,
update to reflect what was built.

---

## Finalize

1. Set plan.json status to `COMPLETE`
2. Present summary: branch, task results, findings fixed/remaining
3. Point to [PR templates](references/pr-templates.md) for body content

**Do NOT commit, push, or create a PR.** User handles this manually.

For plan deviations, see [error handling](references/error-handling.md).
