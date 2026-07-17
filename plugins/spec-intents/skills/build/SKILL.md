---
name: build
version: "0.1.0"
description: "Implement a scoped change in thin slices, proving each slice before the next. Use after `scoping` has written the intent — goal, requirements, acceptance criteria, verification plan, out-of-scope — to the PR body; build the checks from those criteria, never invent new ones. Each check states an observable outcome, is written before the code, and covers one behavior per slice; after every slice you drive the real feature and observe it, not just a green test. Works on an isolated branch, tracks slices in an ephemeral task list that dies at merge, and hands the diff to `check` and the merge decision to the human. Do NOT use to scope a change (that is scoping) or to review the finished diff (that is check)."
license: MIT
compatibility: any-agent
metadata:
  effort: build in verified slices; prove each before the next
  namespaced-as: "spec-intents:build"
---

# Build

You implement the change `scoping` scoped. The intent lives in the PR body: goal, requirements, acceptance criteria, verification plan, out-of-scope. You build to it slice by slice, proving each slice against real behavior before the next. "Done" means built and proven, not built and asserted. The code and its tests are the source of truth you leave behind.

## Stance

- Build to the intent. Don't add scope nobody asked for; don't quietly drop a requirement. If the change needs to grow, or the intent is wrong, impossible, or missing something load-bearing, stop and raise it; never silently reinterpret the ask.
- Build the checks from the intent's **acceptance criteria and verification plan**. You don't author criteria here; `scoping` did that with the human.
- Uphold the repo's house rules (`CLAUDE.md` / `AGENTS.md` / a standards doc) as firmly as the intent. Can't satisfy both? Stop and raise it. Mirror the codebase's existing patterns and test tooling; impose no new framework.
- You don't review your own build. "Implemented" is a claim; the behavior you drove *this session* is the proof.

## 1. Isolate the workspace

- Build on an **isolated branch cut from a clean baseline**, never the live mainline. Name it for the change. One change per branch; never stack a second change on the first's branch.
- Read `task_list`: check `.spec-intents/config.json` first (run `cat .spec-intents/config.json`, or open it with your file tool). If the file or the key is missing, fall back to `CLAUDE.md` / `AGENTS.md`; otherwise default to `.spec-intents/task-list.md`. Write the thin-slice checklist at that path. The default location is gitignored, so the checklist stays on disk for a dead session or a fresh-context read but never enters git or reaches the mainline. Do not commit it. It is branch-local and ephemeral, never persistent or global agent memory.
- Any *other* uncommitted changes that aren't yours: stop and ask. Don't build on someone's half-done edit.

## 2. Slice the change

Cut the work into thin vertical slices: the smallest change each that produces observable behavior. Group by the seams the change touches; a single-seam change is one slice. Let any ordering the intent implies (a migration before its read path, a type before its callers) pin which slice comes first. Track one line per slice with status (`todo` / `done`) in the task list; after a killed session, resume at the first `todo`.

## 3. Build each slice

For each slice, write the checks that prove it, then implement until they pass. Each check must hold five properties:

- **Observable behavior, as an outcome:** "expired link → 400", not "function X returns Y". Assert at the boundary, not an internal step.
- **Written before the code:** watch it fail first, for the right reason (behavior absent, not a broken test).
- **One observable behavior per slice.**
- **Executed:** automated where there's a test surface; a written manual script a human actually runs where there isn't. Never prose nobody runs.
- **Able to fail** if the behavior regressed.

Use the repo's existing test tooling. The full loop, the real-boundary rule, and the faked-done anti-patterns to refuse are in [`references/honest-tests.md`](references/honest-tests.md); load it before you write the first check. Stay inside scope; build nothing on the out-of-scope list.

## 4. Gate A: prove every slice against real behavior

After every slice, prove it by driving the real feature and observing the outcome: not "tests green", demonstrated behavior, including an abuse case where the criteria named one.

> Prove the slice against real behavior. If your harness can launch a subagent, dispatch one to drive the feature and report what it observed; otherwise drive it yourself in this session (or a fresh one). Either way: run it, observe the outcome, don't just trust the green test.

A green slice carries forward; a stack of unproven ones does not.

## Bug-fix protocol

A bug is not a story. Reproduce it with **one failing check** that captures the wrong behavior, fix the code, and keep that check as a regression guard. No slice fan-out: a one-line bug is a one-line fix plus its regression check.

## 5. Finish and hand off

Once every slice is green and proven, commit the code with a message that says what changed and why. Leave the task list in place on disk until `check` has run.

- **You don't certify your own build.** The independent pass is `check`: a fresh, skeptical review of the whole diff against the intent (Gate B). If your harness can dispatch a subagent, dispatch one running `check` on this diff from a clean context; otherwise hand back and let the human run `check` next.
- **Merging is the human's call**, the same as any approval; never merge to the mainline on your own read.
- **At merge, keep the code, the tests, and the decision-log receipt. The intent dies with the merged PR; the task list is gitignored scratch, so delete it from disk.**

## What you do NOT do

- No scope creep, no silent reinterpretation. If the change grows or the intent is wrong, raise it.
- No reviewing your own build; you're the wrong one to certify it.
- No spec artifact with a lifecycle. The task list is scaffolding; it dies at merge.

## Next step

The build is done but proven only by you. The one follow-on is the `check` skill: a fresh-context Gate B over the diff against the intent. Dispatch a subagent to run it if you can, or hand back to the human. Merge is the human's.
