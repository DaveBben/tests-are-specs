---
name: execute
disable-model-invocation: true
effort: high
argument-hint: "[feature or bug directory path or slug, e.g. .claude/features/add-webhook-retry/ or .claude/bugs/stale-text-after-save/]"
molel: opus
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

### Execution State Checkpoint

After each task completes, write (or update) a checkpoint file at
`.claude/{features|bugs}/{slug}/execution-state.json`:

```json
{
  "lastCompletedTask": "task_3",
  "branch": "feature/{slug}",
  "baseBranch": "main",
  "dispatchCount": 16,
  "testBaseline": {
    "totalPassing": 142,
    "knownFailures": ["test_flaky_timeout"]
  },
  "consecutiveReviewFailures": 0,
  "timestamp": "2026-04-12T14:30:00Z"
}
```

This file is the single source of truth for resumption — no git log
parsing or commit message matching needed.

### Resumption

If `execution-state.json` exists:

1. Read it to determine the last completed task, branch, dispatch count,
   and test baseline
2. Verify the branch exists and check it out
3. Check `git status` — if there are uncommitted changes from a previous
   session, stash them: `git stash push -m "recovered-uncommitted-work"`.
   Warn the user about the stash.
4. **Run the full test suite** to verify the branch is in a consistent
   state. If tests fail unexpectedly (beyond the known baseline), warn
   the user before resuming.
5. Re-read plan.json constraints (the new session has no memory of them)
6. Present: "Tasks 0-N complete. Tasks N+1 through M remaining. Resuming
   from task N+1."
7. Skip completed tasks and begin from the first incomplete one
8. Restore the dispatch count from the checkpoint (for context gate tracking)

If `execution-state.json` does not exist but task JSONs have `status: "DONE"`:
fall back to verifying against `git log` — search for commits matching
`"Task N:"`. If a task is marked DONE but has no matching commit, reset
its status to `PENDING`.

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

### Multi-Repository Execution

Multi-repo support works best with monorepos (multiple packages in one
repo) or co-located repos. For truly separate repositories with
independent CI/CD, consider running `/cks:execute` independently per repo.

If plan.json has `repositories` with more than one entry, group tasks by
their `repository` field. Process each repository sequentially:

1. `cd` to the repository path
2. Create branch (`feature/{slug}` or `bugfix/{slug}`)
3. Execute all tasks for this repository (following the per-task loop below)
4. Run post-implementation (Phase 2) for this repository
5. Finalize (Phase 3) for this repository
6. Return to next repository

For single-repo features (repository is `"."`), skip this grouping.

#### Contract Stubs (multi-repo only)

When repo B depends on changes from repo A (e.g., new API endpoints,
shared types), repo B's tests can't hit repo A's unmerged changes. Use
contract stubs to decouple execution:

1. After completing repo A's tasks, extract the contract surface: type
   definitions, API schemas, or interface files that repo B depends on
2. Place these as stub files in repo B's test fixtures directory (e.g.,
   `tests/fixtures/contracts/repo-a-types.ts`)
3. Repo B's tests run against the stubs, not the live endpoints
4. Include a `TODO: replace stub with real import after repo A merges`
   comment in each stub file

If plan.json has a `contracts` field listing shared specs (OpenAPI,
protobuf, TypeScript interfaces), use those directly as the stubs rather
than extracting them.

This mirrors consumer-driven contract testing: both repos agree on the
contract, implement independently, and validate on merge.

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

Track the total number of agent dispatches in this session. Each
RED/GREEN/REFACTOR phase is 1 dispatch. Each /cks:light-review is 1 dispatch.
Review fix iterations add additional dispatches. A simple task with no
review fixes = 4 dispatches. A complex task with review fixes = 6+.

**After 20 dispatches**, pause and check context health:

> "**Context checkpoint** — {N} tasks completed ({D} agent dispatches so
> far), {M} tasks remaining.
>
> Check your context usage (run `/context` or check the context indicator).
> Use your judgment:
> - If context is **well under 50%** and quality feels good, say 'continue'
> - If context is **approaching 50%** or you notice quality degrading,
>   start a fresh session for best results:
>
> `/cks:execute {feature-or-bug-directory-path}`
>
> The workflow picks up exactly where it left off — all {N} completed
> tasks are recorded in the task JSON files. Deep review and PR creation
> happen after all remaining tasks are done."

Wait for the user's response. If they say continue, proceed and trigger
the next gate after another 20 dispatches. If they restart, end gracefully
— all progress is persisted.

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
2. Present the execution summary to the user
3. Remind the user that push and PR creation are manual:
   > "All tasks are complete and committed on `{branch}`. When you're ready,
   > push the branch and create a PR. The PR template is in
   > [references/pr-templates.md](references/pr-templates.md)."

**Do NOT push to remote or create a PR.** The user handles this manually.

---

## Execution Summary

After finalization, present:

```
## Execution Summary

Branch: feature/{slug} or bugfix/{slug}
Tasks: N completed, M failed
Commits: X (N tasks + Y review fixes)

### Task Results
- Task 0: [title] — DONE
- Task 1: [title] — DONE
- Task 2: [title] — BLOCKED (reason)

### Review
- /cks:light-review: N issues found, N fixed
- /cks:deep-review: N issues found, N fixed, N recorded as tech debt

### Next Steps
- Push branch and create PR when ready
- PR template: references/pr-templates.md
[Any unfixed items or human review items]
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
- **Two-tier review.** `/cks:light-review` per task (fast). `/cks:deep-review` for the
  whole branch (thorough).
- **Always in a working state.** Every commit, every task completion, every
  slice — the project builds, all existing tests pass, and no runtime errors
  are introduced. "Working state" does NOT mean the feature is complete —
  intermediate tasks may leave the feature partially implemented behind the
  branch. The feature becomes complete only when all tasks are done and the
  branch is ready for PR. If a task cannot build or pass existing tests
  without future tasks, the plan needs revision.
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
- **Task contradiction**: STOP. Back to `/cks:feature` or `/cks:bug` for revision.

For minor deviations (slightly different import path), adapt and note. For
scope or acceptance criteria changes, stop.

### Flagging Upstream Artifacts for Revision

During execution, if you discover that the plan is inadequate:

1. Note the specific issue and impact
2. Inform the user with a recommendation
3. Continue execution if possible, noting the deviation
