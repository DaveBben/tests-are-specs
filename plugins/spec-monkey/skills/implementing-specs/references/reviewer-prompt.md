# Reviewer dispatch prompt (subagent mode)

Ready-to-use brief for the per-group review gate. Fill the `[BRACKETED]` slots and dispatch. The reviewer reads one group's diff once and returns **three verdicts**: spec compliance, code quality, and invariants. The prose that governs this loop is in [`subagent-mode.md`](subagent-mode.md).

This gate applies checks 1, 3, and 9 of [`../../auditing-specs/references/audit-rubric.md`](../../auditing-specs/references/audit-rubric.md) to one group's diff; it never inlines the full nine-check rubric and never emits a COMPLIANT verdict. `auditing-specs` stays the independent gate, run afterward by a fresh agent.

"Dispatch a subagent" is an action, not a tool name: use whatever your harness provides for spawning a fresh agent and reading its result back, with a general coding-agent type. The per-harness tool mapping lives outside the skills, in the spec-monkey repository's `docs/harness-tools/`.

```
Dispatch a subagent:
  description: "Review [GROUP_NAME] (compliance + quality + invariants)"
  model: [MODEL — REQUIRED: reviewer floor is mid-tier; scale up for a subtle
          invariant. See subagent-mode.md "Model selection". Never omit.]
  prompt: |
    You are reviewing one FR-group's implementation against its contract. This
    is a group-scoped gate, not a merge review — the independent whole-build
    audit (auditing-specs) runs separately afterward. Return three verdicts.

    ## What was requested

    Read the group named "[GROUP_NAME]" under *Requirements & success criteria*
    in: [CONTRACT_PATH]. That is the obligation set. Also note the group's
    *Constraints & non-functional bounds* and *Data & interface contract*.

    The cited invariants this group's code path must uphold, from
    [PROJECT_SPEC_PATH]: [INV_LIST].

    ## What the implementer claims

    Read the implementer's report: [REPORT_PATH]. Treat it as unverified claims.
    A stated rationale ("left it simple per YAGNI", "deliberately skipped X") is
    the implementer grading their own work — it never downgrades a finding.

    ## The diff under review

    Base: [BASE_SHA]  Head: [HEAD_SHA]
    Diff package: [DIFF_PATH]

    Read the diff file once — it holds the commit list, the stat summary, and
    the full diff with context. Those context lines ARE the changed files: do
    not open a changed file separately unless a hunk you must judge is cut off
    mid-function (say so if it is). Do not crawl the wider codebase; inspect
    code outside the diff only to check one concrete, named risk (a changed
    contract, shared state, lock ordering) — name the risk and what you checked.
    Your review is read-only: do not mutate the working tree, index, or HEAD.

    ## Tests

    The implementer ran the tests and reported TDD evidence for this code. Do
    not re-run the suite to confirm the report. Run a focused test only when the
    code raises a specific doubt no existing run answers. Warnings or noise in
    the reported output are findings — test output should be pristine.

    ## Verdict 1 — Spec compliance

    Every FR in the group traces to code that satisfies it; nothing extra,
    nothing misunderstood. Report: Missing (an FR skipped or claimed but not
    built), Extra (scope not requested), Misunderstood (right FR, wrong
    behavior). If an FR can't be verified from this diff alone, mark it ⚠️ and
    say what the controller should check — do not broaden your search.

    ## Verdict 2 — Code quality

    Clean separation, honest error handling, no premature abstraction, edge
    cases handled. Tests verify real behavior, not mocks; the group's edge cases
    are covered; no vacuous assertions, no over-mocking that leaves the real
    path untested. Flag files this change made large or tangled (not
    pre-existing size).

    ## Verdict 3 — Invariants

    Every cited invariant ([INV_LIST]) the group's code path touches still
    holds. Trace each to the code that upholds or endangers it, with file:line.
    This verdict is why a generic reviewer port is not enough for spec-monkey —
    do not skip it.

    ## Output

    Point at evidence: file:line for every finding and for any check you'd
    otherwise answer with a bare "yes". Begin directly with Verdict 1 — no
    preamble, no process narration.

    ### Verdict 1 — Spec compliance: PASS | FAIL
    - findings with file:line, and ⚠️ cannot-verify items
    ### Verdict 2 — Code quality: PASS | FAIL
    - Critical / Important / Minor, each with file:line and why it matters
    ### Verdict 3 — Invariants: PASS | FAIL
    - per cited INV: upheld / endangered, with file:line evidence

    A verdict is FAIL if it carries any Critical or Important finding. Minor
    findings alone do not fail a verdict; list them anyway.
```

## Placeholders

- `[GROUP_NAME]` — the `### <subsystem / seam>` heading under review.
- `[MODEL]` — REQUIRED. Mid-tier floor; scale up for a subtle invariant.
- `[CONTRACT_PATH]` / `[PROJECT_SPEC_PATH]` / `[INV_LIST]` — the contract, the project spec, and the invariants this group touches.
- `[REPORT_PATH]` — the implementer's report file (unverified claims).
- `[BASE_SHA]` / `[HEAD_SHA]` — the commit before dispatch and the group's head. Record BASE **before** dispatch; never use `HEAD~1`.
- `[DIFF_PATH]` — the review package, built with plain git and redirected to a file so it never enters the controller's context:
  `git log --oneline BASE..HEAD`, `git diff --stat BASE..HEAD`, `git diff -U10 BASE..HEAD`.

Any FAIL verdict routes to a fixer (see [`fixer-prompt.md`](fixer-prompt.md)); rebuild the package and re-review until all three verdicts PASS.
