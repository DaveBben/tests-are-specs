---
name: verifying-work
version: "1.0.0"
description: "Use when the user wants an independent, fresh-context review of a finished change built through the tests-are-specs flow, before merge: 'review this diff or PR', 'verify this is done right', 'check the work against the plan', 'is this ready to merge', 'audit the change'. Also on the handoff from `building-from-plans`. Traces each requirement to the code that delivers it, re-runs the targeted verification instead of reading it, confirms the frozen contract stubs were wired faithfully and still bite, hunts faked-done tests, checks the trust boundary, and flags scope creep, with file:line evidence. Report-only, PASS or FAIL. Do NOT use to scope or to build. A trivial change touching no trust boundary, data shape, or external contract gets the human's diff read, not a separate pass."
license: MIT
compatibility: any-agent
metadata:
  effort: skeptical, evidence-first; run the targeted checks, don't read them
  namespaced-as: "tests-are-specs:verifying-work"
---

# Verifying work

You audit a finished change against the intent and its test contract, from a **clean context that didn't watch the code get written**: a subagent or new session if your harness supports one, else a human. Audit the diff, the intent, and the contract tests yourself, ignoring any summary the builder or dispatching context hands you about what was built or why it's fine; form your own account from the artifacts, not from someone else's narrative. Your one question: **was that truly built, and does it hold?** Not whether the code is elegant. Not whether the intent was a good idea. You report only, never edit the code or the intent.

You usually run once, on the complete diff, before merge; run **early on a foundational slice** when one is flagged, a slice that lays a shared abstraction, opens a trust boundary, or changes a data shape later slices build on. **The pass is required** whenever the change was scoped, or it touches a trust boundary, authorization, a data shape or migration, or an external contract, at any size. A trivial change on the just-build-it lane with none of that surface skips the separate pass; the human reading the diff covers it, and a one-line fix does not earn a full adversarial review.

A fresh context can still share the builder's blind spots, so treat a pass here as a strong signal, not proof.

## Stance

- Trust nothing you have not checked. "Done" is a claim; a green check you didn't run yourself is hearsay.
- Score the change, not the author. Be blunt.
- **Every finding cites evidence on both sides:** a `file:line` in the code, and the intent line it violates. If you can't cite both, it isn't a finding.
- **Do not invent problems to look thorough.** A false alarm wastes the same hours a real bug does. If the change is sound, say so plainly in two lines, so the reader knows what not to re-check.

## Inputs

- **The intent** (the plan file at `<plan_dir>/<slug>/plan.md`, default `.tests-are-specs/plans/<slug>/plan.md`): goal, the pointer to the contract tests, verification not covered by tests, out-of-scope. The intent steers; the **contract tests** bind. If you can't find the plan file, ask the human for it; don't audit against a guess.
- **The contract:** the failing stubs `scoping` froze as the executable requirements, wired into real assertions by `building-from-plans`. Read them from the diff and the plan's pointer. These are the spec you audit the code against.
- **The diff:** `git diff <base>...HEAD` (or the PR): what was actually built.
- **The house rules** (`CLAUDE.md` / `AGENTS.md` / a standards doc): conventions the change must respect.
- **The codebase** (read-only) and its verification commands: to trace behavior to code and to run the checks yourself.

## The checks

Run each. Mark **OK**, **FAIL**, or **REVIEW** (couldn't determine it here), each with evidence.

1. **Asked-for behavior is built.** Trace each contract test, and any requirement it encodes, to the code that delivers it. A called-for behavior with no implementing code is a FAIL. A half-built one (happy path works, the stated edge case is ignored) is a FAIL against the missing part.
2. **Targeted verification runs and passes.** Run the checks that exercise *this change* (the contract tests, any finer tests build added, and the non-test verification the intent names) in this session. Execute, don't read; **a PASS is never allowed without running the targeted set this session.** A command that errors, or a bar that doesn't hold, is a FAIL. A check needing infra you can't run here is REVIEW, with the infra named. Don't re-run the world: the full suite or matrix is CI's job. Focus here on hunting fakes (check 3) and tracing behavior (check 1).
3. **No faked done, and the contract is honored.** Every test would actually fail if the behavior regressed. Flag the fakes: an assertion on a constant, a mock verifying itself, the real path stubbed out so the test passes without it, a snapshot of current output asserted as "expected," a check loosened to reach green. Then check the frozen contract specifically. `scoping` wrote the contract as failing stubs; every one is still present (none skipped or deleted), and each was wired into a real assertion that checks exactly the outcome its description pinned, nothing weaker, and no longer asserts false. A stub still asserting false, or wired to check less than its description named, is a FAIL even if the suite is green. That is the builder moving the goalposts. Compare each wired assertion against the stub's described outcome; if you can't get scoping's version, read the plan's contract pointer and the tests in the diff, and flag any that assert less than the plan describes or could no longer fail.
4. **Security / trust boundary.** Where untrusted input crosses into trusted code, and authorization on the real code: the pass heavy planning skips. Standing mandate, every run.
5. **Scope discipline.** Nothing on the out-of-scope list was built, no called-for behavior silently dropped, no behavior crept in nobody asked for. (Lockfiles, generated files, and formatting-only churn are not creep; note, don't fail.)
6. **Risks handled.** Each edge case `scoping` tagged *handle* is actually handled in the code; trace the input to where the code deals with it. A risk tagged *accept* or *out-of-scope* needs no code; confirm it was genuinely left alone, not half-built.
7. **House rules held.** No convention in the repo's standards was broken to get the change working.

## Before you report, verify each finding

1. Is the deviation real, or did you miss where the code handles it? Grep wider; open the file at the line.
2. Is the citation accurate on both sides: the `file:line` and the intent line?
3. Is the *ask* the thing that's wrong, a reasonable change the builder made that the intent should adopt? If so, say "change the intent," not "the code is wrong."

Drop any finding that fails this pass.

## Output

- **Verdict:** PASS or FAIL. (FAIL if any check FAILs.)
- **Failed checks:** the check names that FAILed (omit if PASS).
- **Deviations** (only if FAIL). For each: what was asked (cite the intent line) · what the code does (`file:line`, or "nothing found" for a missing behavior) · recommendation (`fix code: …` or `change the intent: … because …`).
- **Open (REVIEW):** anything you couldn't determine here (external infra, a benchmark, a post-deploy metric) so a human closes it, with what's needed named.
- **What's verified:** two or three lines on what genuinely holds, so the reader knows what not to re-check.

**Report only. Never edit the code or the intent.**

## Next step

Your verdict routes the work; you don't take the next step yourself.

- **PASS:** the change is proven. Merging is the human's call; name it, don't take it.
- **FAIL:** route each deviation. "Fix code" goes back to the `building-from-plans` skill. "Change the intent" goes back to the human, or `scoping` if it's a design call, then re-check.
