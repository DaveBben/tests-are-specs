---
name: building-from-plans
version: "1.0.0"
description: "Use when the user wants to implement or build from an existing plan or failing tests: 'build this plan', 'implement the plan at that path', 'make these failing tests pass', 'start building X from the plan', 'wire up the stubs', or handing off from `scoping`. Implements a scoped change in thin slices on an isolated branch, wiring each failing stub into a real assertion that checks the outcome its description pins, never weakening it, and proving each slice against the real feature before the next. Commits with conventional-commit messages, then suggests running `verifying-work`; kicks a wrong stub back to scoping. Not for scoping the change (use `scoping`) or reviewing the finished diff (use `verifying-work`)."
license: MIT
compatibility: any-agent
metadata:
  effort: build in verified slices; prove each before the next
  namespaced-as: "tests-are-specs:building-from-plans"
---

# Building from plans

You implement the change `scoping` scoped, which left a **frozen contract of failing stubs**: each a named test whose description pins the expected outcome, with a body that asserts false. Wire each stub into a real assertion that checks exactly that outcome, never changing what the description pins, then build until it passes, slice by slice, proving each against real behavior before the next. A short intent in the plan file (`<plan_dir>/<slug>/plan.md`, default `.tests-are-specs/plans/<slug>/plan.md`) points to that contract; read it first.

**Input:** a plan file whose Verification section lists the failing test stubs to wire and pass. A trivial change may arrive straight from a ticket with no plan; then work from the change request and write the failing check yourself (see the bug-fix protocol).

## Stance

- Build to the intent. Don't add scope nobody asked for; don't quietly drop a requirement. If the change needs to grow, or the intent is wrong, impossible, or missing something load-bearing, stop and raise it; never silently reinterpret the ask.
- The **contract's expected outcomes are frozen**: `scoping` wrote it as failing stubs, with the human. Wire each stub into a real assertion that checks exactly the outcome its description pins and nothing weaker; never change, skip, or delete that outcome. If a stub is wrong, impossible, or fighting a house rule, that's not a code fix: stop and kick it back to `scoping`. You may add finer-grained tests of your own, but the contract's outcomes are not yours to change.
- Uphold the repo's house rules (`CLAUDE.md` / `AGENTS.md` / a standards doc) as firmly as the intent; can't satisfy both, stop and raise it. Mirror the codebase's existing patterns and test tooling; impose no new framework.
- You don't review your own build. "Implemented" is a claim; the behavior you drove *this session* is the proof.
- Triage is provisional: if this came straight to build as a trivial change and you find it crosses a seam, a trust boundary, a data shape, or an external contract, stop and scope it. The just-build-it lane is only for changes that stay cheap once you see them.

## 1. Isolate the workspace

- Build on an **isolated branch cut from a clean baseline**, never the live mainline, and name it for the change. One change per branch; never stack a second change on the first's branch.
- Read `task_list`: check `.tests-are-specs/config.json` first (`cat .tests-are-specs/config.json`, or your file tool). If the file or key is missing, fall back to `CLAUDE.md` / `AGENTS.md`; otherwise default to `.tests-are-specs/task-list.md`. Write the thin-slice checklist there and never commit it: the default location is gitignored, so it stays on disk for a dead session or a fresh-context read without ever entering git or reaching the mainline. It is branch-local and ephemeral, never persistent or global agent memory.
- Any *other* uncommitted changes that aren't yours: stop and ask; don't build on someone's half-done edit.

## 2. Slice the change

Cut the work into thin vertical slices, the smallest change each that produces observable behavior, grouped by the seams the change touches; a single-seam change is one slice. Let any ordering the intent implies (a migration before its read path, a type before its callers) pin which slice comes first. Track one line per slice with status (`todo` / `done`) in the task list; after a killed session, resume at the first `todo`.

## 3. Build each slice

Map the slice to the contract stubs it must turn green; they already exist and are already failing. For each, wire it into a real assertion that checks exactly the outcome its description pins, then build the behavior until that assertion passes. The outcome is fixed by `scoping`: never loosen it, and watch each stub go from red to green because the behavior arrived, not because the assertion checks less than its description named.

You may add finer-grained tests of your own as you build (a unit test below a contract test); any test you add must hold the same five properties as a contract test:

- **Observable behavior, as an outcome:** "expired link → 400", not "function X returns Y". Assert at the boundary, not an internal step.
- **Written before the code:** watch it fail first, for the right reason (behavior absent, not a broken test).
- **One observable behavior per slice.**
- **Executed:** automated where there's a test surface; a written manual script a human actually runs where there isn't. Never prose nobody runs.
- **Able to fail** if the behavior regressed.

Use the repo's existing test tooling. The frozen-contract rule, the real-boundary rule, and the faked-done anti-patterns to refuse are in [`references/honest-tests.md`](references/honest-tests.md); load it before you touch the contract. Stay inside scope; build nothing on the out-of-scope list.

## 4. Prove every slice against real behavior

After every slice, drive the real feature and observe the outcome, including an abuse case where the criteria named one. A green contract only means the assertions hold; a passing suite never substitutes for driving the real thing.

> If your harness can launch a subagent, dispatch one to drive the feature and report what it observed; otherwise drive it yourself, in this session or a fresh one. Either way: run it, observe the outcome, and don't just trust the green test.

A green slice carries forward; a stack of unproven ones does not.

## Bug-fix protocol

A bug is not a story: reproduce it with **one failing check** that captures the wrong behavior, fix the code, and keep that check as a regression guard. On the just-build-it lane you write that failing check yourself, since no `scoping` contract exists; on a scoped change the contract already came from `scoping`. No slice fan-out either way: a one-line bug is a one-line fix plus its regression check.

## 5. Finish and hand off

Once every slice is green and proven, commit the code with a **conventional-commit** message (`type(scope): summary`, for example `feat(auth): single-use reset tokens`). The contract tests are part of the diff, wired to real assertions that match the outcomes `scoping` pinned. Leave the task list and the plan file on disk until `verifying-work` has run.

- **You don't certify your own build.** Suggest the human run the `verifying-work` skill next: the independent fresh-context review of the diff against the plan.
- **Merging is the human's call**, the same as any approval; never merge to the mainline on your own read.
- **At merge, keep the code, the tests, and the decision-log receipt. The plan file and the task list are gitignored per-change scratch: delete them from disk.**

## What you do NOT do

- No scope creep, no silent reinterpretation. If the change grows or the intent is wrong, raise it.
- No reviewing your own build; you're the wrong one to certify it.
- No spec artifact with a lifecycle. The task list is scaffolding; it dies at merge.

## Next step

Every slice is green and committed. Suggest the human run the `verifying-work` skill on the diff and the plan before merge; that is the independent review. Merge is the human's.
