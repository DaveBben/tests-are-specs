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
description: >
  Implements a spec produced by /specd:create-spec. Reads the spec, creates a
  feature branch, implements the changes, self-verifies, then runs
  parallel staff and QA reviews. Does not push or create PRs.
---

# Execute — Implement a Spec

Read the spec. Do the work.

---

## Input

Resolve `$ARGUMENTS` to a spec file:

1. **Full path** (`docs/specs/features/{slug}/spec.md`): use directly
2. **Slug**: try `docs/specs/features/{slug}/spec.md`
3. **No input**: glob `docs/specs/features/*/spec.md` and
   `docs/specs/bugs/*/spec.md`. Read each spec's YAML frontmatter and
   filter to those with `Status: Waiting Implementation`. Present the
   matching specs as a numbered menu showing slug and title, then ask
   the user to choose. If none are waiting, tell the user.

Read the spec in full. This is your contract.

Also read `CLAUDE.md` for project conventions and build/test commands,
if it exists.

---

## Pre-flight

1. **Branch**: if on `main`/`master`, create `feature/{slug}`. If on
   another branch, confirm with user. Never execute on main.

2. **Test baseline**: run the verification command from the spec.
   Record the pass/fail state, including the **exact names of any
   already-failing tests**. If tests already fail, warn the user before
   proceeding, and treat precisely those named tests as the
   pre-existing-failure set. Those are excluded from the must-pass set;
   every other test must pass and no currently-passing test may
   regress. Do not expand this set later to excuse a failure you
   introduced.

3. **Validate the spec**: verify that files listed in "Files that
   matter" exist on disk. If any are missing, stop and report.

4. **Run linters and type checkers** if available (check CLAUDE.md
   for commands). Record baseline. These catch mechanical issues
   for free.

---

## Implementation

Read the spec's Approach, Constraints, Edge cases, and Do NOT
sections. These are your boundaries.

### Principles

- Prefer a little repetition over the wrong abstraction. Do the
  simplest thing that satisfies the spec.
- One logical change per commit. If the spec involves multiple
  concerns, commit each separately.
- **Default to parallelizing independent work.** When the spec's
  concerns touch non-overlapping files, dispatch them as concurrent
  implementation subagents (up to 10; prefer sonnet agents for simple
  file edits) rather than editing sequentially. Only stay
  single-threaded when the changes are genuinely interdependent. Pass
  each subagent these principles, the spec file path, and a targeted
  description of the change it needs to make; each must apply the
  principles in its work. Merge their output and verify the combined
  result **before any commit** — never commit unmerged or unverified
  subagent work.
- **Verify, don't predict.** Every import, package, and API method must
  exist in the version this project pins — check the lockfile or
  installed source before using it.
- **Fail loud.** Catch only the specific exceptions the code can raise;
  never catch base exception classes; never ship a stub that fakes
  success (`return True  # in a real implementation...`). Both hide
  brokenness behind plausible-looking success.
- **Match this codebase.** Before writing anything new, find how this
  project already solves similar problems and follow that pattern;
  consolidate near-duplicates instead of adding parallel
  implementations.
- **Least code that works.** No speculative abstractions, no indirection
  for single callers, stdlib over hand-rolling; delete dead code
  outright — git is the backup.
- **Comments explain why, never what.** If a comment restates the code,
  delete it. Update adjacent comments when behavior changes.
- **Test real behavior.** Realistic inputs through real libraries,
  deterministic sync (no sleeps), fixtures with real-world mess. Never
  modify a test to make it pass — flag it instead.



### Doing the work

Read each file in "Files that matter" before modifying it. Understand
what's there before changing it.

Implement the changes described in the spec. Use the "Current
behavior" section to find the starting point. Use "Constraints" and
"Edge cases" to guide the implementation. Use "Do NOT" to stay in
scope. Follow the "Approach". If you encounter a blocker the
approach didn't anticipate, stop and report rather than silently
switching to a different approach.

If the "Alternatives rejected" section lists an approach, do not
use that approach, it was explicitly rejected during planning.

---

## Before Each Commit

After each logical unit of work, before committing:

1. **Run linters and type checkers.** Fix any new violations.
2. **Run the tests relevant to the change** (at minimum, the scope
   of the spec's verification command). All must pass — never
   commit on a red state you introduced.
3. **Diff the tests.** Run `git diff` (and `git status`) against the
   test directories specifically. For every test file the change
   modified, deleted, or skipped, confirm the change is justified by
   the spec — not a weakened or removed assertion that papers over a
   failure. Record each touched test file and its justification for the
   summary. If a test was changed only to make it pass, revert it and
   fix the code instead.

Then commit with a clear message. Keep commits under 400 changed
lines — review effectiveness drops sharply beyond that threshold.
If a logical change exceeds 400 lines, split it into smaller
commits.

---

## Verification

**You are not done until the spec's verification criteria pass.**

Run the verification command from the spec. Check every assertion:
- All existing tests listed must still pass
- All new behaviors described must be verified
- If any check fails, fix it and re-verify

Run linters and type checkers again. Fix any new violations
introduced by your changes.

Do not commit until verification passes. Do not rely on your own
judgment that the code is correct — run the actual commands.

If verification fails after five fix attempts, **or if you find
yourself re-applying a substantially similar fix**, stop and report the
failure to the user with details. Five genuinely different hypotheses
is healthy debugging; repeating the same fix is a stuck agent — the
loop signal is repetition, not just the count.

---

## Final Review

**First, re-read the spec's Constraints, Edge cases, and Do NOT
sections.** This command runs long — implementation, four reviewers,
and up to three fix-and-re-review rounds — which is exactly the session
length where context compaction silently drops constraints. Re-anchor
on the contract before reviewing, rather than trusting a compaction
summary to have preserved it.

Then launch four review agents **in parallel** — a single message with
four Agent tool calls. Do not self-review — models fail to correct
their own errors.

1. **`specd-staff-reviewer`** (`subagent_type: "specd-staff-reviewer"`) —
   multi-pass review of the code: security, correctness,
   performance, reliability.
2. **`specd-code-quality-reviewer`** (`subagent_type:
   "specd-code-quality-reviewer"`) — architectural hallucinations in
   AI-generated code
3. **`specd-qa-reviewer`** (`subagent_type: "specd-qa-reviewer"`) — test
   quality, test coverage, and edge case handling.
4. **`specd-compliance-reviewer`** (`subagent_type:
   "specd-compliance-reviewer"`) — did we build what the spec said we'd
   build?

Pass all four the same inputs:
- `diff`: the full feature diff (`git diff <base-branch>...HEAD`,
  where `<base-branch>` is the branch this feature was cut from —
  usually `main` or `master`)
- `spec_path`: the spec file path


When all four return, merge their findings (deduplicate any
overlap), then resolve them:

- **Staff / QA / code-quality findings**: fix all BLOCKING and SHOULD_FIX findings.
  SUGGESTIONS can be deferred or skipped if they're out of scope,
  but note any you skip and why.
- **Compliance deviations** (NON_COMPLIANT): for each — if the spec
  is right and the code drifted, fix the code. A deviation may instead
  be a reasonable amendment (an edge case the spec missed, a constraint
  that turned out to be wrong — e.g. the spec said "retry 3 times" but
  exponential backoff with 5 retries is better). **You may *propose* an
  amendment; you may not unilaterally decide one and stamp yourself
  compliant.** The spec is the contract you are judged against — quietly
  rewriting it to match the code is how non-compliance gets laundered
  into compliance. So: never silently absorb an amendment. List every
  proposed amendment under **Needs attention** in the summary (not just
  "resolved deviations"), and if the spec was modified during execution,
  get explicit user confirmation before flipping `Status` to
  `Implemented`. Do not finalize while uncorrected non-compliance
  remains.

After fixing, re-run each reviewer whose findings you addressed (or
whose scope your fixes touched) until staff, code-quality, and QA
all return APPROVE and compliance returns COMPLIANT. If reviewers
still return BLOCKING findings after three review rounds, stop and
report the open findings to the user rather than looping further.

---

## Finalize

After verification passes:

1. Run the full test suite (from CLAUDE.md's operational commands)
   to check for regressions beyond the spec's verification scope.
   Fix any regressions before finalizing.

2. Update the spec's "Last updated" date if implementation revealed
   new constraints or edge cases worth recording (or if the
   compliance review prompted spec amendments).

3. Flip the spec's `Status` from `Waiting Implementation` to
   `Implemented` — both in the spec file's header and in its row
   in the Spec Index (`docs/specs/spec.md`). Also refresh that row's
   `Updated` column to today's date (matching the spec file's "Last
   updated"). If the spec lives under `docs/specs/bugs/`, update the
   Bugs table; otherwise update the Features table. **If the spec was
   amended during execution, do not flip to `Implemented` without
   explicit user confirmation** — present the amendments first (step 4)
   and wait.

4. Present a summary:
   - **Branch**: name and commit count
   - **What was done**: 2-3 sentences
   - **Verification**: pass/fail status, and the pre-existing-failure
     set excluded at baseline
   - **Final review findings**: issues caught and fixed by the
     staff, code-quality, and QA reviews
   - **Tests touched**: every test file modified, deleted, or skipped,
     each with its spec justification (or "none")
   - **Compliance review**: COMPLIANT, or list of resolved
     deviations
   - **Needs attention** (if any): every spec amendment proposed or made
     during execution, plus anything unexpected or that the user should
     review

**Do NOT push or create a PR.** The user handles this.
