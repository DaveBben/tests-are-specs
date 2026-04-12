---
name: execute
disable-model-invocation: true
effort: high
argument-hint: "[feature or bug directory path or slug, e.g. .claude/features/add-webhook-retry/ or .claude/bugs/stale-text-after-save/]"
description: >
  Use when the user asks to "execute", "implement", "start building", "run
  the tasks", or "build this feature/fix" — any request to implement approved
  tasks from a /feature or /bug plan. Input is a feature or bug directory path
  (.claude/features/{slug}/ or .claude/bugs/{slug}/) or a slug name. Reads
  task JSON files, executes each through a 3-agent TDD cycle (test-writer →
  implementor → refactor), runs /light-review after each task, runs /deep-review
  after all tasks, and creates a PR.
  Not applicable for plan creation (use /feature or /bug).
---

# Plan Executor

Execute approved implementation tasks from a `/feature` or `/bug` plan. For
each task: run a 3-agent TDD cycle (RED → GREEN → REFACTOR), commit, run
`/light-review`, fix findings, then proceed. After all tasks: run full tests and
lint, run `/deep-review`, fix findings, record tech debt, and create a PR.

### Supporting Files

- [Agent Prompts](references/agent-prompts.md) — Exact prompts for tdd-test-writer, tdd-code-implementor, tdd-code-refactor
- [PR Templates](references/pr-templates.md) — Feature and bugfix PR body templates, multi-slice strategy

## Execution Model

```
Main session:
  ├── Input resolution (feature or bug directory)
  ├── Branch safety check (must not be on main)
  ├── Load plan.json + all task_N.json files
  ├── For each task (sequential):
  │   ├── Pre-task assumption check
  │   ├── tdd-test-writer agent (RED — failing tests)
  │   ├── tdd-code-implementor agent (GREEN — minimal passing code)
  │   ├── tdd-code-refactor agent (REFACTOR — improve or skip)
  │   ├── Commit: "Task N: [title]"
  │   ├── /light-review → fix BLOCKING/SHOULD_FIX → commit fixes
  │   └── Update task status → next task
  ├── Full test suite + lint → fix issues
  ├── /deep-review (max 2 iterations) → fix findings
  ├── Record unfixed items in spec.md tech debt
  ├── Push + create PR
  └── Complete
```

**Why 3 separate agents per task:** The test writer reads `testContext`
(interfaces, types, contracts) but not `implementationContext`, preventing
tests designed around the planned implementation. The implementor reads both
contexts and treats tests as the specification. The refactorer evaluates with
fresh eyes. This context isolation is the core design principle.

**Why sequential:** Each task builds on the previous. Simpler to debug, and
context isolation is maintained by dispatching fresh agents for each phase.

**Two-tier review:** `/light-review` after each task catches issues while context is
fresh. `/deep-review` after all tasks catches cross-task issues and
architectural problems.

---

## Input Resolution

If `$ARGUMENTS` were provided, classify and resolve:

1. **Feature directory path** (contains `.claude/features/`): Verify the
   directory exists. Verify `tasks/plan.json` exists inside it.
2. **Bug directory path** (contains `.claude/bugs/`): Verify the directory
   exists. Verify `tasks/plan.json` exists inside it.
3. **Slug** (no path separators): Try `.claude/features/{slug}/` first,
   then `.claude/bugs/{slug}/`. Use whichever exists.
4. **No input or not found**: Glob both `.claude/features/*/tasks/plan.json`
   and `.claude/bugs/*/tasks/plan.json` to list available plans. Present
   them and ask the user to pick one.

**Determine the source type** from the resolved path:
- `.claude/features/` → source type is `feature`
- `.claude/bugs/` → source type is `bugfix`

The source type determines branch naming and PR template (see below).

**What to load:**

- **plan.json** — read for feature metadata, constraints, scope, status
- **All task_N.json files** — glob `tasks/task_*.json`, sort by numeric ID
  (task_0, task_1, task_2, ...)

### Resumption

If any task JSON has `status: "DONE"`:

1. Cross-reference with `git log` to verify each DONE task was actually
   committed. For each DONE task, search for a commit message matching
   `"Task N:"`. If a task is marked DONE but has no matching commit,
   reset its status to `PENDING` — the previous session may have crashed
   after updating the JSON but before committing.
2. Check `git status` — if there are uncommitted changes from a previous
   session, stash them: `git stash push -m "recovered-uncommitted-work"`.
   Warn the user about the stash.
3. Identify complete vs. remaining tasks
4. Re-read plan.json constraints (the new session has no memory of them)
5. Re-establish the test baseline if one wasn't recorded, or verify the
   previous baseline is still valid
6. Present: "Tasks 0-N complete. Tasks N+1 through M remaining. Resuming
   from task N+1."
7. Skip completed tasks and begin from the first incomplete one
8. **Skip Phase 0 pre-flight checks** that have already passed (branch
   exists, environment verified). Only re-check git state and branch.

---

## Phase 0: Pre-flight Checks

Before executing anything:

### Branch Safety (CRITICAL)

1. Run `git branch --show-current`
2. **If on `main` or `master`**: Create and switch to a branch:
   - Feature: `git checkout -b feature/{slug}`
   - Bugfix: `git checkout -b bugfix/{slug}`
3. **If on another branch**: Confirm with the user that this is the right
   branch, or offer to create the appropriate branch.
4. **If the branch already exists** (resumption): check it out.
5. **Record the base branch** for the PR (typically `main`).

Never execute tasks on `main` or `master`. This is a hard stop.

### Environment Checks

1. **Verify test runner** — check the project has the test framework tasks
   depend on. Look for `package.json` scripts, `pytest.ini`, `Makefile`
   test targets, etc. If not installed, report.
2. **Spot-check verification commands** — read 2-3 task JSONs and confirm
   their `verificationCommand` is syntactically valid.
3. **Check git state** — `git status`. Warn about uncommitted changes.
4. **Verify gh CLI** — run `gh --version`. If not found, warn the user that
   PR creation will fail at the end.
5. **Verify review skills** — check that `skills/light-review/SKILL.md` and
   `skills/deep-review/SKILL.md` exist. If either is missing, stop and report
   before any tasks are executed — a missing review skill causes mid-pipeline
   failure after commits.

### Test Baseline

Run the project's full test suite before any task execution. Record:

1. **Total tests**: count of passing and failing tests
2. **Known failures**: list of test names/files that fail in the baseline
3. Store this in memory as the **test baseline** for this execution session

During the TDD cycle, the GREEN phase only needs to ensure:
- All tests from the RED phase pass (new tests)
- All tests that were passing in the baseline still pass
- Tests that were already failing in the baseline are ignored

This prevents flaky or pre-existing test failures from blocking execution.

### Spec Freshness Check

If the project has a `spec.md` (or `SPEC.md`), check its last-modified date
via `git log -1 --format="%ci" -- spec.md`. If it is older than 30 days or
the last 50 commits (whichever comes first), warn the user:

> "spec.md hasn't been updated in a while (last modified: {date}). Consider
> running `/onboard --update` after this feature to keep it current."

This is a warning, not a blocker — proceed regardless.

### Gate Check

1. **plan.json status is `Approved`** — if not, warn and ask to confirm.
2. **Read constraints and criticalReminders from plan.json** — these are
   execution guardrails passed to every agent.

### Right-Sizing Invariants

These are execution-time guardrails. Violations are not automatic stops —
they are tripwires that trigger a check with the user:

- **>500 lines changed in current slice**: STOP. Report to user. The slice
  is too large for quality review. Recommend splitting before continuing.
- **>3 files changed in a single task beyond what the task declares**: Pause
  and verify with the user. The task may have expanded beyond its declared
  concern. Check that all file changes are necessary for this one task's
  acceptance criteria.
- **Working state**: After every task commit, all tests must pass. If
  implementing the current task requires other uncommitted work to be present
  before anything can be tested, the task is not right-sized — STOP and
  report as a planning error.

If all gates pass, proceed to Phase 1.

---

## Phase 1: Execute Tasks

**Create TodoWrite entries** for every task to give the user real-time
progress visibility.

### Slice-Aware Execution

Read `totalSlices` from plan.json (defaults to 1 if absent).

If `totalSlices > 1`, process slices sequentially. Each slice is a complete
cycle: branch → tasks → post-implementation → PR.

### Multi-Repository Execution

If plan.json has `repositories` with more than one entry, group tasks by
their `repository` field. Process each repository sequentially:

1. `cd` to the repository path
2. Create branch (`feature/{slug}` or `bugfix/{slug}`)
3. Execute all tasks for this repository (following the per-task loop below)
4. Run post-implementation (Phase 2) for this repository
5. Create PR (Phase 3) for this repository
6. Return to next repository

For single-repo features (repository is `"."`), skip this grouping.

**For each slice** (or once if single-slice):

1. **Branch**: `feature/{slug}` for single-slice, or
   `feature/{slug}-slice-{N}` for multi-slice. First slice branches from
   the base branch (main). Subsequent slices branch from the previous slice's
   branch (stacked PRs).
2. **Filter tasks** to the current slice (`task.slice === currentSlice`)
3. **Execute all tasks** in the slice per the task loop below
4. **Post-implementation** (Phase 2) for this slice only
5. **Create PR** (Phase 3) for this slice, then return to next slice

Process tasks within each slice sequentially by ID (task_0, task_1, ...).

### For Each Task

#### Step 1: Pre-task Assumption Check

Before dispatching agents, verify:

- Do `relevantFiles` paths exist (or not exist, as expected by their
  `action`: create vs modify)?
- Have `testContext` or `implementationContext` interfaces changed since planning?
- Is `git status` clean?

If assumptions are violated, ask the user how to proceed.

#### Step 2: RED — Dispatch tdd-test-writer

**Checkpoint**: Run `git stash push -m "pre-RED-task-{N}"` to save clean
state before the phase begins.

Dispatch via the Agent tool using the RED prompt in
[references/agent-prompts.md](references/agent-prompts.md).

Collect the result. If STOPPED: run `git stash pop` to restore clean
state, mark the task `BLOCKED` in its JSON, record the reason in
`executionNotes`, ask the user how to proceed, and skip to the next task.

If RED succeeded, drop the stash: `git stash drop`.

#### Step 3: GREEN — Dispatch tdd-code-implementor

**Checkpoint**: Run `git stash push -m "pre-GREEN-task-{N}"` to save the
post-RED state before the implementation phase begins.

Dispatch via the Agent tool using the GREEN prompt in
[references/agent-prompts.md](references/agent-prompts.md).

Collect the result. If STOPPED: run `git stash pop` to restore the
post-RED state (tests exist but no partial implementation), mark task
`BLOCKED`, record the reason, ask user how to proceed, skip to next task.

If GREEN succeeded, drop the stash: `git stash drop`.

#### Step 4: REFACTOR — Dispatch tdd-code-refactor

**Checkpoint**: Run `git stash push -m "pre-REFACTOR-task-{N}"` to save
the post-GREEN state before refactoring begins.

Dispatch via the Agent tool using the REFACTOR prompt in
[references/agent-prompts.md](references/agent-prompts.md).

If REFACTOR makes things worse (tests fail after refactoring), run
`git stash pop` to restore the working post-GREEN state. Otherwise drop
the stash: `git stash drop`.

#### Step 5: Commit

```
git add [all files from RED + GREEN + REFACTOR phases]
git commit -m "Task N: [title from task JSON]"
```

#### Step 5b: Size Check

After committing, check the diff size:
```
git diff --stat HEAD~1
```

- If this task exceeds 200 lines changed: note in `executionNotes` and
  inform the user. The task may have been too broad.
- If the cumulative slice diff (from branch point) exceeds 500 lines: warn
  the user that the slice is growing large and reviewability may suffer. Ask
  whether to continue, split remaining tasks into a new slice, or stop.

#### Step 6: /light-review

Run `/light-review` against the latest commit.

- If BLOCKING or SHOULD_FIX findings: fix them in the main session,
  scoped to the task's declared files. Commit: `"Task N: check fixes"`
- If a second `/light-review` still has BLOCKING findings: do NOT loop further.
  Record the unresolved findings in the task's `executionNotes`, inform the
  user:
  > "Task N: `/light-review` still has BLOCKING findings after fix attempt.
  > Human review required. Findings: [list]"
  Ask whether to continue with remaining tasks or stop entirely.

#### Step 7: Update Task Status

1. Set `status` to `DONE` in task_N.json (or `BLOCKED` if step 6 triggered)
2. Mark TodoWrite entry as `completed`
3. Proceed to next task

#### Step 8: Context Pause Gate (every 5 tasks)

After every 5th completed task (task 5, 10, 15, ...), pause and check
context health. Each task dispatches 3-4 agents whose results accumulate
in the orchestrator's context, and quality degrades as context fills up.

Present to the user:

> "**Context checkpoint** — {N} tasks completed, {M} remaining.
>
> Check your context usage indicator. If your context is **less than 40%
> full**, we can continue with the next batch of tasks.
>
> If your context is **40% or more full**, start a fresh session for best
> results. Run:
>
> `/execute {feature-or-bug-directory-path}`
>
> The workflow will pick up exactly where it left off — all {N} completed
> tasks are recorded in the task JSON files. Deep review and PR creation
> will happen after all remaining tasks are done."

Wait for the user's response before continuing. If the user says to
continue, proceed with the next task. If the user says to restart, end
the current session gracefully — all progress is already persisted in
the task JSON files.

### For Tasks That STOP

If any TDD agent returns STOPPED:

1. Record the failure reason in `executionNotes`
2. Set task status to `BLOCKED`
3. Check if downstream tasks depend on this one (via `blockedBy` fields)
4. Ask: "Task N failed: [reason]. Tasks [X, Y] depend on it. Continue with
   unblocked tasks, or stop to investigate?"

---

## Phase 2: Post-Implementation

**Only run this phase when ALL tasks are complete** — not after each session
chunk. If execution was split across multiple sessions via the context pause
gate, the final session that completes the last task runs Phase 2. Previous
sessions end after the context pause gate without running deep review or
creating a PR.

After all tasks complete:

### Step 1: Full Test Suite + Lint

Run the project's full test suite and linting/type checking.

- If tests fail: identify which tests and fix. Commit: `"Fix failing tests"`
- If lint/type errors: fix. Commit: `"Fix lint/type errors"`

### Step 2: Deep Review (max 2 iterations)

1. Run `/deep-review` against the full branch diff (diff from base branch)
2. Review the consolidated findings:
   - **BLOCKING**: must fix
   - **SHOULD_FIX**: must fix
   - **SUGGESTIONS**: fix high-value ones that clearly improve code quality
3. Fix findings, commit: `"Deep review fixes"`
4. If the first pass had BLOCKING findings: run `/deep-review` one more time
   (single retry, not a loop)
5. If the second pass still has BLOCKING findings: proceed to Step 3

### Step 3: Record Tech Debt

If any BLOCKING or SHOULD_FIX findings remain unfixed after 2 deep-review
iterations:

1. Check if the project has a `spec.md` (or `SPEC.md`) with a tech debt
   section
2. If yes: append the unfixed items with context (file, description, why
   unfixed)
3. If no: include the unfixed items in the PR description under a "Known
   Issues" section

---

## Phase 3: Create PR

After post-implementation is complete, use the templates in
[references/pr-templates.md](references/pr-templates.md). Choose the template
matching the source type (feature or bugfix).

After creating the PR:
1. Update plan.json: set status to `COMPLETE`, add PR URL
2. Present the PR URL to the user

---

## Execution Summary

After the PR is created, present:

```
## Execution Summary

Branch: feature/{slug} or bugfix/{slug}
PR: #{number} — [URL]
Tasks: N completed, M failed
Commits: X (N tasks + Y review fixes)

### Task Results
- Task 0: [title] — DONE
- Task 1: [title] — DONE
- Task 2: [title] — BLOCKED (reason)

### Review
- /light-review: N issues found, N fixed
- /deep-review: N issues found, N fixed, N recorded as tech debt

### Next Steps
[Any unfixed items, human review items, or "Ready for review"]
```

---

## Key Principles

- **Tests first, always.** RED before GREEN. No exceptions.
- **Context isolation between TDD phases.** Test writer reads `testContext`
  (interfaces, types, contracts) but not `implementationContext`. Implementor
  reads both. This prevents tests from being designed around the implementation.
- **Minimum viable code.** The GREEN phase writes the least code possible.
  The REFACTOR phase improves only what needs improving.
- **Stay within declared scope.** Each agent touches only files declared
  in the task.
- **Never execute on main.** Branch safety is a hard stop.
- **Two-tier review.** `/light-review` per task (fast). `/deep-review` for the
  whole branch (thorough).
- **Always in a working state.** Every commit, every task completion, every
  slice — tests pass, the project builds, nothing is half-done. If you can't
  get to a working state without future tasks, the plan needs revision.
- **If stuck, ask — don't guess.** Ambiguous instructions mean stop and
  report.

### When the Plan Is Wrong

- **File doesn't exist**: STOP. Report to user.
- **Interface changed**: STOP. Task context may need updating.
- **Test infrastructure missing**: Report. User decides how to proceed.
- **Task too large** (>200 lines changed): Report with line count. Recommend
  splitting. User decides.
- **Slice too large** (>500 lines cumulative): Warn. Recommend creating a
  new slice boundary at the current task. User decides.
- **Task touches files beyond what it declares**: Pause. Verify all changes
  are necessary for this task's acceptance criteria. If any changes serve a
  different concern, the task should have been split during planning.
- **Tests require unmerged work**: If the current task's tests cannot pass
  without uncommitted changes from a future task, the task ordering or
  boundaries are wrong. STOP and report — this indicates a planning error.
- **Task contradiction**: STOP. Back to `/feature` or `/bug` for revision.

For minor deviations (slightly different import path), adapt and note. For
scope or acceptance criteria changes, stop.

### Flagging Upstream Artifacts for Revision

During execution, if you discover that the plan is inadequate:

1. Note the specific issue and impact
2. Inform the user with a recommendation
3. Continue execution if possible, noting the deviation
