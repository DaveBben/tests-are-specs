# Plan Artifact Templates

- [plan.md](#planmd)
- [task_{N}.json](#task_njson)
- [plan.json](#planjson)

## plan.md

```markdown
# Plan: {feature description}

**Date**: {YYYY-MM-DD}
**Status**: Draft

## What This Delivers

[2-4 sentences. What will exist when done. Plain language.]

## Why

[The problem, who has it, why it matters. From brainstorm.md.]

## Scope

### In
- [thing this change builds or fixes]

### Out
- [thing this change does NOT build] — [why]

### Constraints (what MUST NOT change)
- [existing API, schema, or interface to preserve]

## Impact

| File | Action | Symbol | Reason |
|------|--------|--------|--------|
| `src/path/file.ts` | modify | `functionName()` | [why] |
| `src/path/new.ts` | create | — | [what it does] |

### Patterns to Follow
- [Pattern]: See `file:line` — [how it applies]

*(max 2 entries — closest analogues only)*

### Risk Areas
- [File or module] — [why a mistake here has outsized impact]

## Architectural Decision

**Chosen**: [approach from brainstorm.md]
**Why**: [the constraint or trade-off that decided it]
**Rejected**: [alternative] — [why not]

## Implementation

### {Section}

**Files**: `src/path/to/file.ts`
**Symbol**: `functionName()`
**What changes**: [concrete description]
**Current**:
```[lang]
[existing signature or schema — paste verbatim from codebase]
```
**Proposed**:
```[lang]
[exact new signature — not pseudocode]
```
**Reference**: See `src/existing/similar.ts:42`

## What NOT to Do
- [Exact text from brainstorm.md Do NOT — copy verbatim]

## Delivery Strategy

**Estimated size**: [line count]
**PR strategy**: Single PR / Stacked PRs

### Slice 1: [one-sentence description]
- **Files**: [list]
- **Delivers**: [what works after this merges]

---

*Do not implement yet.*
```

> **Target: 100–200 lines.** Omit any section with no meaningful
> content. A shorter, focused plan outperforms a comprehensive one.

---

## task_{N}.json

```json
{
  "id": "task_{N}",
  "slice": 1,
  "repository": ".",
  "title": "Task N: [Title]",
  "status": "PENDING",
  "implementer": "AI",
  "intent": "[Why this task exists — one sentence enabling ambiguity resolution]",
  "files": ["src/path/to/file.ts"],
  "symbol": "functionName()",
  "reference": "src/existing/pattern.ts:42",
  "dependencyChain": ["src/routes/index.ts", "src/controllers/feature.ts", "src/services/feature.ts"],
  "relevantFiles": [
    {"path": "src/path/to/file.ts", "action": "modify"}
  ],
  "blockedBy": [],
  "atRiskTests": [
    {
      "path": "tests/existing.test.ts",
      "symbol": "describe('existing')",
      "reason": "[why this test could regress from this change]"
    }
  ],
  "doNot": ["[boundary from plan.md What NOT to Do]"],
  "acceptanceCriteria": [
    "GIVEN [precondition], WHEN [action], THEN [expected outcome]"
  ],
  "verificationCommand": "[single runnable test command]",
  "regressionCheck": "[command to run atRiskTests — empty string only if atRiskTests is empty]",
  "scopeBoundaries": "[what this task owns] / [what adjacent tasks own]",
  "doneWhen": "[mechanically verifiable condition — include 'and regressionCheck passes' when atRiskTests is non-empty]"
}
```

**Field notes:**
- `intent`: explains *why*, not *what*. Enables the agent to make
  judgment calls at ambiguous decision points.
- `files`: 1–4 entries. More than 4 is a planning error — split.
- `reference`: single entry only. The closest existing pattern.
  More than one reference risks context type interference.
- `dependencyChain`: 3–5 hops, verified against codebase. Prevents
  NameError-class failures from missing cross-file references.
- `atRiskTests`: populated from brainstorm.md's confirmed list.
  Empty array only if no existing tests touch the affected code.
- `regressionCheck`: must be set whenever `atRiskTests` is non-empty.

---

## plan.json

```json
{
  "date": "YYYY-MM-DD",
  "status": "Approved",
  "featureSlug": "{slug}",
  "featureDescription": "{description}",
  "whatWeAreBuilding": "[from plan.md What This Delivers]",
  "whyThisExists": "[from plan.md Why]",
  "scope": {
    "in": ["..."],
    "out": ["..."],
    "constraints": ["..."]
  },
  "knownRisks": ["[from plan.md Risk Areas]"],
  "criticalReminders": ["[from plan.md What NOT to Do]"],
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
