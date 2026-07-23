---
name: building-from-plans
version: "1.1.0"
description: "Use when the user wants to implement or build from an existing plan or contract tests: 'build this plan', 'implement the plan at that path', 'make these failing tests pass', 'start building X from the plan', 'wire up the stubs', or handing off from `scoping`. Implements a scoped change as turn-efficient tasks on an isolated branch, removing each contract test's expected-failure marker and building until it passes, never editing its body, refactoring on green, and proving each task against the real feature before the next. Dispatches fresh subagents per task where the harness allows. Commits with conventional-commit messages, then offers to dispatch `verifying-work` in a fresh subagent or hand it to the user; kicks a wrong contract test back to scoping. Not for scoping the change (use `scoping`) or reviewing the finished diff (use `verifying-work`)."
license: MIT
compatibility: any-agent
metadata:
  effort: build in verified turn-efficient tasks; prove each before the next
  namespaced-as: "tests-are-specs:building-from-plans"
---

# Building from plans

You implement the change `scoping` scoped, which left a **frozen contract**: complete tests marked expected-failure, each a full assertion on an independently derived outcome. Task by task, remove each test's marker, build until it passes, refactor on green, and prove the task against real behavior before the next.

**Input:** a plan file (`docs/plans/.build-intents/<slug>/plan.md`, unless the user names another location) whose Verification section lists the contract tests to pass; read it first. A trivial change may arrive straight from a ticket with no plan; then work from the change request and write the failing check yourself (see the bug-fix protocol).

## Stance

- Build to the intent. Don't add scope nobody asked for; don't quietly drop a requirement. If the change needs to grow, or the intent is wrong, impossible, or missing something load-bearing, stop and raise it; never silently reinterpret the ask.
- The **contract is frozen at the body**. Your only edit to a contract test is removing its expected-failure marker; never change an input, an assertion, or an expected value, and never skip or delete one. A fallback stub the plan flags is the one case you wire an assertion, and it must check exactly the outcome its description pins. If a contract test is wrong, impossible, or fighting a house rule, that's not a code fix: stop and kick it back to `scoping`.
- Uphold the repo's house rules (`CLAUDE.md` / `AGENTS.md` / a standards doc) as firmly as the intent; can't satisfy both, stop and raise it. Mirror the codebase's existing patterns and test tooling; impose no new framework.
- You don't review or certify your own build. "Implemented" is a claim; the behavior you drove this session is the proof, and the independent review comes from `verifying-work`.
- Triage is provisional: if a change that came straight to build crosses a seam, a trust boundary, a data shape, or an external contract, stop and scope it.

## 1. Isolate the workspace

- Build on an **isolated branch cut from a clean baseline**, never the live mainline, named for the change. One change per branch.
- Write the task list to `task-list.md` next to the plan file; never commit it. It is branch-local scaffolding, kept on disk for a dead session or a fresh-context read.
- Any other uncommitted changes that aren't yours: stop and ask.

## 2. Decompose the change

Decompose the work into tasks in the task list, one task per dispatch, each written so its implementer finishes in a handful of turns. Group by the contract tests each task turns green; a trivial change is one task. Let any ordering the intent implies (a migration before its read path, a type before its callers) pin what comes first.

- **Self-contained.** The task names the files it touches, the contract tests it must turn green, and the spec detail it needs, so the implementer builds from its first turn instead of exploring or asking. When the plan text contains the code, paste it into the task.
- **Batched.** Group related edits into one task so they land in one round of parallel tool calls; never one task per file. Tell the implementer to chain shell commands when later steps need no reading of earlier output.
- **Ordered only by real dependency.** Independent tasks carry no ordering.
- **Model tier assigned now.** Give each task a tier from the Dispatch section, so dispatch is mechanical.

One line per task with the files, tests, tier, and status (`todo` / `done`); after a killed session, resume at the first `todo`.

## Dispatch: fresh subagents per task

If your harness can launch subagents, run each task in a fresh implementer subagent. Its context is the task entry (contract tests, files, spec detail) plus the house rules; it never inherits your session history. After each task, dispatch a reviewer subagent on that task's diff: spec compliance and code quality.

If your harness can also choose models, name the task's assigned tier explicitly on every dispatch; an omitted model inherits your session's, usually the most capable and most expensive. Pick the least powerful model that handles the role, but count turns, not token price: the cheapest models take 2 to 3 times the turns on multi-step work and cost more overall.

- Plan text contains the complete code, or a single-file mechanical fix: cheapest tier.
- 1 to 2 files with a complete spec: cheap tier.
- Multi-file integration, debugging, or building from prose: mid tier.
- Design judgment or broad codebase understanding: most capable tier.
- Reviewers: scale to the diff's size, complexity, and risk, mid tier as the floor. The whole-branch review at the end is `verifying-work`, run fresh on the most capable tier (see Next step).

No subagents in your harness: build and review each task yourself; the fresh-context review still comes from `verifying-work`.

## 3. Build each task

Load [`references/honest-tests.md`](references/honest-tests.md) before you touch the contract; it holds the frozen-contract rule, the real-boundary rule, the five properties of an honest check, and the faked-done anti-patterns to refuse.

The task lists the contract tests it must turn green. Remove each one's marker and run it: it should fail because the behavior is absent. If it errors instead (a missing import, a seam that doesn't exist), the contract was written against a boundary that doesn't hold; kick it back to `scoping`. Build until the test passes. An unexpected pass on a still-marked test means the behavior arrived early; remove that marker now.

Once green, **refactor with the suite as the net**: tidy names, remove duplication, simplify, keep every test green. You may add finer-grained tests below the contract; they must hold the five properties. Stay inside scope; build nothing on the out-of-scope list.

## 4. Prove every task against real behavior

After every task, drive the real feature and observe the outcome, including an abuse case where the criteria named one; a passing suite never substitutes for driving the real thing. Dispatch a subagent to drive it and report what it observed, or drive it yourself. A green task carries forward; a stack of unproven ones does not.

## Bug-fix protocol

Reproduce the bug with **one failing check** that captures the wrong behavior, fix the code, and keep the check as a regression guard. No task fan-out: a one-line bug is a one-line fix plus its regression check. On the just-build-it lane you write that check yourself; on a scoped change it already exists in the contract.

## 5. Finish and hand off

Once every task is green and proven, commit with a **conventional-commit** message (`type(scope): summary`, for example `feat(auth): single-use reset tokens`). The contract tests are part of the diff, bodies untouched, markers gone. Leave the task list and plan file on disk until `verifying-work` has run; after it passes, delete both in a final chore commit (`chore(<slug>): remove build intent`). Git history keeps the plan; the code, the tests, and the ADR receipt stay. Merging is the human's call.

## Next step

Every task is green and committed; the whole-branch review comes from `verifying-work`, never from you. If your harness can launch subagents, ask the user to pick one:

1. **Launch a subagent to verify.** Dispatch `verifying-work` in a fresh subagent on the most capable available model, given only the plan's slug and the diff range, never your account of the build. Report its verdict back.
2. **I'll verify myself.** Tell the user: clear this context (or start a fresh session) and run `verifying-work` with the plan's slug.

No subagents in your harness: option 2 is the path. Either way the reviewer starts fresh; a reviewer that watched the build, or read your summary of it, inherits its blind spots. Merge is the human's.
