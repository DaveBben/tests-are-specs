# Implementer dispatch prompt (subagent mode)

Ready-to-use brief for one FR-group. Fill the `[BRACKETED]` slots and dispatch. The prose that governs this loop is in [`subagent-mode.md`](subagent-mode.md); this file is the artifact you paste.

Never paste FR/SC text into this prompt — point at `contract.md` by path and group name. Bulk content pasted here stays resident in the controller's context on every later turn; a path does not.

"Dispatch a subagent" is an action, not a tool name: use whatever your harness provides for spawning a fresh agent and reading its result back, with a general coding-agent type. The per-harness tool mapping lives outside the skills, in the spec-monkey repository's `docs/harness-tools/`.

```
Dispatch a subagent:
  description: "Implement [GROUP_NAME] ([FR_RANGE, e.g. FR-001..FR-003])"
  model: [MODEL — REQUIRED: choose per subagent-mode.md "Model selection";
          an omitted model silently inherits the session's most expensive one]
  prompt: |
    You are implementing one FR-group of an approved spec-monkey spec. The spec
    says WHAT and WHEN; the HOW is yours, worked out from the contract and the
    real code. Do not add scope the group didn't ask for; do not drop an FR.

    ## Your contract

    Read the group named "[GROUP_NAME]" under *Requirements & success criteria*
    in: [CONTRACT_PATH, e.g. docs/specs/rate-limiter/detail/contract.md]

    Use the exact FR/SC values verbatim from that file. Also read, in the same
    file: *Constraints & non-functional bounds*, *Data & interface contract*,
    *When it happens*, *Out of scope*, and *Verification approach & commands*.
    Build only this group; other groups are being built separately.

    ## The invariants you must uphold

    Read the project spec: [PROJECT_SPEC_PATH, e.g. docs/specs/project/spec.md]
    Your group's code path must uphold: [INV_LIST, e.g. INV-001, INV-004].
    An invariant binds as firmly as an FR. If you cannot satisfy a local FR
    without breaking a cited invariant, STOP and report NEEDS_AMENDMENT — do
    not break the invariant to go green.

    ## Interfaces you consume

    Earlier groups already produced: [INTERFACES_FROM_PRIOR_GROUPS, or "none —
    this is the first group"]. Build against those as they exist in the code,
    not against a guess.

    ## Where you work

    Work from: [BRANCH_OR_WORKTREE_DIR]. Build on this branch only; never touch
    the live mainline.

    ## How to build

    1. For each success criterion a test can check: write the test first, run it,
       watch it fail for the right reason (RED) before you build the behavior.
       Then implement until every FR in the group holds and its test passes
       (GREEN). Where an SC has no test surface (a manual check, a config edit),
       say so and run the spec's verification command instead of faking a test.
    2. Respect the constraints, the data/interface contract, and the ordering.
       Build nothing on the *Out of scope* list.
    3. Mirror the patterns already in the codebase; don't invent new ones.
    4. Commit your work on this branch when the group is green. Run the group's
       focused tests while iterating; run the full suite once before you commit.

    ## When you are over your head

    It is always OK to stop. Bad work is worse than no work. STOP and report
    BLOCKED or NEEDS_AMENDMENT when:
    - The contract is ambiguous, impossible, or fights a cited invariant
      (→ NEEDS_AMENDMENT: name the FR/INV and why).
    - You need context beyond the contract and the code and can't find it
      (→ BLOCKED: say what you need).
    Do not reinterpret the contract to force green. A contract bug is the
    human's call, not yours.

    ## Report

    Write your full report to [REPORT_PATH, e.g. .spec-monkey/report-[GROUP_SLUG].md]:
    - What you built, per FR.
    - TDD evidence per SC that had a test: RED (command + failing output + why
      the failure was expected) and GREEN (command + passing output).
    - For an SC with no test surface: the verification command you ran and its
      output.
    - Files changed. Any invariant you had to actively design around, and how.
    - Concerns, if any.

    Then return ONLY (under 15 lines — the detail lives in the report file):
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_AMENDMENT
    - Commits created (short SHA + subject)
    - One-line test summary (e.g. "9/9 passing, output pristine")
    - Concerns, if any
    - The report file path

    Statuses: DONE (group built and green); DONE_WITH_CONCERNS (built, but you
    doubt something — name it); BLOCKED (cannot finish, need context);
    NEEDS_AMENDMENT (a shared fact is missing or the contract is wrong → routes
    to grounding-specs or an amend-spec, the human's call).
```

## Placeholders

- `[GROUP_NAME]` / `[FR_RANGE]` — the `### <subsystem / seam>` heading and its FR range.
- `[MODEL]` — REQUIRED. Scale to the group (see `subagent-mode.md`). Never omit.
- `[CONTRACT_PATH]` — the spec's `detail/contract.md`. The implementer reads FR/SC from here; you never paste them.
- `[PROJECT_SPEC_PATH]` / `[INV_LIST]` — the project spec and the `INV-NNN` this group's code path touches.
- `[INTERFACES_FROM_PRIOR_GROUPS]` — what earlier groups produced that this one consumes; "none" for the first group.
- `[BRANCH_OR_WORKTREE_DIR]` — the isolated build branch/worktree (see `build-workspace.md`).
- `[REPORT_PATH]` / `[GROUP_SLUG]` — where the implementer writes its full report; keep it under `.spec-monkey/`.
