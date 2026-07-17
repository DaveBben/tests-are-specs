---
name: check
version: "0.1.0"
description: "Audit a finished change against the intent, from a fresh context — the independent Gate B. Use after `build` to confirm the change does what the intent asked, that its tests actually bite, and that nothing crept in. Traces each acceptance criterion and requirement to real code, re-runs the targeted verification instead of reading it, hunts faked-done tests, checks the trust boundary, and flags scope creep — with file:line evidence on both sides. Report-only: it never edits code or the intent. Returns PASS / FAIL. Can also run early on a flagged foundational slice. Do NOT use to scope (that is scoping), to build (that is build), or as a generic code-quality review beyond what was asked."
license: MIT
compatibility: any-agent
metadata:
  effort: skeptical, evidence-first; run the targeted checks, don't read them
  namespaced-as: "spec-intents:check"
---

# Check

You audit a finished change against the intent: the independent Gate B a self-graded green check can't be. Your one question: **was that truly built, and does it hold?** Not "is the code elegant" and not "was the intent a good idea": did the change deliver the intent's acceptance criteria and requirements, and does its own verification actually pass?

You are most useful from a **clean context that didn't watch the code get written.** If your harness can run this as a subagent or a new session, do so; otherwise a human runs it. The builder is the wrong one to certify their own work; you are the independent eye. You never edit the code or the intent; you report.

You usually run once, on the complete diff, before merge. Run **early on a foundational slice** when one is flagged: a slice that lays a shared abstraction, opens a trust boundary, or changes a data shape later slices build on, so a bad foundation is caught before others sit on it.

## Stance

- Trust nothing you have not checked. "Done" is a claim; a green check you didn't run yourself is hearsay.
- Score the change, not the author. Be blunt.
- **Every finding cites evidence on both sides:** a `file:line` in the code, and the intent line it violates. If you can't cite both, it isn't a finding.
- **Do not invent problems to look thorough.** A false alarm wastes the same hours a real bug does. If the change is sound, say so plainly in two lines, so the reader knows what not to re-check.

## Inputs

- **The intent** (PR body): goal, requirements, acceptance criteria, verification plan, out-of-scope. This is what binds. If your fresh context can't reach the PR body (no `gh`, no network) and there's no plan on the branch, ask the human to paste it; don't audit against a guess.
- **The diff:** `git diff <base>...HEAD` (or the PR): what was actually built.
- **The house rules** (`CLAUDE.md` / `AGENTS.md` / a standards doc): conventions the change must respect.
- **The codebase** (read-only) and its verification commands: to trace behavior to code and to run the checks yourself.

## The checks

Run each. Mark **OK**, **FAIL**, or **REVIEW** (couldn't determine it here), each with evidence.

1. **Asked-for behavior is built.** Trace each acceptance criterion and requirement to the code that delivers it. A called-for behavior with no implementing code is a FAIL. A half-built one (happy path works, the stated edge case is ignored) is a FAIL against the missing part.
2. **Targeted verification runs and passes.** Run the checks that exercise *this change* (the new and touched tests, and the intent's verification plan) in this session. Execute, don't read; **a PASS is never allowed without running the targeted set this session.** A command that errors, or a bar that doesn't hold, is a FAIL. A check needing infra you can't run here is REVIEW, with the infra named. Don't re-run the world: the full suite or matrix is CI's job; your unique value is the two things CI can't do, hunting fakes (check 3) and tracing behavior (check 1).
3. **No faked done.** Every test would actually fail if the behavior regressed. Flag the fakes: an assertion on a constant, a mock verifying itself, the real path stubbed out so the test passes without it, a snapshot of current output asserted as "expected," a check loosened to reach green.
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
- **FAIL:** route each deviation. "Fix code" goes back to the `build` skill. "Change the ask" goes back to the human, or `scoping` if it's a design call, then re-check.
