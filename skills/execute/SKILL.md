---
name: execute
disable-model-invocation: true
effort: high
skills: [implementation-plans]
argument-hint: "[story ID or story path]"
allowed-tools:
  - Agent
  - Skill
  - TodoWrite
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
description: >
  Use when the user asks to "execute the plan", "implement the plan", "start
  building", "run the tasks", "execute tasks", or "implement this" — any
  request to execute approved implementation tasks for a story. Input is a
  story ID (story_NNN) or path. Resolves tasks from JSON artifact files in
  ~/.claude/backlog-driven-development/artifacts/, groups them by repository,
  then for each repo: creates a branch, executes tasks in parallel batches
  using TDD, runs /check after each task, runs /deep-review after all tasks
  complete, and creates a PR.
  Not applicable for plan creation (use /task-decomposition).
---

# Plan Executor

Execute approved implementation tasks for a story. For each repository the
story touches: create a single branch, execute all tasks in TDD order
(parallel where safe), run `/check` after each task, run `/deep-review`
once after all tasks complete, fix findings, then create a PR and push.

## Execution Model

```
Main session:
  ├── Input resolution (artifact store)
  ├── Load all tasks, group by repository
  ├── For each repository (sequential):
  │   ├── Create branch: us-{story-slug}
  │   ├── Execute Task 0 (contracts) — main session
  │   ├── /check on Task 0 → fix findings → commit
  │   ├── Execute batches:
  │   │   ├── Batch 1: [Task 1, Task 3] → parallel code-writer agents
  │   │   │   └── Per task: /check → fix findings → commit
  │   │   ├── Batch 2: [Task 2, Task 4] → parallel
  │   │   │   └── Per task: /check → fix findings → commit
  │   │   └── ...
  │   ├── /deep-review on full branch → fix findings → commit
  │   ├── Push + create PR
  │   └── Return to base branch
  ├── Execution summary
  └── Complete
```

**Why per-task agents:** Each task-agent starts with fresh context
containing only: its task file, Task 0 contracts, and "Context to Read
First" files. This avoids context pollution and keeps each agent focused.

**Why one branch per repo:** All tasks for a repo build on each other.
One branch keeps the commit history linear and produces one reviewable PR.

**Two-tier review:** `/check` after each task catches issues immediately
while context is fresh. `/deep-review` after all tasks catches cross-task
issues, security concerns, and architectural problems across the full
change set.

---

## Input Resolution

If `$ARGUMENTS` were provided, classify and resolve tasks:

1. **Story ID** (matches `story_NNN`): Read the story from
   `~/.claude/backlog-driven-development/artifacts/stories/{id}.json`.
   Read `index.json` and filter tasks where `storyId` matches. Read
   the plan summary from `plan-summaries/plan_NNN.json`.
2. **Story file path** (points to an artifact JSON file): Read the
   story, then look up tasks and plan summary in the artifacts directory.
3. **Bug ID** (matches `bug_NNN`): Respond: "Bugs use `/triage` instead
   of `/execute`. Run `/triage {bug_id}` to investigate and fix this bug."
   **Stop.** Do not proceed.
4. **No input or unrecognized**: Ask the user for a story ID
   (e.g., `story_001`).

**What to load:**
- **Story JSON** — acceptance criteria, context, dependencies
- **Plan summary JSON** — constraints, critical reminders, parallel
  execution schedule, open questions, status
- **All task JSONs** — for execution (filter `index.json` tasks by
  `storyId`, then read each `tasks/{id}.json`)

### Resumption

If the plan summary's status is `in-progress`:

1. Check each task JSON's `status` field
2. Cross-reference with `git log` to verify state
3. Identify complete vs. remaining tasks
4. Present: "Tasks 1-3 complete. Tasks 4-5 remaining."
5. Re-compute batches from remaining tasks
6. Resume from the first incomplete batch

---

## Phase 0: Pre-flight Checks

Before executing anything:

1. **Verify test runner** — check that the project has the test framework
   the tasks' Verification Commands depend on. If not installed, report.
2. **Spot-check Verification Commands** — pick 2-3 and confirm they are
   syntactically valid.
3. **Check git state** — `git status`. Warn about uncommitted changes.
4. **Record the base branch** — note the current branch name.

### Gate Check

1. **Status is `Approved`** — if not, warn and confirm.
2. **Open Questions resolved** — if any unchecked `- [ ]` items, STOP.
3. **Extract Constraints** — read Constraints and Critical Reminders.
   These are execution guardrails.

If all gates pass, set plan-summary.md Status to `In Progress`.

---

## Phase 1: Group Tasks by Repository

### Step 1: Classify Tasks by Repo

Read the `**Repository:**` field from each task file (or the plan header
for single-repo stories). Group tasks into per-repo sets.

If all tasks target one repo, skip multi-repo presentation.

If tasks span multiple repos:

> "This story spans [N] repositories:
>
> **[repo-1]:** Tasks 0, 1, 3, 5
> **[repo-2]:** Tasks 2, 4
>
> I'll execute each repo sequentially: [repo-1] first, then [repo-2].
> Each repo gets its own branch and PR."

### Step 2: Validate Repo Access

For each repo:
- Verify the local directory path exists
- If the directory doesn't exist, ask the user for the correct path

### Step 3: Compute Parallel Batches (per repo)

For each repo's task set, compute batches:

```
completed = {0}  // Task 0 already done (if in this repo)
batches = []
while unscheduled tasks remain:
  candidates = tasks where all Blocked By deps ∈ completed
  batch = [], batchFiles = {}, batchSymbols = {}
  for candidate in candidates (task order):
    // Check file overlap
    fileConflict = candidate.relevantFiles ∩ batchFiles ≠ ∅
    // Check symbol dependency: does this candidate consume a symbol produced by a batch member?
    symbolConflict = candidate.symbolDependencies ∩ batchSymbols ≠ ∅
    if not fileConflict and not symbolConflict:
      batch.add(candidate)
      batchFiles ∪= candidate.relevantFiles
      batchSymbols ∪= candidate.symbolsProduced  // symbols this task's changes export
  batches.add(batch)
  completed ∪= batch
```

**Symbol conflict detection:** Before dispatching a batch, read each task's
`symbolDependencies` array. If task B lists `"Task2.UserService.validateToken"` and
Task 2 is in the same candidate set but not yet `completed`, B cannot share a batch with
Task 2 — even if they touch different files. Task 2's produced symbols are derived from
its `changes` array entries that define public interfaces.

Cross-repo dependencies: if a task in this repo has `Blocked By` on a
task in another repo, treat the dependency as satisfied only if that
repo has already been processed. Warn the user if ordering matters.

### Step 4: Present Execution Plan

**Create TodoWrite entries** for every task — gives the user real-time
progress visibility.

Present the execution schedule per repo:

```
## Execution Schedule — [repo-name]

Branch: us-{story-slug}
Batch 1 (parallel): Task 1, Task 3
Batch 2 (parallel): Task 2 (blocked by 1), Task 4 ⏸ HUMAN
Batch 3: Task 5 (blocked by 2)

Total: 5 tasks, 3 batches
```

Flag Human tasks: "This plan contains N tasks marked for human
implementation. Execution will pause at each one." List the human tasks
upfront with their titles so the user can mentally prepare:
> "Human tasks in this plan:
> - Task N: [title] (Batch M)
> - Task N: [title] (Batch M)
>
> I'll pause when each is reached. You can prepare these in advance."

---

## Phase 2: Execute Per Repository

Process each repository sequentially. For each repo:

### Step 1: Create Branch

```
git checkout -b us-{story-slug}
```

If the branch already exists (resumption), check it out instead.

### Step 2: Execute Task 0 (Contracts)

Task 0 runs in the main session — not in a subagent — because all
subsequent tasks depend on it.

1. Read task-0/task.md and "Context to Read First" files
2. Execute the task (define types, interfaces, contracts)
3. Verify acceptance criteria pass
4. Commit: `"Task 0: [title]"`
5. Run `/check` against the commit — fix BLOCKING and SHOULD_FIX
   findings, commit fixes
6. Update task-0 status to `DONE`

### Step 3: Execute Batches

Process batches sequentially. Within each batch, dispatch all AI tasks
in parallel.

**Before dispatching each task agent:**

1. **Assumption check** — verify:
   - Do `Relevant Files` still exist (or not exist, as expected)?
   - Have `Context to Read First` interfaces changed?
   - Does `git status` show unexpected state?

   If assumptions violated, ask the user how to proceed.

**Each task-agent receives this prompt:**

```
Execute the following task using TDD.
You ONLY touch files listed in this task's Relevant Files section.

PLAN CONSTRAINTS — do NOT violate these under any circumstances:
[Constraints from plan-summary.md verbatim]

Before writing any code:
1. Read the task file at: [path to task-N/task.md]
2. Read every file listed in "Context to Read First"
3. Read the Task 0 contracts
4. Read the files listed in "Relevant Files"
5. If any listed file does not exist: STOP and report
6. If interfaces have changed: STOP and report

Task to execute:
- Task N: [title]

Stay within declared files. If anything is wrong, STOP and report.
```

**For each batch:**

1. Separate into AI tasks and Human tasks
2. Dispatch code-writer agents for all AI tasks simultaneously
3. Present Human tasks to the user and wait for confirmation
4. Wait for all agents to complete
5. **Batch commit gate** — before committing anything:
   - Collect results from all agents in the batch
   - Identify which succeeded and which stopped/failed
   - If ANY task failed: do NOT commit any task's changes. Run
     `git checkout -- .` on the relevant files for the failed task,
     leaving successful tasks' changes on disk but uncommitted.
     Ask: "Task N failed ([reason]). Tasks [X, Y] in this batch
     succeeded. Commit the successful tasks and mark Task N as BLOCKED,
     or roll back the whole batch?"
     - **Commit successful**: commit each successful task individually
       (`"Task N: [title]"`), mark failed task `BLOCKED`
     - **Roll back batch**: `git checkout -- .` on all batch files,
       mark failed task `BLOCKED`, no commits for this batch
   - If ALL tasks succeeded: commit each task individually in task-ID
     order (`"Task N: [title]"`) then run per-task completion procedure
6. Run per-task completion procedure for each committed task

**Per-task completion procedure:**

For a task that **succeeded**:

1. Commit: `"Task N: [title]"`
2. **Check constraints** — verify this commit doesn't violate any
   constraint from plan-summary.md
3. Run `/check` against the latest commit — **pass 1**
4. If `/check` finds BLOCKING or SHOULD_FIX issues: dispatch a fresh
   code-writer agent scoped to the task's declared files to fix them,
   then commit the fixes — **pass 2 (final)**
5. If pass 2 `/check` still has BLOCKING findings: do NOT loop further.
   Record the unresolved findings in the task's `executionNotes`, mark
   the task `BLOCKED`, and surface to the user:
   > "Task N: `/check` pass 2 still has BLOCKING findings after a fix
   > attempt. Human review required before proceeding. Findings: [list]"
   Ask whether to continue with unblocked tasks or stop entirely.
6. Update task status to `DONE` (or `BLOCKED` if step 5 triggered)
7. Mark TodoWrite entry as `completed`

For a task that **stopped** (reported failure):

1. Record the failure and reason
2. Update task file status to `BLOCKED`, append to Execution Notes:
   ```
   - Attempted [approach], failed because [reason].
     If retrying: [guidance].
   ```
3. Mark downstream tasks as blocked
4. Ask: "Task N failed. Tasks [X, Y] depend on it. Continue with
   unblocked tasks, or stop to investigate?"

**For Human tasks:**

1. Write a `.human_task.json` file to the artifact store at
   `~/.claude/backlog-driven-development/artifacts/.human_task.json`:
   ```json
   {
     "taskId": "task_NNN.N",
     "title": "...",
     "relevantFiles": [...],
     "acceptanceCriteria": [...],
     "doNot": [...],
     "checklist": ["implement the change", "verify locally", "confirm here"]
   }
   ```
2. Present the task to the user using AskUserQuestion:
   > "**Human Task: [title]**
   >
   > Files to modify: [relevantFiles]
   > Acceptance criteria: [AC list]
   > Do NOT: [doNot list]
   >
   > Complete this task in your editor, then reply "done" to continue."
3. Block until the user confirms (AskUserQuestion response)
4. Delete `.human_task.json`
5. If uncommitted changes exist in the task's relevant files, commit them:
   `"Task N: [title] (human)"`
6. Run `/check` → fix findings (max 2 passes per 3.2-A) → commit
7. Update task status to `DONE`
8. Mark TodoWrite entry as `completed`

### Step 4: Post-Implementation Test Re-Review

After ALL tasks for this repo complete, before `/deep-review`:

1. Collect the actual test files written during execution (from each
   task's `relevantFiles` entries where the file is a test file, plus
   any new test files visible in `git diff --name-only`)
2. Dispatch the `test-reviewer` agent via the Agent tool, passing:
   - All task JSON files for this story (the original test *descriptions*)
   - The actual test file paths written during execution
   - Instruction: "Review whether the actual tests match the intent of
     the task descriptions. Check: do real tests cover what the
     descriptions promised? Are there gaps between planned and
     implemented test coverage?"
3. If test-reviewer returns **RETHINK** or **STRENGTHEN** findings:
   - For CRITICAL/SERIOUS: dispatch a code-writer agent to close the
     gap (scoped to the relevant test files), commit:
     `"Test coverage fixes"`
   - For CONCERNS/NOTES: record in plan-summary `executionNotes` for
     human awareness but do not block progress

### Step 5: Final Deep Review

After the post-implementation test re-review:

1. Run `/deep-review` against the full branch (diff from base branch)
2. Review the consolidated findings
3. For BLOCKING and SHOULD_FIX findings: dispatch a code-writer agent
   to fix them, commit fixes: `"Deep review fixes"`
4. Run `/deep-review` one more time only if BLOCKING findings existed
   in the first pass — this is a single retry, not a loop

### Step 6: Push and Create PR

After deep review passes:

1. Push the branch: `git push -u origin us-{story-slug}`
2. If `gh` CLI is available, create a PR:

   ```
   gh pr create --title "[story title]" --body "$(cat <<'EOF'
   ## Summary
   [From story context — what this delivers and why]

   ## Changes
   [Bullet list from task titles]

   ## Test plan
   - [ ] All automated tests pass
   - [ ] [Manual verification items if any]

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

3. Update the story's `status` to `IN_REVIEW` in both `stories/{id}.json`
   and `index.json`
4. Record the PR URL

### Step 7: Return to Base

```
git checkout {base-branch}
```

If more repos remain, proceed to the next repo (back to Step 1).

---

## Phase 3: Execution Summary

After all repos are processed, present a summary:

```
## Execution Summary

### [repo-1]
Branch: us-{story-slug}
PR: #42 — [URL]
Tasks: 5 completed, 0 failed
Commits: 7 (5 tasks + 2 review fixes)
Files: 12 changed, +352 lines

### [repo-2]
Branch: us-{story-slug}
PR: #43 — [URL]
Tasks: 2 completed, 0 failed
Commits: 3 (2 tasks + 1 review fix)
Files: 4 changed, +89 lines

Total: 7 tasks, 2 PRs, +441 lines across 16 files
Issues: none
```

Update the plan summary JSON (`plan-summaries/plan_NNN.json`):
- Status → `complete` (plan summary status — unchanged)
- Add execution state with branch names, PR URLs, commit counts

Update artifact statuses:
- Set each completed task's `status` to `DONE` in both its JSON
  file and `index.json`
- Set the story's `status` to `DONE` in both its JSON file and
  `index.json`
- Update `lastModified` in `index.json`

Present next steps:

> "Execution complete. PRs created:
> - [repo-1]: [PR URL]
> - [repo-2]: [PR URL]
>
> Review and merge the PRs to complete this story."

---

## Key Principles

- **Tests first, always.** RED before GREEN. No exceptions.
- **Stay within declared file boundaries.** Each agent only touches its
  Relevant Files.
- **One branch per repo.** All tasks commit to the same branch.
- **Two-tier review.** `/check` per task (fast, focused). `/deep-review`
  per repo (thorough, cross-cutting).
- **Assumption check before every task.** No surprises mid-execution.
- **The plan is the prompt.** Follow it literally. If wrong, stop and
  report.
- **If stuck, ask — don't guess.** Ambiguous instructions → stop and
  report.

### Flagging Upstream Artifacts for Revision

During execution, if you discover that an upstream artifact is
inadequate:

1. Mark the artifact as `NEEDS_REFINEMENT` with a `revisionReason`
2. Inform the user with the specific issue and impact
3. Continue execution if possible, noting the deviation

### When the Plan Is Wrong

- **File doesn't exist**: STOP. Report to user.
- **Interface changed**: STOP. Task 0 contracts may need updating.
- **Test infrastructure missing**: Create as prerequisite within the
  task. Note the deviation.
- **Task too large** (> 200 lines): Report. User decides to split or
  continue.
- **Task contradiction**: STOP. Back to `/task-decomposition`.

For minor deviations (slightly different import path), adapt and note.
For scope or AC changes, stop.

---

## Pipeline

```
tasks/ (/task-decomposition)
  → /execute (this skill)
      Per repo:
        branch → tasks (parallel batches + TDD)
          → /check per task
          → /deep-review per repo
          → PR
  → user review + merge
  → Complete
```
