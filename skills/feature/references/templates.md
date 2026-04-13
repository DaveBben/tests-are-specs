# Feature Artifact Templates

## Contents

- [plan.md](#planmd)
- [tasks.md](#tasksmd)
- [Task JSON Schemas](#task-json-schemas)

---

## plan.md

```markdown
# Plan: {feature description}

**Date**: {YYYY-MM-DD}
**Status**: Draft

## What This Delivers

[2-4 sentences. What will exist when done. Plain language.]

## Why

[The problem, who has it, why it matters. No technology.]

## Scope

### In
- [thing this change builds or fixes]

### Out
- [thing this change does NOT build] — [why]

### Constraints (what MUST NOT change)
- [existing API, schema, or interface to preserve]

## Impact

| File | Action | Symbols | Reason |
|------|--------|---------|--------|
| `src/path/file.ts` | modify | `functionName()` | [why] |
| `src/path/new.ts` | create | — | [what it does] |
| `tests/path/test.ts` | create | — | [tests for what] |

### Patterns to Follow
- [Pattern]: See `file:line` — [how it applies]

### Risk Areas
- [File or module] — [why a mistake here has outsized impact]

## Architectural Decisions

### [Decision]
**Chosen**: [approach]  **Why**: [rationale]
**Rejected**: [alternative] — [why]

## Implementation

### {Section}

**Files**: `src/path/to/file.ts`
**What changes**: [concrete description]
**Proposed code**:
[Actual signatures, types, schemas — not pseudocode. Paste existing
reference implementation alongside proposed change.]
**Reference**: See `src/existing/similar.ts:42`

## Assumptions
- [Specific, falsifiable claim the plan depends on]

## Delivery Strategy

**Estimated size**: [line count]
**PR strategy**: Single PR / Stacked PRs

### Slice 1: [one-sentence diff description]
- **Files**: [list]
- **Delivers**: [what works after this merges]

## What NOT to Do
- [Explicit anti-pattern or boundary]

---

*Do not implement yet.*
```

> **Target: 100-200 lines.** If the plan exceeds 300 lines, the feature
> likely needs splitting or the scope is too broad.

---

## tasks.md

```markdown
# Tasks: {feature description}

**Total Tasks**: {N}

## {Section}

### {N}. {Task Title}
- **File**: `src/path/to/file.ts`
- **Symbol**: `functionName()`
- **Reference**: See `src/existing/handler.ts:42`
- **MUST**: [single-concern description]
- **Do NOT**: [explicit boundary]
- **Done when**: [mechanically verifiable condition]
```

---

## Task JSON Schemas

### plan.json

```json
{
  "date": "YYYY-MM-DD",
  "status": "Approved",
  "featureSlug": "{slug}",
  "featureDescription": "{description}",
  "whatWeAreBuilding": "[from plan]",
  "whyThisExists": "[from plan]",
  "scope": {
    "in": ["..."],
    "out": ["..."],
    "constraints": ["..."]
  },
  "knownRisks": ["[domain-specific risks]"],
  "criticalReminders": ["..."],
  "totalTasks": "N",
  "repositories": ["."],
  "totalSlices": 1,
  "slices": [
    {
      "id": 1,
      "description": "[one-sentence diff description]",
      "files": ["src/path/a.ts", "src/path/b.ts"]
    }
  ]
}
```

### task_{N}.json

```json
{
  "id": "task_{N}",
  "slice": 1,
  "repository": ".",
  "title": "Task N: [Title]",
  "intent": "[Why this task exists — enables the agent to resolve ambiguities]",
  "status": "PENDING",
  "implementer": "AI",
  "files": ["src/path/to/file.ts"],
  "symbol": "functionName()",
  "reference": "src/existing/pattern.ts:42",
  "blockedBy": ["task_0"],
  "atRiskTests": [
    {"path": "tests/existing.test.ts", "symbol": "describe('existing')", "reason": "[why this test could regress]"}
  ],
  "relevantFiles": [
    {"path": "src/path/to/file.ts", "action": "create"}
  ],
  "testContext": [
    {"path": "src/types/contracts.ts", "reason": "[interfaces needed for tests]"}
  ],
  "implementationContext": [
    {"path": "src/services/existing.ts", "reason": "[pattern to follow]"}
  ],
  "acceptanceCriteria": [
    "GIVEN [precondition], WHEN [action], THEN [expected outcome]"
  ],
  "environmentCheck": "",
  "verificationCommand": "[single runnable command]",
  "scopeBoundaries": "[what this task owns] / [what others own]",
  "doNot": ["[explicit anti-scope]"],
  "doneWhen": "[mechanically-verifiable condition]",
  "executionNotes": ""
}
```

Notes:
- **files**: 1-4 entries. More than 4 is a planning error — split the task.
- **intent**: Explains *why*, not *what*. Enables the agent to make judgment
  calls at ambiguous decision points.
- **atRiskTests**: Existing tests that could regress from this change. Traced
  from dependents of modified files. Empty array only if no existing tests
  touch the affected code.
- **blockedBy**: Set when this task consumes a type, interface, or migration
  created by an earlier task.
- **testContext**: max 3 entries — interfaces, types, and contracts only
- **implementationContext**: max 3 entries — pattern references only
- No path should appear in both `testContext` and `implementationContext`
