---
name: execute-spec
model: opus
effort: high
argument-hint: "[spec slug or path, optionally a task id]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - Write
  - Task
description: "Implement an approved spec produced by /spec-monkey:create-spec. Finds the spec, lets you pick which task(s) to implement, builds them exactly as specified, runs parallel reviews. One task is one MR-sized unit. Does not push or create PRs."
---

# Execute: Implement a Spec

Read the spec. Implement the task you're given, exactly as written. Review. Record.

The spec is your contract for WHAT and WHY (and the data contracts). The task's section in
`tasks.md` is your contract for HOW: the file manifest and run commands. If reality contradicts
either, **stop and report**. Never silently switch approaches or edit the spec to match the code.

## Phase 1: Find the spec

A spec lives in `docs/specs/{slug}/`: the core `spec.md` plus a sibling `tasks.md` (readable
per-task sections). The spec's history is git: `git log -- docs/specs/{slug}/`. Resolve
`$ARGUMENTS`:

1. **Full path to a `spec.md`** → use it.
2. **A bare slug** → `docs/specs/{slug}/spec.md`.
3. **A slug + task id** (e.g. `auth T2`) → that spec, that task.
4. **No input** → list implementable specs in one shell pass, then ask:

   ```bash
   grep -lE '^status:[[:space:]]*(decomposed|applied)' docs/specs/*/spec.md 2>/dev/null
   ```

   A `decomposed` or `applied` spec with un-done tasks is implementable. (A `reviewed` spec has
   no tasks yet: it hasn't been decomposed.)

Read the spec **in full**. It's your contract. Read the constitution its `standards:`
frontmatter names (`standards.md` / `CLAUDE.md` / `AGENTS.md`) for invariants, commands, and
boundaries.

## Phase 2: Pick the task(s)

Read the per-task sections from `tasks.md`. Each `## T#` carries a trace line
(`wave N · ~LOC · implements FR-… · verifies SC-… · depends_on …`), a `**Files**` table, a
`**Run**` block, and a `- [ ] done` checkbox.

- Show the user the un-done tasks: id, summary, `~LOC`, `wave`, and whether each task's
  `depends_on` are already done.
- Ask which to implement. **Default: one task = one MR.**
- Be mindful of size and context. A `wave` marks tasks that *can* go in parallel, but each is still
  its own MR unless the user says otherwise. If the user picks several **independent** same-wave
  tasks, you'll fan them out to parallel sonnet subagents in Phase 3 — so per-task context is not a
  worry, but still flag any single task whose own `~LOC` blows past ~400 diff lines.
- Refuse a task whose `depends_on` aren't done. Name what must land first.

## Phase 3: Implement, exactly as specified

Build the selected task(s) per the task's **Files** manifest and **Run** commands (in its
`tasks.md` section), the spec's **Data contracts**, and the requirements (`FR-…`) the task
implements.

**Solo or fan out.** One task: build it yourself, following the rest of this phase. **Several
independent tasks the user wants in this run** — same `wave`, no `depends_on` between them, no
shared files — fan out instead of building serially. Launch one **sonnet** subagent per task in a
single message (parallel `Task` calls). Give each only what it needs, nothing more:

- the **spec path** — its contract for WHAT/WHY and the *Data contracts*;
- a pointer to its **task's `## T#` section in `tasks.md`** — the Files rows it may touch and its
  Run block;
- the **`standards:` constitution** the spec names;
- a tight brief: implement exactly that task and its tests, stay inside its Files rows, run its
  **Run** commands to self-check, and return the files changed plus the test result.

You orchestrate; you do not implement in parallel yourself. Independent tasks touch disjoint
files, so their subagents share the working tree safely. When they return, commit each task
separately (one task = one MR), then take the whole set through Verify and Review below. Sequence —
never fan out — when tasks depend on each other or touch the same file.

Pre-flight:

- **Branch.** Create a branch for the task only when you're on `main`/`master` **and** in the
  primary checkout, not a linked worktree. A linked worktree is already an isolated workspace, so
  stay on its branch even if it's `main`. Detect it: a linked worktree has `git rev-parse
  --git-dir` differing from `git rev-parse --git-common-dir`. On a non-main branch, confirm first.
- **Baseline.** Have `spec-monkey:test-runner` run the task's **Run** commands (and the spec's
  *How I know it works* verification). Record already-failing tests; they're excluded from
  must-pass. Nothing else may regress.
- **Validate.** Dispatch `spec-monkey:reference-linter` on the spec folder. On any MISSING or
  MISLOCATED reference in the task's manifest, stop and report. A stale manifest is a stale contract.

Doing the work:

- Navigate by the task's **Files** rows, don't re-read whole files: `modify` → read the symbol +
  edit; `context` → read to orient, don't change; `new` → create; `delete` → read enough to remove
  cleanly. Stay within the task's rows. The diff should match them.
- **Fail loud.** Catch only the specific exceptions raised; never ship a stub that fakes success.
  **Least code that works.** Match how this codebase already solves the problem.
- **Test real behavior.** Realistic inputs through real libraries; each test must be able to fail
  (name the line that, deleted, reddens it); derive expected values independently, never from the
  code's own constants; exercise an error path. Never weaken a test to make it pass.
- **Always delegate** test / lint / type runs to `spec-monkey:test-runner`. Never run them inline:
  the output is noisy and floods context. Keep each commit ≤ ~400 changed lines.

Hit a blocker the design didn't anticipate → stop and report.

## Phase 4: Verify

You are not done until the task's **Run** commands and the spec's *How I know it works*
verification pass.

- Run them (via `spec-monkey:test-runner`). Every requirement (`FR-…`) the task implements maps to
  a passing check, including each error path. If the task carries the test for a success criterion
  (`verifies SC-…`), confirm that check exists and passes.
- **Self-check** before moving on: re-walk each `FR-…` the task implements and confirm it's
  satisfied; confirm each **Constraint** (*How it fits*) the task is bound by is met; confirm
  `git diff` touches only the task's **Files** rows and introduces no stray edits elsewhere.
- Stop and report after five fix attempts, or once you're repeating a fix.

## Phase 5: Review (parallel)

Re-read the spec's **Constraints** (*How it fits*) and **What could go wrong** (edge cases) first:
this run is long, and that's exactly where a summary silently drops the contract.

Launch four reviewers **in parallel** (one message, four Task calls). Never review your own diff.
Pass each the same inputs: `diff` is `git diff <base-branch>...HEAD`; `spec_path` is the spec file
(its sibling `tasks.md` is read alongside it for the manifest).

1. **`spec-monkey:staff-reviewer`**: security, correctness, performance, reliability.
2. **`spec-monkey:code-quality-reviewer`**: architectural hallucinations in AI code.
3. **`spec-monkey:qa-reviewer`**: test quality, coverage, edge cases.
4. **`spec-monkey:compliance-reviewer`**: did we build what the spec said?

Merge findings (dedup). Fix all BLOCKING and SHOULD_FIX from staff/qa/code-quality; SUGGESTIONS
may be deferred (note which and why). For compliance: if the spec is right and the code drifted,
fix the code. A real deviation may be a **proposed** amendment. Never edit the spec to match the
code and call it compliant. Re-review in scoped re-verification mode (only the reviewers whose
findings you addressed). Default one re-round; ceiling three.

## Phase 6: Finalize

- Run the **full** test suite (via `spec-monkey:test-runner`) for regressions beyond the task's scope.
- Mark the task(s) done: flip `- [ ] done` → `- [x] done` in each task's section in `tasks.md`.
- If **every** task is now done, flip the spec's `status` → `applied` in `spec.md`; otherwise leave
  it `decomposed`. If you amended the spec during execution, get explicit user confirmation before
  flipping.
- **Record the narrative in the commit message: git is the spec's audit trail, not a log file.**
  In the commit(s) for this task capture: what shipped, every test file touched (with its
  justification), spec gaps you hit, and any proposed amendments. Surface a proposed amendment in
  your report so the user can accept it into the spec. Never apply it silently.
- Present a summary: branch + commit count; what was done (2-3 sentences); verification result
  (with the pre-existing-failure set); review findings fixed; tests touched; compliance; spec gaps
  ("none" if the spec was sufficient); needs-attention (proposed amendments, anything to review).

**Do NOT push or create a PR. The user handles that.**
