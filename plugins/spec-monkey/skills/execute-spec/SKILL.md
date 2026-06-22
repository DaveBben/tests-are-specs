---
name: execute-spec
disable-model-invocation: true
model: sonnet
effort: high
argument-hint: "[path to spec file]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - Write
  - Task
description: "Implements a spec produced by /spec-monkey:create-spec. Reads the spec, creates a feature branch, implements the changes with self-verification, then runs parallel staff and QA reviews. Does not push or create PRs."
---

# Execute — Implement a Spec

Read the spec. Do the work.

---

## Input

A feature is a folder of **slices** (`docs/specs/features/{slug}/` — an `_index.md` plus one `{slice}.md` each). Run **one slice per call**; that slice file is your contract, not `_index.md` or its siblings. Resolve `$ARGUMENTS`:

1. **Full path to a slice**: use directly.
2. **A feature folder or its `_index.md`**: read `_index.md`, pick the **next unblocked slice** — the first row in a ready-to-implement state whose `Depends on` slices are all `Implemented`. The ready state is `Reviewed` for v3 features (`schema_version: v3`) and `Waiting Implementation` for legacy v2 features (`schema: v2`). Several eligible → present a menu and ask.
3. **A bare slug**: resolve `docs/specs/features/{slug}/_index.md`, then pick as in (2).
4. **No input**: find ready slices in one shell pass — don't read every slice into context just to filter. Match both the v3 ready state (`Reviewed`) and the legacy v2 one (`Waiting Implementation`):

   ```bash
   grep -liE '(\*\*)?status(\*\*)?:[[:space:]]*(Reviewed|Waiting Implementation)' \
     docs/specs/features/*/*.md docs/specs/bugs/*/*.md 2>/dev/null | grep -v '/_index.md'
   ```

   For each match read its front-matter `summary`. Group by feature, show only unblocked slices (slug + summary), and ask. None → tell the user.

Read the chosen slice **in full** — this is your contract. For a v3 slice, also read the **constitution** its `standards:` front-matter names (`standards.md` / `CLAUDE.md` / `AGENTS.md`) — it holds the invariants, commands, and boundaries the slice's `Principles` and `Boundaries` excerpt. Also read `CLAUDE.md` and `AGENTS.md` (if present) for conventions and build/test commands.

---

## Running tests and checks (always delegate)

**Never run a test suite, linter, or type-checker inline** — the output is large and noisy. **Every time** you need one (verification command, baseline, pre-commit, fix-loop, finalize), dispatch `spec-monkey-test-runner` (`subagent_type: "spec-monkey-test-runner"`) with the exact command and repo root.

It runs and returns a compact digest; **you** judge which failures matter and what to fix. If a digest lacks the detail to debug a failure, ask the runner to re-run that one test with more verbosity (`-vv`) — not the whole suite inline.

---

## Pre-flight

1. **Prerequisites**: read `_index.md`, find the slice's row, collect its `Depends on` slugs. (Cross-check the slice's front-matter `depends_on`; on disagreement `_index.md` wins — warn the user.) Read each prerequisite's `Status`. If any is **not `Implemented`**, warn which come first and ask whether to proceed — don't auto-abort or auto-proceed.

2. **Branch**: on `main`/`master`, create `feature/{slug}/{slice}` so this slice is its own PR. On another branch, confirm with the user. **Never execute on main.**

3. **Test baseline**: have the test-runner run the slice's verification command. Record pass/fail and the **exact names of already-failing tests** — that is the pre-existing-failure set, excluded from must-pass. Every other test must pass and none may regress. Don't expand this set later to excuse a failure you introduced.

4. **Validate the spec**: dispatch `spec-monkey-reference-linter` (`subagent_type: "spec-monkey-reference-linter"`) with the slice path. It checks that the files, symbols, named tests, and dependencies the slice cites still exist in the *current* repo. On any MISSING or MISLOCATED reference, stop and report before implementing — a slice pointing at moved or vanished code is a stale contract. (REVIEW rows are usually things the slice intends to create.)

5. **Lint/type baseline**: if the project has linters or type checkers (per CLAUDE.md/AGENTS.md), run them via the test-runner and record baseline.

---

## Implementation

"The spec" below means the chosen slice file, not `_index.md` or its siblings. Read its Approach, Constraints, and Edge cases — your boundaries. For a slice, also read its `Boundaries (this slice)` (the ✅/⚠️/🚫 tiers — never do a 🚫, ask before a ⚠️) and its `Tasks` table (your ordered worklist).

### Principles

- One logical change per commit.
- **Fail loud.** Catch only the specific exceptions the code can raise; never base classes; never ship a stub that fakes success.
- **Match this codebase.** Follow how the project already solves similar problems; consolidate near-duplicates instead of adding parallel implementations.
- **Least code that works.** No speculative abstractions, no indirection for single callers, stdlib over hand-rolling; delete dead code outright (git is the backup).
- **Comments explain why, never what.** Delete a comment that restates the code; update adjacent comments when behavior changes.
- **Test real behavior.** Realistic inputs through real libraries, deterministic sync (no sleeps), fixtures with real-world mess. Each test must be able to fail — name the production line that, deleted, reddens it. Derive expected values independently; don't import the code's own constants or messages as the assertion target. Exercise an error path with genuinely bad input. When sibling tests share an observable contract (a log line, an error field), every one asserts it. Never modify a test to make it pass; flag it instead.

### Doing the work

The **Files** manifest is an index, not a reading list. The investigation already located each symbol — don't re-read whole files to rediscover it. Navigate by the symbol anchor and each entry's mode.

For a slice, Files is a table with a `mode` column:
 - **modify** → read the cited symbol and nearby lines, then edit
 - **context** → read just enough to orient; do NOT change it
 - **new** → read nothing, you're creating it

(Legacy v2 slices group entries under **Modified** / **Context** / **Removed** / **New** subheadings — same navigation, plus **Removed** → read just enough to delete it cleanly.)

**Tasks checklist.** A slice carries a `Tasks` table (`id | task | files | [P] | done`) in dependency order. Work it top to bottom; a `[P]` task may run alongside its siblings. As you finish each task, flip its `done` cell to `x` in the slice file — the checklist is resumable, so a re-run picks up where you left off.

If an anchor is wrong or too thin to change the code safely, widen the read — then record it as a spec gap in the retrospective, because the index should have been enough.

Implement what the spec describes: "Current behavior" is your starting point, "Constraints" and "Edge cases" keep you in scope, follow the "Approach". Hit a blocker the Approach didn't anticipate → stop and report; don't silently switch approaches. Never use an approach listed under "Alternatives rejected" — it was rejected during planning.

---

## Before Each Commit

After each logical unit of work, before committing:

1. **Lint and type-check** (via the test-runner). Fix new violations.
2. **Run the relevant tests** (via the test-runner) — at minimum the spec's verification scope. All must pass; never commit on a red state you introduced.
3. **Diff the tests.** `git diff`/`git status` the test directories. For every test file modified, deleted, or skipped, confirm the spec justifies it — not a weakened assertion papering over a failure. Record each touched test file and its justification for the summary. A test changed only to make it pass → revert it and fix the code. Confirm each new or changed test can fail (name the line that, deleted, reddens it); a test that cannot fail is a finding.

Then commit with a clear message. Keep commits under 400 changed lines (review effectiveness drops sharply beyond that); split a larger change into smaller commits.

---

## Verification

**You are not done until the spec's verification criteria pass.**

Have the test-runner run the spec's verification command and check every assertion: all listed existing tests still pass, all new behaviors are verified, and any failure gets fixed and re-verified. For a **v3** slice, each EARS assertion (`V1`, `V2`, …) must map to exactly one passing test — including every `[error — required]` path — and you then run the slice's own **Self-check** (re-walk every assertion, confirm every Constraint is met, confirm the Files manifest equals the changed files). Run linters and type checkers again; fix new violations. Don't trust your own judgment that the code is correct — run the actual commands.

Stop and report when verification still fails after **five** fix attempts, or when you're re-applying a substantially similar fix. Five different hypotheses is healthy debugging; repeating one fix means you're stuck — watch for repetition, not just the attempt count.

---

## Final Review

**First, re-read the spec's Constraints and Edge cases** (and, for a v3 slice, its `Boundaries (this slice)` and the `Self-check`). This command runs long (implementation, four reviewers, up to three fix rounds) — exactly where compaction silently drops constraints. Re-anchor on the contract, don't trust a summary to have kept it.

Then launch four review agents **in parallel** (one message, four Agent calls). Delegate every review — don't review your own diff, since models fail to correct their own errors.

1. **`spec-monkey-staff-reviewer`**: security, correctness, performance, reliability.
2. **`spec-monkey-code-quality-reviewer`**: architectural hallucinations in AI-generated code.
3. **`spec-monkey-qa-reviewer`**: test quality, coverage, edge-case handling.
4. **`spec-monkey-compliance-reviewer`**: did we build what the spec said?

Pass all four the same inputs — `diff`: `git diff <base-branch>...HEAD` (base = the `main`/`master` this slice cut from); `spec_path`: the slice file.

When all four return, merge their findings (dedup overlap) and resolve:
- **Staff / QA / code-quality**: fix all BLOCKING and SHOULD_FIX. SUGGESTIONS may be deferred or skipped if out of scope — note which and why.
- **Compliance (NON_COMPLIANT)**: if the spec is right and the code drifted, fix the code. A deviation may instead be a reasonable amendment — an edge case the spec missed, or a constraint that proved wrong. You may **propose** an amendment; you may not decide one yourself and then mark the work compliant, and never edit the spec to match the code and call that compliance. List every proposed amendment under **Needs attention**. If you modified the spec during execution, get explicit user confirmation before flipping `Status` to `Implemented`. Don't finalize while any uncorrected non-compliance remains.

After fixing, re-review in **re-verification mode** — a scoped re-check of your fixes, not a fresh full review. Re-dispatch only the reviewers whose findings you addressed, passing each `fix_diff` (the diff of just your fixes), `prior_findings` (their findings you claim resolved), and `spec_path`. They mark each RESOLVED/NOT_RESOLVED and scan only `fix_diff` for regressions — a fresh full review re-pays the entire diff + spec; the scoped check doesn't.

**Default to one re-review round.** Later rounds mostly surface low-confidence false positives, not real bugs. Open a second only on a **new BLOCKING** finding absent from the original review. The three-round ceiling is a backstop, not a target — stop and report any BLOCKING that remains after it. Continue until staff, code-quality, and QA APPROVE and compliance is COMPLIANT (or you hit the ceiling).

---

## Finalize

After verification passes:

1. Run the **full** test suite (CLAUDE.md's operational commands, via the test-runner) to catch regressions beyond the spec's scope. Fix any before finalizing.

2. Update the slice's front-matter `modified` to today if implementation revealed new constraints or edge cases worth recording (or compliance prompted amendments). Leave the `execution` block for step 5.

3. **Flip status in three places** — slice, `_index.md`, Spec Index. **If the slice was amended during execution, don't flip to `Implemented` without explicit user confirmation** (present the amendments in step 4 first). Otherwise:
   a. **Slice front-matter**: `status` → `Implemented` (from `Reviewed` for v3, or `Waiting Implementation` for v2).
   b. **`_index.md`**: flip this slice's `Status` cell, then recompute the front-matter rollup `status` from the table. v3 rollup rules: any slice still `Draft` → `Draft`; all `Reviewed`, none implemented → `Reviewed`; some implemented → `In Progress — {k}/{N} slices implemented`; all implemented → `Implemented` (see `index-template-v3.md`). v2 features use `index-template.md`'s rules. Bump `modified` to today.
   c. **Spec Index** (`docs/specs/spec.md`): copy the new rollup into the feature row's Status, set `Updated` to today. A feature under `docs/specs/bugs/` updates the Bugs table; otherwise Features.

4. Present a summary:
   - **Branch**: name (`feature/{slug}/{slice}`) and commit count
   - **Next slice**: the next unblocked slice from `_index.md`, or "all slices implemented — feature complete"
   - **What was done**: 2–3 sentences
   - **Verification**: pass/fail, plus the pre-existing-failure set excluded at baseline
   - **Final review findings**: issues caught and fixed by the reviews
   - **Tests touched**: every test file modified, deleted, or skipped, each with its spec justification (or "none")
   - **Compliance**: COMPLIANT, or list of resolved deviations
   - **Spec gaps** (if any): context you had to discover beyond the spec — a reference you re-located, a file it didn't point to, behavior or a data contract you reverse-engineered, setup it omitted. One concrete line each; this is the spec's retrospective. "none" if the spec was sufficient — report a gap only when you hit one, not to look thorough.
   - **Needs attention** (if any): every spec amendment proposed or made, plus anything the user should review

5. Offer to record the run's cost: "If you want this run's cost recorded in the slice's `execution` block, run `/cost` and paste the output." If pasted, fill the `execution` block — `total_cost` from "Total cost", `total_duration` from the wall duration, one `usage_by_models` entry per model (`model`, `input`, `output`, `cache_read`, `cache_write`, `cost`). Bump the slice's `modified` to today.

**Do NOT push or create a PR.** The user handles this.
