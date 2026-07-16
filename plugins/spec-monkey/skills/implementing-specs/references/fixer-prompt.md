# Fixer dispatch prompt (subagent mode)

Ready-to-use brief for a failed review verdict. Fill the `[BRACKETED]` slots and dispatch. The fixer fixes the **code**, never the check. The prose that governs this loop is in [`subagent-mode.md`](subagent-mode.md).

The one line that makes this role safe: a finding that conflicts with the contract is the human's call, not the fixer's. The fixer reclassifies it to `amend-spec` and stops — it never edits the contract, and it never loosens a test to pass.

"Dispatch a subagent" is an action, not a tool name: use whatever your harness provides for spawning a fresh agent and reading its result back, with a general coding-agent type. The per-harness tool mapping lives outside the skills, in the spec-monkey repository's `docs/harness-tools/`.

```
Dispatch a subagent:
  description: "Fix [GROUP_NAME]: [FAILED_VERDICT]"
  model: [MODEL — REQUIRED: the implementer's tier, one step up if the fix
          needs more reasoning. See subagent-mode.md "Model selection".]
  prompt: |
    You are fixing findings from a failed review verdict on one FR-group. You
    fix the code, never the check. Loosening an assertion, skipping a case, or
    relaxing a bound to reach green fakes the result — do not do it.

    ## Your contract

    Read the group named "[GROUP_NAME]" under *Requirements & success criteria*
    in: [CONTRACT_PATH]. Use the exact FR/SC values from that file. The cited
    invariants your code path must uphold, from [PROJECT_SPEC_PATH]: [INV_LIST].

    ## What failed

    The reviewer returned these findings on [FAILED_VERDICT — e.g. "Verdict 2,
    Code quality"]:

    [FINDINGS — paste the reviewer's Critical/Important findings verbatim, each
    with its file:line]

    ## Where you work

    Work from: [BRANCH_OR_WORKTREE_DIR], the same branch the group was built on.

    ## How to fix

    1. Address each finding at its file:line. Fix the code so the finding no
       longer holds — do not edit the test to hide it, and do not weaken an SC.
    2. Re-run the tests that cover the amended code. A finding about a vacuous
       or over-mocked test means writing a real test, not deleting the check.
    3. Do not expand scope beyond the findings. Do not touch other groups.
    4. Commit the fix on this branch.

    ## When a finding conflicts with the contract

    If a finding can only be resolved by changing what the contract requires —
    the FR is wrong, an SC is impossible, or the fix would break a cited
    invariant — STOP. Do not reinterpret the contract to force green, and do not
    edit the contract yourself. Report status AMEND_SPEC, name the FR/SC/INV in
    tension and why, and hand it back. The human decides a contract change.

    ## Report

    Append your fix to [REPORT_PATH] (the group's report file):
    - Each finding, and what you changed to resolve it (file:line).
    - The tests you re-ran and their output (the reviewer will not re-run them —
      your report is the test evidence).

    Then return ONLY:
    - **Status:** FIXED | FIXED_WITH_CONCERNS | AMEND_SPEC | BLOCKED
    - Commits created (short SHA + subject)
    - One-line test summary
    - Any finding you could not resolve, and why
```

## Placeholders

- `[GROUP_NAME]` — the group being fixed.
- `[FAILED_VERDICT]` — which of the three reviewer verdicts failed (compliance / quality / invariants).
- `[FINDINGS]` — the reviewer's Critical/Important findings, pasted verbatim with file:line. (Findings are small and specific — pasting them is fine; contract FR/SC text is not, so still point at `[CONTRACT_PATH]`.)
- `[MODEL]` — REQUIRED. The implementer's tier, one step up for a harder fix.
- `[CONTRACT_PATH]` / `[PROJECT_SPEC_PATH]` / `[INV_LIST]` — the contract, the project spec, and the cited invariants.
- `[BRANCH_OR_WORKTREE_DIR]` / `[REPORT_PATH]` — the group's build branch and its report file.

After the fixer returns FIXED, rebuild the review package from the new head and re-review (all three verdicts) until every verdict PASSes. An `AMEND_SPEC` return leaves the loop: it routes to `writing-specs` (the contract regresses to `draft` and re-earns its gate) or `grounding-specs` (a shared fact), the human's call.
