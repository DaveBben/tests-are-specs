---
name: execute
disable-model-invocation: true
effort: xhigh
argument-hint: "[feature or bug directory path or slug]"
model: opus
description: >
  Implements approved tasks from /tpe:plan or /tpe:bug. For each task:
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
   If missing and path is under `.claude/bugs/`:
   > "No tasks found at `.claude/bugs/{slug}/tasks/`. Run `/tpe:bug {slug}` to complete investigation and produce task JSONs."
   If missing and path is under `.claude/features/`:
   > "No plan.json found at `.claude/features/{slug}/tasks/`. Run `/tpe:plan {slug}` to produce the plan and task JSONs."
2. **Slug**: Try `.claude/features/{slug}/` then `.claude/bugs/{slug}/`.
3. **No input**: Glob for available plans, present choices.

Determine source type from path (`feature` or `bugfix`) for branch naming.

Load `plan.json` + all `task_*.json` files sorted by numeric ID. If `execution-state.json` exists, follow [resumption procedure](references/resumption.md).

---

## Pre-flight

### Branch Safety (hard stop)

If on `main`/`master`: create `feature/{slug}` or `bugfix/{slug}`. If on another branch: confirm with user. Never execute on main.

### Validate Task JSONs

For each task:
- `files` paths exist (modify) or don't exist (create)
- `relevantFiles` paths with `action: modify` exist on disk
- `relevantFiles` paths with `action: create` do NOT exist on disk
- `doNot`, `acceptanceCriteria` non-empty; `doneWhen` non-empty
- `verificationCommand` is syntactically valid

Critical violations → report and ask. Minor issues → warn and continue.

### Test Baseline

Run full test suite. Record passing count and known failures.

### Spec Freshness

If any `spec.md` (root or domain) has `Last verified` >30 days old and plan date >7 days old: warn and continue. Skip if plan was just produced.

### Brainstorm.md Check

If any task qualifies as Complex tier, verify `brainstorm.md` exists. If missing: warn, offer to downgrade to Standard tier or return to `/tpe:think`. Do not block.

### Gate Check

- `plan.json` status is `Approved`
- Read `constraints` and `criticalReminders` — passed to every agent

---

## Fast Path (Small Plans)

If the plan has **≤2 tasks**, total estimated size is **under 200 lines**, and the combined unique `files` across all tasks is **≤4**, skip task-by-task execution:

1. Dispatch a single implementation agent with each task JSON path (not merged), plan constraints, and the union of atRiskTests
2. If agent returns DONE and all regressionChecks pass: proceed to Post-Implementation
3. If agent STOPs or exceeds 200 lines: fall back to standard task-by-task execution below

≤2 tasks / ≤4 files keeps the agent within the context interference threshold. Do not merge task JSONs into a single blob — pass them as separate files so the agent reads each task's boundaries independently.

---

## Task Execution

Create TodoWrite entries for all tasks for user visibility.

### Slice-Aware Execution

If `totalSlices > 1`: process sequentially. Each slice = branch → tasks → post-implementation → finalize. Slice 1 branches from main; subsequent slices branch from previous (stacked PRs).

### Complexity Tier

Before dispatching each task, classify it:

| Tier | Criteria | Agent Config |
|------|----------|-------------|
| **Simple** | 1 file, clear reference, no interface changes | maxTurns: 20, model: haiku |
| **Standard** | 2-3 files, or 1 file with interface changes | maxTurns: 50, model: sonnet (default) |
| **Complex** | 4 files, or touches shared interfaces/types | maxTurns: 75, model: opus, also pass `brainstorm.md` path for additional approach context |

If a Simple task agent STOPs or hits maxTurns, retry once at Standard tier before marking BLOCKED.

### For Each Task

#### Step 1: Pre-task Check

- Do `relevantFiles` paths match expected state (exist/not-exist)?
- Is `git status` clean? (Should be — prior task was committed in Step 3.) If not clean, something went wrong. Ask user before proceeding.
- If `blockedBy` lists tasks that aren't DONE, skip and report.
- If `execution-state.json`'s `executionNotes` has a BLOCKED note for this task, show it to the user and ask whether to proceed.

If assumptions violated, ask the user.

#### Step 2: Implement

Dispatch the `code-implementor` agent. Pass: task JSON path, plan JSON path, test baseline, plan constraints verbatim, task's `doNot` and `dependencyChain` verbatim. Instruct agent to re-read `doNot` and constraints before verification (counters instruction fade-out).

If STOPPED: mark `BLOCKED`, record in `executionNotes[task_id]`, ask user.

**Trust-but-verify**: run `regressionCheck` from the orchestrator (do not rely on agent self-report). Check both: (1) exit code is non-zero → fail, and (2) scan output for "fail", "error", "FAIL", "ERROR", or "skipped" — a test suite can exit 0 while skipping the tests you care about. If either check fails: one retry, then `BLOCKED`.

#### Step 3: Commit

Commit with message `task_{N}: {task title}`. Do not push.

#### Step 4: Handoff Check

If any pending task has this task's ID in its `blockedBy`, dispatch the `task-handoff-checker` agent (completed + dependent task JSON paths, known-failures baseline). Returns `PASS` or `BLOCKED — [reason]`.

On BLOCKED: record in `executionNotes[dependent_task_id]`, warn user. Skip entirely if no task depends on this one.

#### Step 5: Size & Drift

- Task >200 lines: note in `executionNotes`, inform user
- Cumulative slice >500 lines: warn, ask to continue or split
- Agent used >80% maxTurns: flag possible drift

#### Step 6: Update Status & Mask

Set task `DONE`/`BLOCKED`. Update `execution-state.json` with one-line summary. For next task prompt: reference only summaries for prior tasks (keep last 2 full results for continuity).

### Context Pause Gate

Every **6 completed tasks**: pause, report progress, ask user to check `/context` or start fresh session (resumption picks up automatically).

### Blocked Tasks

Record reason, set `BLOCKED`, check dependents, ask user to continue or stop.

---

## Post-Implementation & Finalize

After all tasks in the current slice:
1. Run full test suite + lint. Fix failures.
2. If `spec.md` exists and capabilities changed, update it.
3. Set plan.json status to `COMPLETE`.
4. Present summary: branch, task results, remaining issues. Then say:
   > "Clear your context and run `/tpe:review` to review the changes."
5. Point to [PR templates](references/pr-templates.md) for body content.

**Do NOT push or create a PR.** User handles this manually.
See [error handling](references/error-handling.md) for plan deviations.
