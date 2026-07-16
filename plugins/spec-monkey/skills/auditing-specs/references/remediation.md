# Remediation: the fix-and-re-audit loop (opt-in)

The auditor reports by default. This mode runs only when the user asks for it. It drives `fix-code` deviations to resolution and re-audits, while contract changes wait for a human. It never changes the report-only default.

## What this mode may change, and what it may not

- **`fix-code`**: the code diverged from the approved contract. The contract is right; the code is wrong. Apply the fix and re-verify.
- **`amend-spec` / `amend-project-spec`**: the *contract* should change. Applying one rewrites what the human approved. Never auto-apply it. Surface it, name the change and why, and stop. A spec amendment re-enters `reviewing-specs` / `writing-specs`; a project-spec amendment re-enters `grounding-specs`. This loop does not do that work.
- **REVIEW (Open) items**: undetermined here (a benchmark, external instrumentation, a post-deploy metric). The loop cannot close them. Leave them for the human.

## The loop

1. Audit as normal. COMPLIANT → stop.
2. NON_COMPLIANT → split the deviations: `fix-code` on one side; `amend-spec` / `amend-project-spec` / REVIEW on the other.
3. Apply the `fix-code` deviations, one at a time, with the verify-before-implement discipline below. Fix the code, never the check.
4. Re-verify using the **Re-verification mode** in [`audit-rubric.md`](audit-rubric.md): re-check only the prior deviations, mark each RESOLVED / NOT_RESOLVED with `file:line`, and scan the fix diff for any new deviation. This is the one re-check procedure; the loop adds no second.
5. Repeat 3-4 for still-NOT_RESOLVED deviations, capped at two more passes.
6. Stop when every `fix-code` deviation is RESOLVED, or one resists: still NOT_RESOLVED after the cap, or the only honest fix is a contract change (reclassify it to `amend-spec` and hand it to the human).
7. Report the `amend-*` and REVIEW items untouched. The verdict is COMPLIANT only when nothing of any kind remains open.

## Applying a fix: verify before you implement

A deviation is a claim, the same way `status: implemented` was.

- Re-read the code at the cited `file:line`. Confirm the deviation is real and not a place the auditor missed where the code already handles it. If it isn't real, drop it and say so with evidence; do not "fix" a non-problem.
- Confirm the fix makes the code meet the contract and breaks no other FR, SC, or cited `INV-NNN`. A fix that resolves one deviation and violates an invariant is not a fix.
- Change the code, not the success criterion, not the spec. If the only honest fix changes what the contract requires, that deviation was `amend-spec`, not `fix-code`: reclassify it and hand it to the human.
- Apply one deviation at a time and re-verify it, so a re-check maps to a single change.

No performative agreement with the report. You are not thanking the auditor; you are testing each finding and fixing the ones that hold. Where a finding is wrong, push back in the report with the `file:line` that disproves it.

## Severity gating

Gate by recommendation, not a Critical/Important/Minor axis. The recommendation already encodes the gate.

- **`fix-code`**: the loop resolves it. Every one is must-fix; the contract is approved, so there is no "minor" divergence from it.
- **`amend-spec` / `amend-project-spec`**: the contract-change gate. Surfaced, never crossed automatically.
- **REVIEW (Open)**: rolls up for a human to close; does not block the fixes.

## If your harness supports subagents

- **With subagents:** dispatch a fixer subagent with the deviation, its `file:line`, and the contract section it violates; hand it that diff only, not your audit history. It applies the `fix-code` change and reports the diff and the check it re-ran. Give it the verify-before-implement discipline above.
- **Without subagents (the portable default):** the same agent applies the `fix-code` change inline, or the human does, then you re-run the Re-verification checks. Identical loop, one context.

Never require the subagent path.

## What not to do

- Do not auto-apply an `amend-spec` or `amend-project-spec` deviation. Changing the contract is a human decision; the loop that grades against the contract must not also rewrite it.
- Do not weaken a check to reach COMPLIANT. Fix the code the check guards.
- Do not loop forever. Three passes on a `fix-code` deviation is the ceiling; past it, hand the human your evidence and stop.
- Do not turn the default audit into this. It runs only when the user asks.
