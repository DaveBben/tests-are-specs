# Bug Artifact Templates

Templates for the markdown artifacts produced by `/cks:bug`. Each template
shows the expected structure — replace bracketed placeholders with real content.

---

## research.md

```markdown
# Research: Bug — {symptom title}

## Symptom Summary
[From the conversational capture — what the user observed, severity,
environment, and reproduction steps. This is the bug card in prose form.]

- **Severity**: [Critical | High | Medium | Low]
- **Environment**: [OS, version, build, relevant config]
- **Frequency**: [Every time | Intermittent — conditions]
- **Workaround**: [Yes — description | None known]

## Reproduction Findings
[Results from the automated reproduction attempt in Phase 2.]

### Existing Test Coverage
[Which existing tests exercise the affected code path. Did any already fail?]

### Reproduction Test
[The draft reproduction test written during Phase 2. Include the full test
code — it becomes a reference for the task breakdown.]

```[language]
[full test code]
```

### Result
[RED — bug confirmed programmatically. Include exact failure output.]
[GREEN — bug did not reproduce in test environment. Note possible reasons:
environment-specific, intermittent, already fixed, test setup incomplete.]
[ERROR — infrastructure issue prevented running the test. Note what failed.]

## Exploration Questions
[10 codebase-answerable questions generated from the symptom data. These
force Explore agents to trace the downstream ripple of the bug and its fix.
Every answer MUST include file:line evidence or an explicit "not applicable"
with justification.]

1. **[Question]**
   > Answer: [finding with `file:line` reference]
2. **[Question]**
   > Answer: [finding with `file:line` reference]
3. **[Question]**
   > Answer: [finding with `file:line` reference]
4. **[Question]**
   > Answer: [finding with `file:line` reference]
5. **[Question]**
   > Answer: [finding with `file:line` reference]
6. **[Question]**
   > Answer: [finding with `file:line` reference]
7. **[Question]**
   > Answer: [finding with `file:line` reference]
8. **[Question]**
   > Answer: [finding with `file:line` reference]
9. **[Question]**
   > Answer: [finding with `file:line` reference]
10. **[Question]**
    > Answer: [finding with `file:line` reference]

## Codebase Findings
[Deep reading results from Phase 1 — specific files, functions, patterns
found along the bug's code path. Every claim must include a file:line
reference.]

### Entry Point
[The function or handler that receives the user action from the
reproduction steps — file:line]

### Code Path Trace
[Step-by-step trace from entry point to where behavior diverges from
expected. Each step includes file:line.]

### Data Flow
[What values are passed, transformed, and stored along the path.
Note where data changes shape or type.]

## Placement Analysis
**Where does this symptom originate in the system?**
[Specific modules, files, functions with reasoning — where the bug lives,
not just where the symptom appears]

## Root Cause Hypothesis
**What appears to be going wrong?**
[Based on code tracing and reproduction — a technical hypothesis. Clearly
labeled as a hypothesis, not a confirmed diagnosis.]

**Evidence supporting this hypothesis:**
- [Evidence 1 — file:line reference]
- [Evidence 2 — observed behavior]

**Evidence that might contradict it:**
- [Counter-evidence, if any]

## Existing Patterns
**How are similar code paths handled elsewhere?**
[Reference implementations that work correctly — file:line. These inform
what the fix should look like.]

## Recent Changes
[Output of `git log --oneline -20 -- [affected files]`. Note any recent
commits that might have introduced or relate to the bug.]

## Open Questions
[Uncertainties that need user input before planning]

## Sources Read

### Files
- `[path]` — [brief reason for reading, e.g., "traced code path", "existing test coverage"]

### URLs
- [url] — [summary of content retrieved]
- *No URLs fetched during this research.*

### Git History
- `[exact git command]` — [what was learned]
```

---

## impact-map.md

```markdown
# Impact Map: Bug — {symptom title}

## Files Affected

| File | Action | Symbols | Reason |
|------|--------|---------|--------|
| `src/path/file.ts` | modify | `functionName()` | [where the bug lives] |
| `tests/path/test.ts` | create | — | [regression test for this bug] |
| `tests/path/edge.ts` | create | — | [edge case tests] |

## Existing Patterns to Follow

- [Pattern name]: See `file:line` — [how it applies to the fix]

## Dependencies Touched

- [Module/package/service] — [how it's affected by the fix]

## Risk Areas

- [File or module where the fix could have unintended side effects] — [why]
```

---

## plan.md

```markdown
# Plan: Bug Fix — {symptom title}

**Date**: {YYYY-MM-DD}
**Status**: Draft

## What This Fixes

[2-4 sentences. What symptom will be resolved. What the user will see
differently after the fix. Plain language.]

## Why

[The symptom, who it affects, severity, and impact. Reference the
reproduction findings — was the bug confirmed programmatically?]

## Root Cause

[The confirmed or hypothesized root cause from research. Technical
explanation of what is going wrong and why.]

## Scope

### In
- Regression test that reproduces the bug
- Minimal fix addressing the root cause
- Edge case tests for related scenarios

### Out
- [Refactoring beyond what the fix requires] — [why]
- [Performance improvements] — separate work item
- [Related but different bugs] — separate bug cards

### Constraints (what must NOT change)
- [existing API, schema, or interface to preserve]
- [behavior that callers depend on]

## Implementation

### 1. Regression Test

**File**: `tests/path/test.ts`

**What changes**: Write a test that reproduces the bug — asserts expected
behavior and fails with the current code.

**Proposed code**:
[The draft reproduction test from research.md, refined for project
conventions. Actual test code, not pseudocode.]

**Reference**: See `tests/existing/similar.ts:42` for test pattern

### 2. Fix

**File**: `src/path/file.ts`

**What changes**: [Concrete description of the minimal fix]

**Proposed code**:
[Actual code showing the fix — function signatures, logic changes.
Not pseudocode.]

**Reference**: See `src/existing/working.ts:42` for correct pattern

### 3. Edge Case Tests (if applicable)

**File**: `tests/path/edge.ts`

**What changes**: [Additional test scenarios that exercise the same
code path under different conditions]

## What NOT to Do
- Do not refactor surrounding code
- Do not fix unrelated issues discovered during investigation
- Do not change public APIs or data formats unless required by the fix
- [Specific anti-patterns for this bug]

---

*This plan is ready for annotation. Do not implement yet.*
```

---

## tasks.md

```markdown
# Tasks: Bug Fix — {symptom title}

**Status**: Ready
**Total Tasks**: {N}

## 1. Regression Test

### 1.1 {Test Task Title}
- **File**: `tests/path/to/test.ts`
- **Symbol**: `test_bug_slug_symptom_description()`
- **Reference**: See `tests/existing/similar.ts:42` for test pattern
- **Must**: Write a test that reproduces the bug by asserting the expected
  behavior — the test must fail (RED) against the current code
- **Do NOT**: Write any implementation code or modify source files — the
  fix is a separate task
- **Done when**: Test exists, runs, and fails with an assertion error that
  matches the bug symptom

## 2. Fix Implementation

### 2.1 {Fix Task Title}
- **File**: `src/path/to/file.ts`
- **Symbol**: `affectedFunction()`
- **Reference**: See `src/existing/working.ts:42` for correct pattern
- **Must**: [single-concern description of the minimal fix]
- **Do NOT**: Refactor surrounding code, fix unrelated issues, or change
  the public API
- **Done when**: The regression test from task 1.1 passes (GREEN) and all
  existing tests still pass

## 3. Edge Case Tests (if applicable)

### 3.1 {Edge Case Task Title}
- **File**: `tests/path/to/edge.ts`
- **Symbol**: `test_bug_slug_edge_case_description()`
- **Reference**: See `tests/existing/similar.ts:42` for test pattern
- **Must**: Test [specific edge case scenario]
- **Do NOT**: Modify implementation code — if an edge case fails, create
  a new bug card
- **Done when**: Edge case test passes against the fixed code

```

---

## Task JSON Schemas

### plan.json

Plan-level information stored at `.claude/bugs/{slug}/tasks/plan.json`:

```json
{
  "date": "YYYY-MM-DD",
  "status": "Approved",
  "type": "bugfix",
  "bugSlug": "{slug}",
  "symptomTitle": "{symptom-based title}",
  "whatThisDelivers": "[from plan — what this fixes]",
  "whyThisExists": "[from plan — symptom, impact, severity]",
  "rootCause": "[from plan — root cause explanation]",
  "scope": {
    "in": ["regression test", "minimal fix", "edge case tests"],
    "out": ["..."],
    "constraints": ["..."]
  },
  "severity": "[Critical | High | Medium | Low]",
  "reproductionResult": "[RED | GREEN | ERROR]",
  "criticalReminders": ["..."],
  "totalTasks": "N"
}
```

### task_{N}.json

One file per task at `.claude/bugs/{slug}/tasks/task_{N}.json`:

```json
{
  "id": "task_{N}",
  "repository": ".",
  "title": "Task N: [Title]",
  "status": "PENDING",
  "implementer": "AI",
  "files": ["src/path/to/file.ts"],
  "symbol": "functionName()",
  "reference": "src/existing/pattern.ts:42",
  "blockedBy": [],
  "relevantFiles": [
    {"path": "src/path/to/file.ts", "action": "modify"}
  ],
  "testContext": [
    {"path": "src/types/contracts.ts", "reason": "[interfaces, types, contracts needed to write tests]"}
  ],
  "implementationContext": [
    {"path": "src/services/existing.ts", "reason": "[implementation details only the code writer needs]"}
  ],
  "steps": [
    "Read the reference implementation at src/existing/pattern.ts:42",
    "Write failing tests based on acceptance criteria below",
    "Run tests to verify they fail (confirm RED state)",
    "Write minimal implementation to make tests pass",
    "Run tests to verify they pass (confirm GREEN state)"
  ],
  "acceptanceCriteria": [
    "GIVEN [precondition], WHEN [action], THEN [expected outcome]"
  ],
  "environmentCheck": "[command to validate prerequisites, e.g. pg_isready -h localhost -p 5432, or empty string if none]",
  "verificationCommand": "[single runnable command]",
  "scopeBoundaries": "[what this task owns] / [what others own]",
  "doNot": ["[explicit anti-scope]"],
  "doneWhen": "[mechanically-verifiable condition]",
  "executionNotes": ""
}
```
