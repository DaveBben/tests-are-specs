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

Resolve `$ARGUMENTS` to a spec file:

1. **Full path** (`docs/specs/features/{slug}/spec.md`): use directly
2. **Slug**: try `docs/specs/features/{slug}/spec.md`
3. **No input**: build the menu with a single shell pass — don't read every spec into your context just to filter it. Grep for the waiting status across both spec roots, e.g.:

   ```bash
   grep -lE '(\*\*)?Status(\*\*)?:[[:space:]]*Waiting Implementation' \
     docs/specs/features/*/spec.md docs/specs/bugs/*/spec.md 2>/dev/null
   ```

   (The pattern matches the status whether it's written as a `**Status**:` body line or a plain frontmatter key, so it doesn't depend on which form the spec uses.) For each match, read only its first line for the title. Present the matches as a numbered menu showing slug and title, then ask the user to choose. If none match, tell the user.

Read the spec in full. This is your contract.

Also read `CLAUDE.md`, and `AGENTS.md` for project conventions and build/test commands, if it exists.

---

## Running tests and checks (always delegate)

**Never run a test suite, linter, or type-checker inline** (their output is large and noisy). **Every time** you need to run one (the verification command, at baseline, before each commit, in the fix-loop, at finalize), dispatch the `specd-test-runner` agent (`subagent_type: "specd-test-runner"`) with the exact command and repo root.

It returns a compact digest and only runs and reports. **You** judge which failures matter and what to fix. If a digest lacks the detail to debug a specific failure, ask the runner to re-run that one test with more verbosity (e.g. `-vv`), not the whole suite inline.

---

## Pre-flight

1. **Branch**: if on `main`/`master`, create `feature/{slug}`. If on another branch, confirm with user. Never execute on main.

2. **Test baseline**: have the test-runner run the spec's verification command. Record the pass/fail state and the **exact names of any already-failing tests**. If tests already fail, warn the user and treat precisely those tests as the pre-existing-failure set: excluded from the must-pass set, while every other test must pass and none may regress. Don't expand this set later to excuse a failure you introduced.

3. **Validate the spec**: dispatch the `specd-reference-linter` agent (`subagent_type: "specd-reference-linter"`) with the spec path. It verifies the files, symbols, named tests, and dependencies the spec references still exist in the *current* repo (the spec may have drifted since it was authored). On any MISSING or MISLOCATED reference, stop and report before implementing: a spec pointing at moved or vanished code is a stale contract. (REVIEW rows are usually new things the spec intends to create.)

4. **Run linters and type checkers** if available (check CLAUDE.md, AGENTS.md), via the test-runner. Record baseline.

---

## Implementation

Read the spec's Approach, Constraints, Edge cases, and Do NOT sections. These are your boundaries.

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

Implement the changes described in the spec. Use the "Current behavior" section to find the starting point. Use "Constraints" and "Edge cases" to guide the implementation. Use "Do NOT" to stay in scope. Follow the "Approach". If you encounter a blocker the approach didn't anticipate, stop and report rather than silently switching to a different approach.

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

If verification fails after five fix attempts, **or you find yourself re-applying a substantially similar fix**, stop and report to the user with details. Five different hypotheses is healthy debugging; repeating the same fix is a stuck agent. The loop signal is repetition, not just the count.

---

## Final Review

**First, re-read the spec's Constraints, Edge cases, and Do NOT sections.** This command runs long (implementation, four reviewers, up to three fix-and-re-review rounds), exactly the session length where context compaction silently drops constraints. Re-anchor on the contract rather than trust a compaction summary to have preserved it.

Then launch four review agents **in parallel** (one message, four Agent calls). Don't self-review; models fail to correct their own errors.

1. **`specd-staff-reviewer`** (`subagent_type: "specd-staff-reviewer"`): security, correctness, performance, reliability.
2. **`specd-code-quality-reviewer`** (`subagent_type: "specd-code-quality-reviewer"`): architectural hallucinations in AI-generated code.
3. **`specd-qa-reviewer`** (`subagent_type: "specd-qa-reviewer"`): test quality, coverage, edge-case handling.
4. **`specd-compliance-reviewer`** (`subagent_type: "specd-compliance-reviewer"`): did we build what the spec said?

Pass all four the same inputs:
- `diff`: the full feature diff (`git diff <base-branch>...HEAD`, where `<base-branch>` is the branch this feature was cut from, usually `main` or `master`)
- `spec_path`: the spec file path

When all four return, merge their findings (deduplicate overlap), then resolve:

- **Staff / QA / code-quality findings**: fix all BLOCKING and SHOULD_FIX. SUGGESTIONS may be deferred or skipped if out of scope; note any you skip and why.
- **Compliance deviations** (NON_COMPLIANT): if the spec is right and the code drifted, fix the code. A deviation may instead be a reasonable amendment (an edge case the spec missed, a constraint that turned out wrong, e.g. spec said "retry 3 times" but exponential backoff with 5 retries is better). **You may *propose* an amendment; you may not unilaterally decide one and stamp yourself compliant.** Quietly rewriting the contract to match the code is how non-compliance gets laundered into compliance. So: list every proposed amendment under **Needs attention** in the summary (not just "resolved deviations"), and if the spec was modified during execution, get explicit user confirmation before flipping `Status` to `Implemented`. Do not finalize while uncorrected non-compliance remains.

After fixing, re-run each reviewer whose findings you addressed (or whose scope your fixes touched) until staff, code-quality, and QA return APPROVE and compliance returns COMPLIANT. If BLOCKING findings remain after three rounds, stop and report the open findings rather than looping further.

---

## Finalize

After verification passes:

1. Run the full test suite (from CLAUDE.md's operational commands) via the test-runner to check for regressions beyond the spec's verification scope. Fix any regressions before finalizing.

2. Update the spec's "Last updated" date if implementation revealed new constraints or edge cases worth recording (or if the compliance review prompted spec amendments).

3. Flip the spec's `Status` from `Waiting Implementation` to `Implemented` — both in the spec file's header and in its row in the Spec Index (`docs/specs/spec.md`). Also refresh that row's `Updated` column to today's date (matching the spec file's "Last updated"). If the spec lives under `docs/specs/bugs/`, update the Bugs table; otherwise update the Features table. **If the spec was amended during execution, do not flip to `Implemented` without explicit user confirmation** — present the amendments first (step 4) and wait.

4. Present a summary:
   - **Branch**: name and commit count
   - **What was done**: 2-3 sentences
   - **Verification**: pass/fail status, and the pre-existing-failure set excluded at baseline
   - **Final review findings**: issues caught and fixed by the staff, code-quality, and QA reviews
   - **Tests touched**: every test file modified, deleted, or skipped, each with its spec justification (or "none")
   - **Compliance review**: COMPLIANT, or list of resolved deviations
   - **Needs attention** (if any): every spec amendment proposed or made during execution, plus anything unexpected or that the user should review

**Do NOT push or create a PR.** The user handles this.
