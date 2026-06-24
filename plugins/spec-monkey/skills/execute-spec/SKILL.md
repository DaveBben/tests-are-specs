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

# Execute — Implement a Spec

Read the spec. Implement the task you're given, exactly as written. Review. Record.

The spec is your contract. If reality contradicts it, **stop and report** — never silently
switch approaches or edit the spec to match the code.

## Phase 1 — Find the spec

A spec is one file at `docs/specs/{slug}/spec.md`. Resolve `$ARGUMENTS`:

1. **Full path to a `spec.md`** → use it.
2. **A bare slug** → `docs/specs/{slug}/spec.md`.
3. **A slug + task id** (e.g. `auth T2`) → that spec, that task.
4. **No input** → list implementable specs in one shell pass, then ask:

   ```bash
   grep -lE '^status:[[:space:]]*(reviewed|applied)' docs/specs/*/spec.md 2>/dev/null
   ```

   A `reviewed` or `applied` spec with un-done tasks is implementable.

Read the spec **in full** — it's your contract. Read the constitution its `standards:`
frontmatter names (`standards.md` / `CLAUDE.md` / `AGENTS.md`) for invariants, commands, and
boundaries.

## Phase 2 — Pick the task(s)

Read the spec's **Tasks** table (`id | task | files | AC | depends_on | wave | est_diff | done`).

- Show the user the un-done tasks: id, summary, `est_diff`, `wave`, and whether each task's
  `depends_on` are already `done`.
- Ask which to implement. **Default: one task = one MR.**
- Be mindful of size and context. If the user picks several, warn when the combined
  `est_diff` or the files to load would blow past ~400 diff lines or a large context. A
  `wave` marks tasks that *can* go in parallel, but each is still its own MR unless the user
  says otherwise.
- Refuse a task whose `depends_on` aren't `done` — name what must land first.

## Phase 3 — Implement, exactly as specified

Build the selected task(s) per the spec's **Approach**, the **Files / Change Manifest** rows
the task names, the **Data Model & Contracts**, and the acceptance criteria the task covers.

Pre-flight:

- **Branch.** Create a branch for the task only when you're on `main`/`master` **and** in
  the primary checkout — not a linked worktree. A linked worktree is already an isolated
  workspace, so stay on its branch even if it's `main`. Detect it: a linked worktree has
  `git rev-parse --git-dir` differing from `git rev-parse --git-common-dir`. On a non-main
  branch, confirm before proceeding.
- **Baseline.** Have `spec-monkey:test-runner` run the spec's verification command. Record
  already-failing tests; they're excluded from must-pass. Nothing else may regress.
- **Validate.** Dispatch `spec-monkey:reference-linter` on the spec. On any MISSING or
  MISLOCATED reference, stop and report — a stale manifest is a stale contract.

Doing the work:

- Navigate by the manifest, don't re-read whole files: `modify` → read the symbol + edit;
  `context` → read to orient, don't change; `new` → create; `delete` → read enough to remove
  cleanly. Stay within the task's rows — the diff should match them.
- **Fail loud.** Catch only the specific exceptions raised; never ship a stub that fakes
  success. **Least code that works.** Match how this codebase already solves the problem.
- **Test real behavior.** Realistic inputs through real libraries; each test must be able to
  fail (name the line that, deleted, reddens it); derive expected values independently — never
  from the code's own constants; exercise an error path. Never weaken a test to make it pass.
- **Always delegate** test / lint / type runs to `spec-monkey:test-runner` — never inline,
  the output is noisy and floods context. Keep each commit ≤ ~400 changed lines.

Hit a blocker the Approach didn't anticipate → stop and report.

## Phase 4 — Verify

You are not done until the spec's **Verification** passes.

- Run the Verification commands (via the spec-monkey:test-runner). Every acceptance criterion the task
  covers maps to a passing check — including each error path. If the task implements an NFR,
  confirm its **Measurement** is met, or flag that it needs a benchmark you can't run here.
- Run the spec's **Self-check**: re-walk every criterion, confirm each Constraint is met, and
  confirm `git diff` touches only the task's manifest rows.
- Stop and report after five fix attempts, or once you're repeating a fix.

## Phase 5 — Review (parallel)

Re-read the spec's **Constraints** and **Edge Cases** first — this run is long, and that's
exactly where a summary silently drops the contract.

Launch four reviewers **in parallel** (one message, four Task calls). Never review your own
diff. Pass each the same inputs — `diff`: `git diff <base-branch>...HEAD`; `spec_path`: the
spec file.

1. **`spec-monkey:staff-reviewer`** — security, correctness, performance, reliability.
2. **`spec-monkey:code-quality-reviewer`** — architectural hallucinations in AI code.
3. **`spec-monkey:qa-reviewer`** — test quality, coverage, edge cases.
4. **`spec-monkey:compliance-reviewer`** — did we build what the spec said?

Merge findings (dedup). Fix all BLOCKING and SHOULD_FIX from staff/qa/code-quality;
SUGGESTIONS may be deferred (note which and why). For compliance: if the spec is right and
the code drifted, fix the code; a real deviation may be a **proposed** amendment — never edit
the spec to match the code and call it compliant. Re-review in scoped re-verification mode
(only the reviewers whose findings you addressed). Default one re-round; ceiling three.

## Phase 6 — Finalize

- Run the **full** test suite (via the spec-monkey:test-runner) for regressions beyond the task's scope.
- Mark the task(s) `done` in the spec's Tasks table.
- If **every** task is now `done`, flip the spec's `status` → `applied`; otherwise leave it
  `reviewed`. If you amended the spec during execution, get explicit user confirmation before
  flipping.
- Append to the **Activity Log**: what shipped, every test file touched (with its
  justification), spec gaps you hit, and any proposed amendments.
- Present a summary: branch + commit count; what was done (2–3 sentences); verification
  result (with the pre-existing-failure set); review findings fixed; tests touched; compliance;
  spec gaps ("none" if the spec was sufficient); needs-attention (amendments, anything to review).

**Do NOT push or create a PR. The user handles that.**
