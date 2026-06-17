---
name: execute-spec
disable-model-invocation: true
model: opus
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
description: "Implements a spec produced by /specd:create-spec. Reads the spec, creates a feature branch, implements the changes with self-verification, then runs parallel staff and QA reviews. Does not push or create PRs."
---

# Execute — Implement a Spec

Read the spec. Do the work.

---

## Input

A feature is a folder of **slices** (`docs/specs/features/{slug}/` with an `index.md` plus one `{slice}.md` per slice). You run **one slice per call** — the chosen slice file is your contract, not `index.md` and not its siblings. Resolve `$ARGUMENTS` to a single slice file:

1. **Full path to a slice** (`docs/specs/features/{slug}/{slice}.md`): use directly.
2. **A feature folder or its `index.md`**: read `index.md`, then pick the **next unblocked slice** — the first row whose `Status` is `Waiting Implementation` and whose `Depends on` slices are all `Implemented`. If several are eligible, present them as a menu and ask.
3. **A bare feature slug**: resolve `docs/specs/features/{slug}/index.md`, then pick the next unblocked slice as in (2).
4. **No input**: build the menu with a single shell pass — don't read every slice into your context just to filter it. Grep for the waiting status across both spec roots, **excluding `index.md`**:

   ```bash
   grep -liE '(\*\*)?status(\*\*)?:[[:space:]]*Waiting Implementation' \
     docs/specs/features/*/*.md docs/specs/bugs/*/*.md 2>/dev/null \
     | grep -v '/index.md'
   ```

   (The `-i` makes it case-insensitive, so it matches the YAML front-matter `status:` key and still catches any older bold `**Status**:` body line. The `grep -v` drops the per-feature `index.md`, whose rollup status is not a runnable slice.) For each match, read its front-matter **`summary`** field for the one-line description. Group the matches by feature and show only the eligible (unblocked) slices, with slug and summary, then ask the user to choose. If none match, tell the user.

Read the chosen slice in full. This is your contract.

Also read `CLAUDE.md`, and `AGENTS.md` for project conventions and build/test commands, if it exists.

---

## Running tests and checks (always delegate)

**Never run a test suite, linter, or type-checker inline** (their output is large and noisy). **Every time** you need to run one (the verification command, at baseline, before each commit, in the fix-loop, at finalize), dispatch the `specd-test-runner` agent (`subagent_type: "specd-test-runner"`) with the exact command and repo root.

It returns a compact digest and only runs and reports. **You** judge which failures matter and what to fix. If a digest lacks the detail to debug a specific failure, ask the runner to re-run that one test with more verbosity (e.g. `-vv`), not the whole suite inline.

---

## Pre-flight

1. **Check prerequisites**: read the feature's `index.md`. Find the chosen slice's row and collect its `Depends on` slugs. (Cross-check the slice's front-matter `depends_on`; if the two disagree, `index.md` wins — warn the user about the mismatch.) Read each prerequisite slice's `Status` from the index table. If any prerequisite is **not `Implemented`**, warn which slices come first and their statuses, then ask whether to proceed anyway — don't auto-abort or auto-proceed:

   > "Slice `api-endpoint` depends on `data-model`, still `Waiting Implementation`. Shipping now may not work end-to-end. Proceed anyway, or run `data-model` first?"

2. **Branch**: if on `main`/`master`, create `feature/{slug}/{slice}` (e.g. `feature/checkout/data-model`) so this slice becomes its own PR. If on another branch, confirm with user. Never execute on main. Each slice branches off `main`/`master` — slices are sized to ship on their own; the prerequisite check above guards ordering.

3. **Test baseline**: have the test-runner run the slice's verification command. Record the pass/fail state and the **exact names of any already-failing tests**. If tests already fail, warn the user and treat precisely those tests as the pre-existing-failure set: excluded from the must-pass set, while every other test must pass and none may regress. Don't expand this set later to excuse a failure you introduced.

4. **Validate the spec**: dispatch the `specd-reference-linter` agent (`subagent_type: "specd-reference-linter"`) with the slice path. It verifies the files, symbols, named tests, and dependencies the slice references still exist in the *current* repo (the slice may have drifted since it was authored), and that any `depends_on` resolves to a sibling slice in the same folder. On any MISSING or MISLOCATED reference, stop and report before implementing: a slice pointing at moved or vanished code is a stale contract. (REVIEW rows are usually new things the slice intends to create.)

5. **Run linters and type checkers** if available (check CLAUDE.md, AGENTS.md), via the test-runner. Record baseline.

---

## Implementation

In this section and the ones below, "the spec" means the chosen slice file — the contract you read in full above, not `index.md` and not its sibling slices.

Read the slice's Approach, Constraints, and Edge cases sections. These are your boundaries.

### Principles

- Prefer a little repetition over the wrong abstraction. Do the simplest thing that satisfies the spec.
- One logical change per commit. Commit each concern separately.
- **Default to parallelizing independent work.** When the spec's concerns touch non-overlapping files, dispatch them as concurrent implementation subagents; stay single-threaded only when the changes are interdependent. Pass each subagent these principles, the spec path, and a targeted description of its change. Merge and verify the combined result **before any commit**; never commit unmerged or unverified subagent work.
- **Fail loud.** Catch only the specific exceptions the code can raise; never catch base exception classes; never ship a stub that fakes success (`return True  # in a real implementation...`). Both hide brokenness behind plausible success.
- **Match this codebase.** Find how this project already solves similar problems and follow that pattern; consolidate near-duplicates instead of adding parallel implementations.
- **Least code that works.** No speculative abstractions, no indirection for single callers, stdlib over hand-rolling; delete dead code outright (git is the backup).
- **Comments explain why, never what.** Delete a comment that restates the code. Update adjacent comments when behavior changes.
- **Test real behavior.** Realistic inputs through real libraries, deterministic sync (no sleeps), fixtures with real-world mess. Never modify a test to make it pass; flag it instead.


### Doing the work

Read each file in "Files that matter" before modifying it. Understand what's there before changing it.

Implement the changes described in the spec. Use the "Current behavior" section to find the starting point. Use "Constraints" and "Edge cases" to guide the implementation and stay in scope. Follow the "Approach". If you encounter a blocker the approach didn't anticipate, stop and report rather than silently switching to a different approach.

If the "Alternatives rejected" section lists an approach, do not use that approach, it was explicitly rejected during planning.

---

## Before Each Commit

After each logical unit of work, before committing:

1. **Run linters and type checkers** (via the test-runner). Fix any new violations.
2. **Run the tests relevant to the change** via the `specd-test-runner` agent (`subagent_type: "specd-test-runner"`); at minimum the scope of the spec's verification command. All must pass; never commit on a red state you introduced.
3. **Diff the tests.** Run `git diff` and `git status` against the test directories. For every test file the change modified, deleted, or skipped, confirm the spec justifies it, not a weakened assertion papering over a failure. Record each touched test file and its justification for the summary. If a test was changed only to make it pass, revert it and fix the code.

Then commit with a clear message. Keep commits under 400 changed lines (review effectiveness drops sharply beyond that); split a larger logical change into smaller commits.

---

## Verification

**You are not done until the spec's verification criteria pass.**

Have the `specd-test-runner` agent run the spec's verification command. Check every assertion:
- All existing tests listed must still pass.
- All new behaviors described must be verified.
- On any failure, fix it and re-verify (re-run via the test-runner).

Run linters and type checkers again (via the test-runner); fix any new violations. Don't commit until verification passes, and don't trust your own judgment that the code is correct: run the actual commands.

Stop and report to the user with details when either holds: verification has failed after five fix attempts, or you are re-applying a substantially similar fix. Five different hypotheses is healthy debugging; repeating one fix means you are stuck. Watch for repetition, not just the attempt count.

---

## Final Review

**First, re-read the spec's Constraints and Edge cases sections.** This command runs long (implementation, four reviewers, up to three fix-and-re-review rounds), exactly the session length where context compaction silently drops constraints. Re-anchor on the contract rather than trust a compaction summary to have preserved it.

Then launch four review agents **in parallel** (one message, four Agent calls). Delegate every review to these agents; do not review your own diff, since models fail to correct their own errors.

1. **`specd-staff-reviewer`** (`subagent_type: "specd-staff-reviewer"`): security, correctness, performance, reliability.
2. **`specd-code-quality-reviewer`** (`subagent_type: "specd-code-quality-reviewer"`): architectural hallucinations in AI-generated code.
3. **`specd-qa-reviewer`** (`subagent_type: "specd-qa-reviewer"`): test quality, coverage, edge-case handling.
4. **`specd-compliance-reviewer`** (`subagent_type: "specd-compliance-reviewer"`): did we build what the spec said?

Pass all four the same inputs:
- `diff`: this slice's diff (`git diff <base-branch>...HEAD`, where `<base-branch>` is `main`/`master`, the branch this slice was cut from)
- `spec_path`: the slice file path

When all four return, merge their findings (deduplicate overlap), then resolve:

- **Staff / QA / code-quality findings**: fix all BLOCKING and SHOULD_FIX. SUGGESTIONS may be deferred or skipped if out of scope; note any you skip and why.
- **Compliance deviations** (NON_COMPLIANT): if the spec is right and the code drifted, fix the code. A deviation may instead be a reasonable amendment — an edge case the spec missed, or a constraint that turned out wrong (e.g. the spec said "retry 3 times" but exponential backoff with 5 retries is better). You may **propose** an amendment. You may not decide one yourself and then mark the work compliant. Do not edit the spec to match the code and call that compliance. So: list every proposed amendment under **Needs attention** in the summary, not only under "resolved deviations". If you modified the spec during execution, get explicit user confirmation before flipping `Status` to `Implemented`. Do not finalize while any uncorrected non-compliance remains.

After fixing, re-run each reviewer whose findings you addressed (or whose scope your fixes touched) until staff, code-quality, and QA return APPROVE and compliance returns COMPLIANT. If BLOCKING findings remain after three rounds, stop and report the open findings rather than looping further.

---

## Finalize

After verification passes:

1. Run the full test suite (from CLAUDE.md's operational commands) via the test-runner to check for regressions beyond the spec's verification scope. Fix any regressions before finalizing.

2. Update the slice's front-matter `modified` date to today if implementation revealed new constraints or edge cases worth recording (or if the compliance review prompted amendments). Also fill in the front-matter `model` field with the model that did this execution. Optionally record `tokens`, `cost`, and `reasoning_effort` if you have them; otherwise leave them blank.

3. **Flip status in three places** — slice, then `index.md`, then the Spec Index. **If the slice was amended during execution, do not flip to `Implemented` without explicit user confirmation** — present the amendments first (step 4) and wait. Otherwise:

   a. **Slice front-matter**: `status` → `Implemented`.

   b. **`index.md`** (`docs/specs/features/{slug}/index.md`): flip this slice's `Status` cell in the Slices table to `Implemented`. Then **recompute the front-matter rollup `status`** from the table — `In Progress — {k}/{N} slices implemented` if some remain, `Implemented` if all are now done (see `index-template.md`). Bump `index.md`'s `modified` to today.

   c. **Spec Index** (`docs/specs/spec.md`): copy `index.md`'s new rollup string into the feature row's Status column, and set its `Updated` column to today. If the feature lives under `docs/specs/bugs/`, update the Bugs table; otherwise the Features table.

4. Present a summary:
   - **Branch**: name (`feature/{slug}/{slice}`) and commit count
   - **Next slice**: the next unblocked slice from `index.md` to run, or "all slices implemented — feature complete"
   - **What was done**: 2-3 sentences
   - **Verification**: pass/fail status, and the pre-existing-failure set excluded at baseline
   - **Final review findings**: issues caught and fixed by the staff, code-quality, and QA reviews
   - **Tests touched**: every test file modified, deleted, or skipped, each with its spec justification (or "none")
   - **Compliance review**: COMPLIANT, or list of resolved deviations
   - **Spec gaps** (if any): context you had to discover beyond the spec — a reference you re-located, a file it didn't point to, behavior or a data contract you reverse-engineered, setup it omitted. One concrete line each. This is the spec's retrospective: how the next spec improves and where CLAUDE.md gaps surface. List every gap you actually hit during execution. Write "none" if the spec was sufficient; report a gap only when you hit one, not to look thorough.
   - **Needs attention** (if any): every spec amendment proposed or made during execution, plus anything unexpected or that the user should review

**Do NOT push or create a PR.** The user handles this.
