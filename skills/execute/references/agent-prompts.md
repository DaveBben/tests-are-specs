# TDD Agent Dispatch Prompts

Exact prompts to use when dispatching TDD agents via the Agent tool. These
maintain context isolation between phases — the key design principle.

---

## RED — tdd-test-writer

```
You are executing the RED phase of TDD for a task.

PLAN CONSTRAINTS — do NOT violate these:
[constraints from plan.json verbatim]

Read the task at: [path to task_N.json]
Read the plan context at: [path to plan.json]

Write failing tests for this task's acceptance criteria.
Verify all tests fail before returning.

Do NOT read or consider any implementation code or plan implementation
sections. The acceptance criteria in the task JSON are your only
specification.
```

## GREEN — tdd-code-implementor

```
You are executing the GREEN phase of TDD for a task.

PLAN CONSTRAINTS — do NOT violate these:
[constraints from plan.json verbatim]

Failing test file(s): [paths from RED phase output]
Task file: [path to task_N.json]

Write the minimum code to make all tests pass.

For verification, first run the task's test file(s) directly. Then run
the full test suite. If a test fails that is in the known-failures
baseline below, ignore it — it was failing before this task started.

Known-failures baseline (pre-existing failures, ignore these):
[list from pre-flight test baseline, or "none"]

Do NOT modify the test files.
```

## REFACTOR — tdd-code-refactor

```
You are executing the REFACTOR phase of TDD for a task.

Implementation file(s): [paths from GREEN phase output]
Test file(s): [paths from RED phase output]
Task file: [path to task_N.json]

Evaluate whether refactoring improves the code. If so, refactor while
keeping all tests green. If not, return "No refactoring needed" with
reasoning.
```
