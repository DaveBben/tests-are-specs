# Implementation Agent Dispatch Prompt

Prompt template for the implementation agent. One agent reads the task
JSON and implements directly.

---

## Prompt

```
You are implementing a single task from an approved plan.

PLAN CONSTRAINTS — do NOT violate these:
[constraints from plan.json verbatim]

Task file: [path to task_N.json]
Plan file: [path to plan.json]

Read the task JSON. It contains your specification (acceptanceCriteria),
the pattern to follow (reference), files to touch (files), regression
targets (atRiskTests), and boundaries (doNot).

1. Read reference, testContext, and implementationContext
2. Implement to satisfy all acceptanceCriteria
3. Run atRiskTests — fix regressions without changing existing tests
4. Run verificationCommand

If the task has an environmentCheck, run it first. If it fails,
return STOPPED with reason "environment not ready: [error]".

Known-failures baseline (ignore these):
[list from pre-flight test baseline, or "none"]

Do NOT modify existing test files.
Do NOT commit — leave changes uncommitted.
Before reporting, re-read the task's doNot list and verify you
haven't crossed any boundary.

Report only file names, line counts, and test results — do not echo
file contents or full test output. Format:
- Status: DONE or STOPPED (with reason)
- Files changed: list with line counts
- At-risk tests: all passing / [which failed]
- Verification: passing / failing
- Issues: deviations or concerns, or "none"
```
