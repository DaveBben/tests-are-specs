---
name: execute
disable-model-invocation: true
effort: high
argument-hint: "[feature or bug directory path or slug, e.g. .claude/features/add-webhook-retry/ or .claude/bugs/stale-text-after-save/]"
model: opus
description: >
  Use when the user asks to "execute", "implement", "start building", "run
  the tasks", or "build this feature/fix" — any request to implement approved
  tasks from a /cks:feature or /cks:bug plan. Input is a feature or bug directory path
  (.claude/features/{slug}/ or .claude/bugs/{slug}/) or a slug name. Reads
  task JSON files, executes each through a 3-agent TDD cycle (test-writer →
  implementor → refactor), runs /cks:light-review after each task, runs /cks:deep-review
  after all tasks. Does not push or create PRs — user handles that manually.
  Not applicable for plan creation (use /cks:feature or /cks:bug).
---

# Plan Executor

Execute approved implementation tasks from a `/cks:feature` or `/cks:bug` plan. For
each task: run a 3-agent TDD cycle (RED → GREEN → REFACTOR), commit, run
`/cks:light-review`, fix findings, then proceed. After all tasks: run full tests and
lint, run `/cks:deep-review`, fix findings, record tech debt, and create a PR.

### Supporting Files

- [Agent Prompts](references/agent-prompts.md) — Exact prompts for tdd-test-writer, tdd-code-implementor, tdd-code-refactor
- [PR Templates](references/pr-templates.md) — Feature and bugfix PR body templates, multi-slice strategy
- [Resumption](references/resumption.md) — Checkpoint format and session resumption logic
- [Multi-Repo](references/multi-repo.md) — Multi-repository execution and contract stubs
- [Error Handling](references/error-handling.md) — Plan deviation responses and upstream flagging
- [Implementation Guidance](references/implementation-guidance.md) — Patterns for effective human-AI collaboration during execution

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
  │   ├── /cks:light-review → fix BLOCKING/SHOULD_FIX → commit fixes
  │   └── Update task status → next task
  ├── Full test suite + lint → fix issues
  ├── /cks:deep-review (max 2 iterations) → fix findings
  ├── Record unfixed items in spec.md tech debt
  └── Complete (user handles push + PR)
```

**Why 3 separate agents per task:** The test writer reads `testContext`
(interfaces, types, contracts) but not `implementationContext`, preventing
tests designed around the planned implementation. The implementor reads both
contexts and treats tests as the specification. The refactorer evaluates with
fresh eyes. This context isolation is the core design principle.

**Why sequential:** Each task builds on the previous. Simpler to debug, and
context isolation is maintained by dispatching fresh agents for each phase.

**Two-tier review:** `/cks:light-review` after each task catches issues while context is
fresh. `/cks:deep-review` after all tasks catches cross-task issues and
architectural problems.

---

## Input Resolution

Resolve `$ARGUMENTS` — classify and find the plan directory:

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

After each task completes, write/update a checkpoint file for resumption.
See [references/resumption.md](references/resumption.md) for format and
resumption logic. If `execution-state.json` exists at startup, follow
the resumption procedure before continuing.

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
4. **Skip** — gh CLI is not needed (push and PR creation are manual).
5. **Verify review skills** — invoke `/cks:light-review` and `/cks:deep-review`
   with a dry-run or confirm they are available. If either skill is not found,
   stop and report before any tasks are executed.

### Task JSON Validation

Before executing, validate every task JSON:

1. **File paths**: every path in `files` either exists (for `modify`) or
   doesn't exist (for `create`). Paths in `testContext` and
   `implementationContext` must exist.
2. **Required fields non-empty**: `doNot`, `acceptanceCriteria`, and
   `doneWhen` must be non-empty. Flag empty fields as a planning deficiency.
3. **Verification command**: `verificationCommand` must be syntactically
   valid. Spot-check 2-3 by running them with `--help` or `--version`.
4. **Environment check**: if `environmentCheck` is set, run it now to
   verify the environment is ready before any tasks begin.

If critical violations are found (missing files that should exist, broken
verification commands), report them and ask the user before proceeding.
Minor issues (empty `doNot`) get a warning but don't block.

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
> running `/cks:onboard --update` after this feature to keep it current."

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
- **Working state**: After every task commit, the project MUST build and all
  existing tests MUST pass. The feature may be incomplete — that's expected
  on a branch. But if the current task breaks the build or existing tests
  and cannot be fixed without future tasks, the task ordering or boundaries
  are wrong — STOP and report as a planning error.

If all gates pass, proceed to Phase 1.

---

## Phase 1: Execute Tasks

**Create TodoWrite entries** for every task to give the user real-time
progress visibility.

### Slice-Aware Execution

Read `totalSlices` from plan.json (defaults to 1 if absent).

If `totalSlices > 1`, process slices sequentially. Each slice is a complete
cycle: branch → tasks → post-implementation → PR.

If plan.json has `repositories` with more than one entry, see
[references/multi-repo.md](references/multi-repo.md) for multi-repo
execution and contract stub patterns.

**For each slice** (or once if single-slice):

1. **Branch**: `feature/{slug}` for single-slice, or
   `feature/{slug}-slice-{N}` for multi-slice. First slice branches from
   the base branch (main). Subsequent slices branch from the previous slice's
   branch (stacked PRs).
2. **Filter tasks** to the current slice (`task.slice === currentSlice`)
3. **Execute all tasks** in the slice per the task loop below
4. **Post-implementation** (Phase 2) for this slice only
5. **Finalize** (Phase 3) for this slice, then return to next slice

Process tasks within each slice sequentially by ID (task_0, task_1, ...).

### For Each Task

#### Step 1: Pre-task Assumption Check

Before dispatching agents, verify:

- Do `relevantFiles` paths exist (or not exist, as expected by their
  `action`: create vs modify)?
- Have `testContext` or `implementationContext` interfaces changed since planning?
- Is `git status` clean?

If assumptions are violated, ask the user how to proceed.

#### Phase Checkpoints (temporary branches)

Each TDD phase creates a temporary branch as a checkpoint before starting.
This is safer than `git stash` — no merge conflicts on restore, no opaque
stash stack, no confusion with user stashes. Temp branches are named and
visible in `git branch`.

Pattern for each phase:
1. Before phase: `git checkout -b tmp/pre-{PHASE}-task-{N}`
2. Switch back: `git checkout -` (return to the working branch)
3. If phase fails: `git reset --hard tmp/pre-{PHASE}-task-{N}` (restore)
4. If phase succeeds: `git branch -D tmp/pre-{PHASE}-task-{N}` (cleanup)

#### Step 2: RED — Dispatch tdd-test-writer

**Checkpoint**: `git checkout -b tmp/pre-RED-task-{N} && git checkout -`

Dispatch via the Agent tool using the RED prompt in
[references/agent-prompts.md](references/agent-prompts.md).

Collect the result. If STOPPED: `git reset --hard tmp/pre-RED-task-{N}`
to restore clean state, then `git branch -D tmp/pre-RED-task-{N}`. Mark
the task `BLOCKED` in its JSON, record the reason in `executionNotes`,
ask the user how to proceed, and skip to the next task.

If RED succeeded: `git branch -D tmp/pre-RED-task-{N}`.

#### Step 3: GREEN — Dispatch tdd-code-implementor

**Checkpoint**: `git checkout -b tmp/pre-GREEN-task-{N} && git checkout -`

Dispatch via the Agent tool using the GREEN prompt in
[references/agent-prompts.md](references/agent-prompts.md).

Collect the result. If STOPPED: `git reset --hard tmp/pre-GREEN-task-{N}`
to restore the post-RED state (tests exist but no partial implementation).
Then `git branch -D tmp/pre-GREEN-task-{N}`. Mark task `BLOCKED`, record
the reason, ask user how to proceed, skip to next task.

If GREEN succeeded: `git branch -D tmp/pre-GREEN-task-{N}`.

#### Step 4: REFACTOR — Dispatch tdd-code-refactor

**Checkpoint**: `git checkout -b tmp/pre-REFACTOR-task-{N} && git checkout -`

Dispatch via the Agent tool using the REFACTOR prompt in
[references/agent-prompts.md](references/agent-prompts.md).

If REFACTOR makes things worse (tests fail after refactoring):
`git reset --hard tmp/pre-REFACTOR-task-{N}` to restore the working
post-GREEN state. Then `git branch -D tmp/pre-REFACTOR-task-{N}`.

If REFACTOR succeeded or was skipped:
`git branch -D tmp/pre-REFACTOR-task-{N}`.

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

#### Step 6: /cks:light-review

Run `/cks:light-review` against the latest commit.

- If BLOCKING or SHOULD_FIX findings: fix them in the main session,
  scoped to the task's declared files. Commit: `"Task N: check fixes"`
- If a second `/cks:light-review` still has BLOCKING findings: do NOT loop further.
  Record the unresolved findings in the task's `executionNotes`, increment
  `consecutiveReviewFailures` in execution-state.json, and inform the user:
  > "Task N: `/cks:light-review` still has BLOCKING findings after fix attempt.
  > Human review required. Findings: [list]"
  Ask whether to continue with remaining tasks or stop entirely.

**Circuit breaker**: If `consecutiveReviewFailures` reaches 2 (two
consecutive tasks with unresolved findings), STOP execution entirely:

> "Two consecutive tasks have unresolved review findings. This may
> indicate a systemic issue. Options:
> 1. **Revert to last clean task** — reset to the commit before these
>    failures and re-plan the affected tasks
> 2. **Continue accepting the findings** — proceed with remaining tasks
> 3. **Abandon and re-plan** — the implementation approach may need revision"

Reset `consecutiveReviewFailures` to 0 whenever a task passes light-review
cleanly.

#### Step 7: Update Task Status

1. Set `status` to `DONE` in task_N.json (or `BLOCKED` if step 6 triggered)
2. Update `execution-state.json` with the current task ID, dispatch count,
   and timestamp
3. Mark TodoWrite entry as `completed`
4. Proceed to next task

#### Step 8: Architectural Drift Check (every 4 tasks)

After every 4th completed task, run a quick sanity check against the plan:

1. Compare the files actually changed so far (`git diff --name-only` from
   base branch) against the impact map's expected files. Flag any files
   changed that weren't in the plan.
2. Check if any file has grown significantly beyond what the plan
   anticipated (e.g., a task that was supposed to add 30 lines added 200).
3. Check for imports or dependencies introduced that weren't in the plan.

If drift is detected, inform the user:

> "Architectural drift detected after {N} tasks:
> - [unexpected files changed / oversized files / unexpected dependencies]
>
> This may indicate the implementation is diverging from the plan.
> Continue, or pause to review?"

This catches "bypassed the service layer" and "quietly added a dependency"
problems before they compound across more tasks.

#### Step 9: Context Pause Gate (dispatch-count based)

Track total agent dispatches (each RED/GREEN/REFACTOR/light-review = 1).
A simple task = 4 dispatches; complex with review fixes = 6+.

**After 20 dispatches**, pause: report tasks completed, dispatches used,
tasks remaining. Ask the user to check context usage (`/context`) and
either continue or start a fresh session with
`/cks:execute {feature-or-bug-directory-path}` (resumption picks up
automatically). Wait for user response. Next gate at another 20 dispatches.

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

1. Run `/cks:deep-review` against the full branch diff (diff from base branch)
2. Review the consolidated findings:
   - **BLOCKING**: MUST fix
   - **SHOULD_FIX**: MUST fix
   - **SUGGESTIONS**: fix high-value ones that clearly improve code quality
3. Fix findings, commit: `"Deep review fixes"`
4. If the first pass had BLOCKING findings: run `/cks:deep-review` one more time
   (single retry, not a loop)
5. If the second pass still has BLOCKING findings: **do NOT create a PR.**
   Proceed to Step 3.

### Step 3: Handle Unresolved Findings

**If BLOCKING findings remain after 2 iterations:**

Do NOT finalize. Present the unresolved findings to the user:

> "Deep review found BLOCKING issues that could not be auto-fixed after
> 2 attempts. The feature will NOT be marked complete until these are resolved:
>
> [list of BLOCKING findings with file:line]
>
> Options:
> 1. Fix these manually, then run `/cks:execute {path}` to resume (it will
>    re-run deep review and finalize)
> 2. If you've reviewed and determined these are false positives, say
>    'override' to finalize anyway"

Record the findings in the plan.json `executionNotes` field so they
survive across sessions.

**If only SHOULD_FIX findings remain (no BLOCKING):**

1. Check if the project has a `spec.md` (or `SPEC.md`) with a tech debt
   section
2. If yes: append the unfixed items with context (file, description, why
   unfixed)
3. If no: include the unfixed items in the PR description under a "Known
   Issues" section
4. Proceed to Phase 3 (Finalize)

---

### Step 4: Update spec.md Current State

If the project has a `spec.md` (or `SPEC.md`), read its `## Current State`
section. If the feature changes capabilities described there (new endpoints,
changed behavior, new dependencies, removed functionality), update the
section to reflect what was actually built. Keep the same style and level
of detail as the existing content.

Commit: `"Update spec.md current state"`

This makes spec maintenance automatic rather than aspirational. Skip this
step if spec.md doesn't exist or if the feature doesn't affect anything
described in Current State.

---

## Phase 3: Finalize

After post-implementation is complete:

1. Update plan.json: set status to `COMPLETE`
2. Present a summary: branch name, task results (DONE/BLOCKED per task),
   review findings fixed/remaining, and any unfixed items or tech debt
3. Remind the user that push and PR creation are manual — point to
   [references/pr-templates.md](references/pr-templates.md) for body templates

**Do NOT push to remote or create a PR.** The user handles this manually.

When the plan is wrong (missing files, changed interfaces, oversized tasks),
see [references/error-handling.md](references/error-handling.md) for
response procedures. For minor deviations, adapt and note. For scope or
acceptance criteria changes, stop and report.
