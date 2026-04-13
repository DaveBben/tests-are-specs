---
name: execute
disable-model-invocation: true
effort: high
argument-hint: "[feature or bug directory path or slug]"
model: opus
description: >
  Implements approved tasks from /cks:feature or /cks:bug. For each task:
  dispatches a single implementation agent, commits, runs /cks:light-review.
  After all tasks: full test suite, /cks:deep-review, finalize. Does not
  push or create PRs.
---

# Plan Executor

Execute approved tasks. For each task: implement → commit → light-review.
After all tasks: full tests → deep-review → finalize.

### Supporting Files

- [Agent Prompt](references/agent-prompt.md) — Implementation agent dispatch prompt
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
  │   ├── Commit: "Task N: [title]"
  │   ├── /cks:light-review → fix findings → commit fixes
  │   └── Update task status
  ├── Full test suite + lint
  ├── /cks:deep-review (max 2 iterations)
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

### Gate Check

- `plan.json` status is `Approved`
- Read `constraints` and `criticalReminders` — passed to every agent

---

## Task Execution

Create TodoWrite entries for all tasks for user visibility.

### Slice-Aware Execution

If `totalSlices > 1`: process sequentially. Each slice = branch →
tasks → post-implementation → finalize. Slice 1 branches from main;
subsequent slices branch from previous (stacked PRs).

### For Each Task

#### Step 1: Pre-task Check

- Do `relevantFiles` paths match expected state (exist/not-exist)?
- Is `git status` clean?
- If `blockedBy` lists tasks that aren't DONE, skip and report.

If assumptions violated, ask the user.

#### Step 2: Implement

Create checkpoint: `git checkout -b tmp/pre-task-{N} && git checkout -`

Dispatch the implementation agent via Agent tool using the prompt in
[references/agent-prompt.md](references/agent-prompt.md). Pass it:
- Task JSON path
- Plan JSON path (for constraints)
- Test baseline (known failures to ignore)
- Plan constraints verbatim

If agent returns STOPPED: restore via
`git reset --hard tmp/pre-task-{N}`, cleanup branch, mark task `BLOCKED`,
record reason in `executionNotes`, ask user how to proceed.

If succeeded: `git branch -D tmp/pre-task-{N}`.

#### Step 3: Size Check + Commit

```
git diff --stat HEAD
```

If task exceeds 200 lines: note in `executionNotes`, inform user.
If cumulative slice diff exceeds 500 lines: warn user, ask whether to
continue or split.

```
git add [files from task]
git commit -m "Task N: [title]"
```

#### Step 4: Light Review

Run `/cks:light-review` against latest commit.

- BLOCKING/SHOULD_FIX findings: fix, commit `"Task N: review fixes"`
- Second review still BLOCKING: record in `executionNotes`, inform user
- **Circuit breaker**: 2 consecutive tasks with unresolved findings →
  STOP execution, present options (revert / continue / re-plan)

Reset consecutive failure count on clean review.

#### Step 5: Update Status

Set task to `DONE` (or `BLOCKED`). Update `execution-state.json`.
Mark TodoWrite entry completed.

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

Run full tests and linting. Fix failures, commit separately.

### Step 2: Deep Review (max 2 iterations)

1. Run `/cks:deep-review` against full branch diff
2. Fix BLOCKING and SHOULD_FIX findings, commit `"Deep review fixes"`
3. If first pass had BLOCKING: run once more (single retry)
4. Still BLOCKING after 2 iterations: do NOT finalize — present to user

### Step 3: Unresolved Findings

**BLOCKING remains**: present findings, offer manual fix + re-run or
override. Record in `plan.json executionNotes`.

**Only SHOULD_FIX remains**: append to `spec.md` tech debt section if
it exists, otherwise include in PR description. Proceed to finalize.

### Step 4: Update spec.md

If `spec.md` exists and feature changes capabilities in `## Current State`,
update to reflect what was built. Commit `"Update spec.md current state"`.

---

## Finalize

1. Set plan.json status to `COMPLETE`
2. Present summary: branch, task results, findings fixed/remaining
3. Point to [PR templates](references/pr-templates.md) for body content

**Do NOT push or create a PR.** User handles this manually.

For plan deviations, see [error handling](references/error-handling.md).
