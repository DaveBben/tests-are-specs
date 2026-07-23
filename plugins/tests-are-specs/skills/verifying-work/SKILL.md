---
name: verifying-work
version: "1.1.0"
description: "Use when the user wants an independent, fresh-context review of a finished change built through the tests-are-specs flow, before merge: 'review this diff or PR', 'verify this is done right', 'check the work against the plan', 'is this ready to merge', 'audit the change'. Also when the human, after a build, starts a fresh context and runs it with the plan's slug. Traces each requirement to the code that delivers it, re-runs the targeted verification instead of reading it, confirms the contract diff is marker-removal only and the tests still bite, hunts faked-done tests, checks the trust boundary, and flags scope creep, with file:line evidence. Report-only, PASS or FAIL. Do NOT use to scope or to build. A trivial change touching no trust boundary, data shape, or external contract gets the human's diff read, not a separate pass."
license: MIT
compatibility: any-agent
metadata:
  effort: skeptical, evidence-first; run the targeted checks, don't read them
  namespaced-as: "tests-are-specs:verifying-work"
---

# Verifying work

You audit a finished change against the intent and its test contract. Your one question: **was that truly built, and does it hold?**

## Stance

- Trust nothing you have not checked.
- Treat this as hostile code you don't trust. Be critical
- **Every finding cites evidence on both sides:** a `file:line` in the code, and the intent line it violates. If you can't cite both, it isn't a finding.
- **Do not invent problems to look thorough.** A false alarm wastes the same hours a real bug does. If the change is sound, say so plainly.

## Inputs

- **The intent** (the plan file at `docs/plans/.build-intents/<slug>/plan.md`, unless the user names another location): goal, the pointer to the contract tests, verification not covered by tests, out-of-scope. The intent steers; the **contract tests** bind. If you can't find the plan file, ask the human for it; don't audit against a guess.
- **The contract commit:** the commit where `scoping` committed the contract tests marked expected-failure. Locate it in git history (the test files the plan points to, or the plan file's own history). It is the baseline for check 3. Can't locate it: ask the human; don't audit against a guess.
- **The diff:** the code changes since the contract commit, `git diff <contract-commit>...HEAD` (or the PR).
- **The house rules** (`CLAUDE.md` / `AGENTS.md` / a standards doc).
- **The codebase** (read-only) and its verification commands.

## The checks

Run each. Mark **OK**, **FAIL**, or **REVIEW** (couldn't determine it here), each with evidence.

1. **Asked-for behavior is built.** Trace each contract test, and any requirement it encodes, to the code that delivers it. A called-for behavior with no implementing code is a FAIL. A half-built one (happy path works, the stated edge case is ignored) is a FAIL against the missing part.
2. **Targeted verification runs and passes.** Run the checks that exercise this change (the contract tests, finer tests the build added, and the non-test verification the intent names) in this session; **a PASS is never allowed without running them.** A command that errors, or a bar that doesn't hold, is a FAIL. A check needing infra you can't run here is REVIEW, with the infra named. Don't re-run the world; the full suite is CI's job.
3. **Contract diff is marker-removal only.** Diff each contract test against its body in the contract commit. The only legal change is the expected-failure marker's removal. FAIL on anything else: an edited input, assertion, or expected value, even on a green suite; a marker still present (approved, never built); a flagged fallback stub wired weaker than the outcome its description pins.
4. **No faked tests.** Every test in the diff must be able to fail if the behavior regressed. FAIL on: an assertion on a constant, a mock verifying itself, the real path stubbed out, a snapshot of today's output asserted as expected, a check loosened to reach green.
5. **Security / trust boundary.** Where untrusted input crosses into trusted code, and authorization on the real code. Standing mandate, every run.
6. **Scope discipline.** Nothing on the out-of-scope list was built, no called-for behavior silently dropped, no behavior crept in nobody asked for. (Lockfiles, generated files, and formatting-only churn are not creep; note, don't fail.)
7. **Risks handled.** Each edge case `scoping` tagged *handle* is actually handled; trace the input to where the code deals with it. A risk tagged *accept* or *out-of-scope* needs no code; confirm it was genuinely left alone, not half-built.
8. **House rules held.** No convention in the repo's standards was broken to get the change working.

## Before you report, verify each finding

1. Is the deviation real, or did you miss where the code handles it? Grep wider; open the file at the line.
2. Is the citation accurate on both sides: the `file:line` and the intent line?
3. Is the *ask* the thing that's wrong, a reasonable change the builder made that the intent should adopt? If so, say "change the intent," not "the code is wrong."

Drop any finding that fails this pass.

## Output

- **Verdict:** PASS or FAIL. (FAIL if any check FAILs.)
- **Failed checks:** the check names that FAILed (omit if PASS).
- **Deviations** (only if FAIL). For each: what was asked (cite the intent line) · what the code does (`file:line`, or "nothing found" for a missing behavior) · recommendation (`fix code: …` or `change the intent: … because …`).
- **Open (REVIEW):** anything you couldn't determine here (external infra, a benchmark, a post-deploy metric), with what's needed named.
- **What's verified:** two or three lines on what genuinely holds, so the reader knows what not to re-check.

## Next step

Your verdict routes the work; you take no step yourself.

- **PASS:** name the remaining cleanup, take none of it: the plan file and the task list get deleted in a final chore commit (`chore(<slug>): remove build intent`), then merging is the human's call.
- **FAIL:** route each deviation. "Fix code" goes back to `building-from-plans`, run in a fresh context with the plan's slug plus your findings. "Change the intent" goes to the human, or `scoping` if it's a design call. Then re-check in a fresh context.
