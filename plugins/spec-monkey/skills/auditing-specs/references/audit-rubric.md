# Audit rubric

## What binds

The spec states WHAT and WHEN. These parts of it are the contract you audit against:

- **Requirements** (`FR-NNN`, in `detail/requirements.md`): the behavior that had to be built.
- **Success criteria** (`SC-NNN`, beside their requirements) and **Verification approach & commands** (the
  commands and the worked case): the proof it works.
- **Data & interface contract**: the shapes and signatures other code depends on.
- **Constraints & non-functional bounds**: the limits the build had to respect.
- **Out of scope**, and the **Failure modes** decisions: the boundaries and the failure handling.
- **When it happens**: ordering, triggers, rollout conditions.

You do NOT judge code quality, security, or performance beyond what that contract and those bounds require:
that is generic review, a different job. You also do not re-litigate the spec's design.

## Checks

Run each. Mark OK, FAIL, or REVIEW (couldn't determine it here), each with evidence.

**1. Requirements built**
- For each `FR-NNN`, trace the code that satisfies it. An `FR-NNN` with no implementing code is a FAIL.
- A partial build is a FAIL against the unbuilt part: the FR's WHEN condition ignored, or one clause of a
  multi-part SHALL missing.

**2. Verification passes for real**
- Run the commands under *Verification approach & commands*. Don't trust the prose; execute them.
- Every runnable `SC-NNN` must hold, and the *Worked case* must produce the exact `Then` values it states
  from real input. A command that errors, or an SC that doesn't hold, is a FAIL.
- For an `SC-NNN` only measurable after deploy (a production metric), confirm the instrumentation to
  evaluate it exists (a log, counter, event, or dashboard hook) in the diff or the system. Nothing measures
  it → FAIL (it ships blind). Can't tell whether external instrumentation covers it → REVIEW. Do NOT assert
  the post-deploy number was hit; that is not knowable here.

**3. No faked done**
- A requirement counts as built only if a check would catch it breaking. For each FR's backing test,
  confirm it exercises the real path and would fail if the behavior regressed.
- Flag vacuous proof: an assertion on a constant, a mock verifying itself, the real code path stubbed out
  so the test passes without it, or an `SC` "met" by a test that never runs the behavior. This is the
  failure this audit exists to catch.

**4. Data & interface contract**
- The code implements each contract in *Data & interface contract* as specified: field names, shapes,
  invariants, and signatures match. A renamed field, a dropped attribute, a changed signature, or a broken
  invariant is a FAIL. Cite the consuming code that expects the specified shape.

**5. Constraints & non-functional bounds**
- Each **Constraint** and **Non-functional bound** in *Constraints & non-functional bounds* is satisfied;
  cite where. For a bound whose threshold needs a benchmark or a production measurement you can't run here,
  mark REVIEW and name the measurement a human must take.

**6. Scope discipline**
- Nothing under *Out of scope* was built, and a "don't touch X" prohibition is respected.
- No requirement was silently dropped, and no behavior was added that the spec never asked for. Real scope
  creep is a deviation: recommend "amend spec" if the addition is warranted, "fix code" (remove it) if
  not. Lockfiles, generated files, and formatting-only churn are not scope creep; note, don't fail.

**7. Edge cases handled**
- For each case in *Failure modes* marked HANDLE, trace the input through the code to where it is handled
  per the decision. Missing HANDLE handling is a FAIL. A case marked ACCEPT or OUT-OF-SCOPE needs no code;
  confirm it was genuinely left alone, not half-built.

**8. Ordering & triggers**
- Where *When it happens* pins an order, a trigger, a precondition, or a rollout condition, confirm the
  build honors it: the migration runs before the read path, the job fires on the stated event, the gate
  blocks until the condition holds. Where the code alone can't confirm it, mark REVIEW.

## Before reporting, verify each finding

1. Is the deviation real, or did you miss where the code handles it? Grep wider; open the file at the line.
2. Is the citation accurate on both sides, the `file:line` and the spec header or ID?
3. Is the spec the thing that's wrong: a reasonable change the implementer made that the spec should adopt?
   If so, the recommendation is "amend spec", not "fix code".

Drop any finding that fails this pass. A false deviation wastes the same time a real one does.

## Re-verification mode

Invoked again after a fix (with the fix diff and your prior deviations): do NOT re-run everything.
1. Re-check only the prior deviations: mark each RESOLVED or NOT_RESOLVED with `file:line` evidence.
2. Scan the fix diff for any new deviation it introduced.
Return the report shape below, scoped to those.

## Output: a structured report

- **Verdict:** COMPLIANT or NON_COMPLIANT. (NON_COMPLIANT if any check FAILs.)
- **Spec:** the path and its `status`.
- **Failed checks:** the check names that FAILed (omit if COMPLIANT).
- **Deviations** (only if NON_COMPLIANT). For each:
  - **{check}**: what the contract requires, citing the header name / `FR-NNN` / `SC-NNN`.
  - **What the code does:** `file:line` evidence, or "nothing found" for a missing requirement.
  - **Recommendation:** "fix code: {change}" or "amend spec: {what + why}".
- **Open (REVIEW):** anything you couldn't determine here (a benchmark, external instrumentation, a
  post-deploy metric), so a human closes it.
- **What's verified:** two or three lines on what genuinely holds, so the reader knows what not to re-check.

Do not edit the spec or the code. Report only.
