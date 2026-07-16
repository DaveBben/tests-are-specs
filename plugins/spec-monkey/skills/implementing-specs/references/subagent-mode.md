# Subagent-orchestrated build (opt-in)

The single-agent workflow in `SKILL.md` is the default and works in any harness. This mode is an option for harnesses that dispatch subagents, on specs large enough to earn it (three or more FR-groups). It never replaces the default; remove this file and the skill still reads complete.

"Dispatch a subagent" here is an action, never a tool name: spawn a fresh agent with an isolated context, hand it a brief, read its result back. Which tool that is — and which agent type to pass — is your harness's business; the per-harness mapping lives outside the skills, in the spec-monkey repository's `docs/harness-tools/`. If your harness has no such tool, this whole mode is unavailable: run the single-agent workflow in `SKILL.md` instead, and never fabricate a dispatch call.

**The three dispatch prompts ship ready to use.** You don't re-derive them per build; you fill the bracketed slots and dispatch:

- [`implementer-prompt.md`](implementer-prompt.md) — builds one FR-group against `contract.md`.
- [`reviewer-prompt.md`](reviewer-prompt.md) — the three-verdict per-group gate (compliance, quality, invariants).
- [`fixer-prompt.md`](fixer-prompt.md) — resolves a failed verdict in code, never in the check.

The sections below explain the loop those prompts run in. Read them once; then work from the prompt files.

## Why files, not pasted text

Everything you paste into a dispatch prompt, and everything a subagent prints back, stays resident in the controller's context and is re-read on every later turn. Hand artifacts over as files so bulk content never enters the controller's context. spec-monkey has an advantage here: `detail/contract.md` is already the durable brief, and its *Requirements & success criteria* is already grouped by subsystem/seam. No task-extraction step is needed; the brief is the contract path plus the group name.

## The unit of work: one FR-group

The spec's *Requirements & success criteria* groups FRs by `### <subsystem / seam>`, each block carrying a *Behavior* and its FR/SC list. That block is one task. *When it happens* sets the order. Build groups in that order. Dispatch two implementers in parallel only when the groups touch disjoint files and neither depends on the other; never parallel-dispatch conflicting implementers.

## The workspace

`.spec-monkey/` at the repo root, self-ignoring (write `*` to `.spec-monkey/.gitignore`). It holds the ledger, the per-group reports, and the review diffs. All of it is recoverable from `git log` if it is lost.

## The loop, per group

1. Record the base commit before dispatch (never `HEAD~1`, which drops all but the last commit of a multi-commit group).
2. Dispatch the implementer subagent.
3. Build the review package.
4. Dispatch the reviewer; get its three verdicts.
5. For any failed verdict, dispatch a fixer; rebuild the package; re-review. Repeat until clean.
6. Append the group's line to the ledger.
7. Move to the next group. No human check-in between groups unless one is blocked.

## The implementer dispatch

Use [`implementer-prompt.md`](implementer-prompt.md); it is the five-part brief below, filled in. Hand the subagent that and nothing else:
- Where it fits (the group name and its place in the order).
- The `contract.md` path and the group name, with "use the exact FR/SC values verbatim from the contract."
- The project-spec path and the `INV-NNN` the group's code path must uphold.
- The interfaces produced by earlier groups it consumes.
- The report-file path and the report contract.

Never paste the FR/SC text; point at `contract.md`. The implementer builds the HOW from the contract and the real code, the same stance as the single-agent path. It writes its full report to `.spec-monkey/report-<group-slug>.md` and returns only status, commits, a one-line test summary, and concerns. Statuses: DONE, DONE_WITH_CONCERNS, BLOCKED, NEEDS_AMENDMENT (a shared fact is missing → route to `grounding-specs`).

## The review package

`.spec-monkey/review-<base7>..<head7>.diff`, built with plain git:
- `git log --oneline BASE..HEAD`
- `git diff --stat BASE..HEAD`
- `git diff -U10 BASE..HEAD`
redirected into the file. Use the base recorded before dispatch. No script required.

## The reviewer dispatch: three verdicts

Use [`reviewer-prompt.md`](reviewer-prompt.md). The reviewer reads the group's diff package once and returns three verdicts, scoped to the group:
1. **Spec compliance**: every FR in the group traces to code that satisfies it; nothing extra, nothing misunderstood.
2. **Code quality**: clean, honest tests, no vacuous assertions or over-mocking.
3. **Invariants**: every cited `INV-NNN` the group's code path touches still holds.

This applies checks 1, 3, and 9 of [`../../auditing-specs/references/audit-rubric.md`](../../auditing-specs/references/audit-rubric.md) to one group's diff; cite them by reference, do not restate them. Treat the implementer's report as unverified claims; a stated rationale never downgrades a finding. Do not paste the diff into the prompt, do not tell the reviewer what not to flag, do not pre-rate severity.

## The fix loop

Use [`fixer-prompt.md`](fixer-prompt.md). The fixer carries the implementer's contract and the failed verdict. It fixes the code, never the check. A finding that conflicts with the contract is the human's call, not the fixer's: reclassify to `amend-spec` and stop.

## The ledger

`.spec-monkey/progress.md`, keyed to FR-group and status:

```
# Build: docs/specs/rss-reader
Feed ingestion (FR-001..FR-003): complete, commits a1b2c3d..e4f5f6a, gate clean, INV-002 upheld
Read tracking (FR-004..FR-005): in progress
API surface (FR-006..FR-007): pending
```

At start, read the ledger; a group marked complete is done, so resume at the first incomplete group. Append its line when a gate comes back clean. After compaction, trust the ledger and `git log` over memory. If `git clean -fdx` destroyed the workspace, rebuild the ledger from `git log`.

## Model selection

Two rules: use the least powerful model that can do each role, and always specify it explicitly (an omitted model inherits the session's, usually the most expensive).

- **Implementer**: scale to the group. A single-seam group with a tight FR/SC takes a fast mid-tier; a multi-seam group with integration concerns takes standard; design judgment against tangled code takes the most capable.
- **Reviewer**: mid-tier floor (three verdicts are judgment); scale up for a subtle invariant (concurrency, a trust boundary).
- **Fixer**: the implementer's tier, one step up if the fix needs more reasoning.
- **Final self-review**: the most capable available; cross-group integration is the hardest call in the build.

spec-monkey specs never contain code (they are WHAT/WHEN, never HOW), so a build is never pure transcription. Mid-tier is the effective floor for implementers, not the cheapest tier. Turn count beats token price: a too-cheap model takes 2-3× the turns and costs more overall.

## The final pass, and where auditing-specs takes over

After the last group, run `SKILL.md` steps 4 and 5 once over the whole build: run the spec's *Verification approach & commands* end-to-end (the worked case must produce its exact values), confirm every cited `INV-NNN` holds across the assembled groups, and review the full diff for integration gaps the per-group gates could not see. This may be one reviewer subagent over the whole-branch package. This is the builder checking its own work.

`auditing-specs` stays a separate skill, run afterward by a fresh agent that trusts nothing it has not checked. Its independence is the point. This mode never inlines the nine-check rubric and never emits a COMPLIANT verdict. Build here; accept there.

## What not to do

- Don't put file paths or code into the spec to make it "dispatchable." The spec stays WHAT/WHEN; `contract.md` is already the durable brief. This is the sharpest line between spec-monkey and a plan-with-code-in-it; do not cross it.
- Don't require subagents, a hook, or context forking anywhere the default path can reach.
- Don't paste FR/SC text into dispatch prompts; point at `contract.md` by path.
- Don't skip the third verdict; the invariant check is why a generic port isn't enough for spec-monkey.
- Don't duplicate the audit rubric or emit a compliance verdict; `auditing-specs` stays the independent gate.
- Don't pre-judge reviewer findings or tell a reviewer what not to flag.
- Don't ship bash scripts as a hard dependency; the git one-liners live inline above.
