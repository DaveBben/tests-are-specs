---
name: implementing-specs
version: "1.11.0"
description: "Implement an engineering spec end-to-end. Build the code that satisfies its requirements and verify it against the spec's own success criteria and commands. Use when the user provides you a spec to implement. Do NOT use to author or review a spec or for a change with no approved spec."
license: MIT
compatibility: any-agent
---

# Implementing Specs

You take an approved spec and build it. The spec says WHAT to do, WHEN, and the high-level approach; the detailed HOW is yours. You work that out from the spec and the real code.

## Stance

- Build what the spec says. Don't add scope it didn't ask for, and don't drop a requirement.
- **Build in slices, prove each before the next.** The contract already groups its FRs by subsystem/seam; those groups are your slices. Build one, verify its success criteria hold, then move to the next in the order *When it happens* sets. A big-bang build that codes every group and tests at the end is how the model loses the thread on a complex change — the sharpest complaint against spec tools is that implementation quality lags the plan, and this is why. Small verified slices are the fix.
- **Use TDD.** Write the failing test first and confirm it fails, then write the code needed to pass. Never write all the tests upfront; take one success criterion at a time. When an SC has no test surface (a manual check, a production metric, a pure config edit), say so and fall back to the spec's verification command; don't fake a test to have one.
- **Author every artifact the contract lists.** Each line under *Artifacts to author* must exist in the diff by the end of the build. A green unit test does not discharge a boundary-crossing artifact the contract also names — author that one too. An artifact tagged NEEDS INFRA is still due now: write the file now, defer only its run. "Can't run it here" is never "don't write it."
- **Uphold the project spec.** If the spec names a `parent`, the project spec's cited `INV-NNN` and shared contracts bind the build as firmly as the spec's own FRs. Never break an invariant to satisfy a local requirement; if you can't have both, stop and raise it.
- If the spec is wrong, impossible, or missing something load-bearing, stop and raise it with the human. Don't silently reinterpret it.
- You are not done until verification passes, every FR and non-functional bound is met, and no cited `INV-NNN` is violated. "Implemented" is a claim; the verification you ran this session is the proof. Don't make the claim without the proof.

## Workflow

Do the work; don't narrate the steps.

1. **Find the spec.** Locate the approved spec folder at `docs/specs/{slug}/` (its `spec.md` `status` reads `approved`). Read `spec.md` and `detail/contract.md` — together the full build contract: the requirements (`FR-NNN`) and their success criteria (`SC-NNN`), *When it happens* (triggers and ordering), the *Data & interface contract*, the scope and *Out of scope* lines, and *Verification approach & commands*. Read `detail/design.md`'s *Approach* too: the high-level shape the spec commits to, your starting point. The rest of `detail/design.md` is review-time reasoning; open it when the contract leaves a decision unclear. If `spec.md` names a `parent`, read the project spec (`docs/specs/project/spec.md`) too: the `INV-NNN` and shared contracts it cites bind this build.

2. **Isolate the workspace and plan the build as slices.** Work the implementation out from the spec, the *Approach*, and the code. Find the seams the change touches: the callers, the types, the tests. Take the FR-groups under *Requirements & success criteria* as your slices, and let *When it happens* order them; a dependency pins which comes first, disjoint groups may run in parallel. Build and prove one slice at a time, not the whole change at once.
   - **Build on an isolated branch, never the live mainline.** From a clean baseline, cut a branch (or a worktree where your setup supports it) named for the slug, so a multi-slice build never lands half-done on `main` and two work items' commits never tangle. The branch/worktree discipline and the finishing decision are in [`references/build-workspace.md`](references/build-workspace.md).
   - **Keep the slice ledger.** On a change of more than one slice, write the slice list to `.spec-monkey/progress.md` at the repo root (self-ignoring: put `*` in `.spec-monkey/.gitignore`), one line per FR-group with its status, and mark each `complete` as its verification passes. After a session dies or context compacts, read it and resume at the first incomplete slice. Fully recoverable from `git log`, so it binds nothing.

3. **Build each slice.** Apply the TDD loop from the Stance to each of the slice's testable success criteria, and implement until every `FR-NNN` in the slice holds. Respect the constraints, the data and interface contracts, and the ordering; stay inside scope and build nothing on the *Out of scope* list; mirror the codebase's existing patterns rather than inventing new ones. Prove the slice before starting the next; carry a green slice forward, not a stack of untested ones. The test-first loop and the faked-done anti-patterns to refuse are in [`references/build-discipline.md`](references/build-discipline.md).

   **When a slice won't go green and you don't understand why, stop.** Don't edit half-understood until the error moves — that shotgun loop is exactly how build quality falls behind the spec. Work [`references/debugging.md`](references/debugging.md): reproduce it, one hypothesis at a time, binary-search the delta to the root cause. If the cause is the contract itself (ambiguous, impossible, or fighting a cited `INV-NNN`), that's an `amend-spec`, not a code fix: raise it, don't reinterpret the spec to force green.

4. **Verify the whole build.** Once every slice is green, confirm every *Artifacts to author* line exists in the diff — a missing one is a gap, not a deferred item, even when tagged NEEDS INFRA. Then run every "runs here" gate from *Verification approach & commands* in this session end to end, and read the output before you trust it. Every success criterion must hold, the worked case must produce the exact values it states, and every cited `INV-NNN` must still hold in the assembled code. A pass you remember from an earlier run, or expect because the code should work, is not one; run it now. A NEEDS-INFRA gate you can't run here is reported authored-but-unrun as an open item — never as absent. When a check fails, fix the code, not the check: loosening an assertion, skipping the case, or relaxing a bound to reach green fakes the result instead of meeting it.

5. **Review the change.** Read your own diff critically against the spec, as a hostile reviewer would: does every requirement trace to a real change, are the edge cases handled, are the tests honest (no vacuous assertions, no over-mocking that leaves the real path untested)? The self-review rubric — the same standard `auditing-specs` applies from a fresh context — is in [`references/build-discipline.md`](references/build-discipline.md). Meet it here and the audit confirms rather than corrects.

6. **Finalize, then name the finish.** Set the spec's `status` to `implemented` only once the checks passed in this session; the status records what you verified, not what you expect to hold. Then commit with a message saying what changed and why, pointing back to the spec. The branch stops here: finishing is the human's gate, the same as approval. Name it — open a PR, merge, or discard the branch/worktree — and hand it over rather than merging to the mainline on your own read. Discard is a fine outcome for a spike that didn't pan out; say so instead of leaving dead commits. See [`references/build-workspace.md`](references/build-workspace.md).

## Optional: subagent-orchestrated build

The workflow above runs in one context — the default, sufficient in any harness. If your harness can dispatch subagents (fresh agents with isolated context you task and read results back from) **and** the spec's *Requirements & success criteria* splits into three or more FR-groups, you may instead run the build as an orchestration: a fresh implementer per FR-group, a review gate after each, a fix loop until clean, and a ledger that survives compaction. It raises quality by giving each group a clean context and its own gate, at the cost of more invocations — so it earns its keep only past two or three groups. Otherwise run the workflow above; never require a subagent.

The mechanics (per-group dispatch, the three-verdict gate — spec compliance, code quality, cited `INV-NNN` — the fix loop, the file handoffs, the `.spec-monkey/progress.md` ledger, and model selection) live in [`references/subagent-mode.md`](references/subagent-mode.md). Read it before you orchestrate.

## What you do NOT do

- No scope creep. If you find the spec needs to change, raise it; don't quietly expand the work. If the build needs a shared fact the project spec lacks (a new invariant, entity, or contract change), that is a project-spec amendment: stop and raise it, don't invent it locally.
- No authoring or reviewing the spec itself.

## Next step

With `status: implemented` and the change committed, the build is done but unproven by a second pass. Next is `auditing-specs`: an independent trace of every requirement to code, with the spec's own verification re-run. Offer it. This is separate from your step-5 review; a fresh context catches what the builder's does not.
