# Feature Artifact Templates

Templates for the markdown artifacts produced by `/feature`. Each template
shows the expected structure — replace bracketed placeholders with real content.

## Contents

- [research.md](#researchmd)
- [impact-map.md](#impact-mapmd)
- [plan.md](#planmd)
- [tasks.md](#tasksmd)
- [Task JSON Schemas](#task-json-schemas)

---

## research.md

```markdown
# Research: {feature description}

## Project Context
[What was learned from architecture.md, spec.md, etc. — summarize the
relevant parts, not everything]

## Feature Intent
**What**: [The concrete change the user wants — confirmed by user]
**Why**: [The motivation, problem, or goal — confirmed by user]

## External Context
[Context provided by the user from outside the codebase. Include summaries
of fetched URLs, verbatim user-provided context, or "No external context
provided." Every entry must note its source.]

## Codebase Findings
[Deep reading results — specific files, functions, patterns found.
Every claim must include a file:line reference.]

## Placement Analysis
**Where does this change belong in the system?**
[Answer with specific modules, directories, files, and reasoning]

## Existing Patterns
**Does something similar already exist?**
[Yes/no — with file:line references if yes, search methodology if no]

## Reusable Solutions
**Have we solved a related problem before?**
[Patterns, utilities, approaches that apply — with file:line references]

## Open Questions
[Things discovered during research that need user input before planning]

## Devil's Advocate Challenge
[Appended by the devils-advocate agent — do not write manually]

### Assumptions (verify before planning)
- **[Assumption]**: [Why this might be wrong, grounded in codebase evidence]

### Ambiguities (clarify before planning)
- **[Term or behavior]**: Could mean [A] or [B]. This matters because [consequence].

### Edge Cases (address in plan or explicitly defer)
- **[Scenario]**: [What happens and why it's not covered]

### Scope Creep Risks (draw the line now)
- **[Adjacent concern]**: Tempting because [reason]. Dangerous because [consequence].

### Pre-Mortem
> [2-3 sentences, past tense, narrating the most likely failure]

### User Responses
[Filled in after user reviews the challenges]
```

---

## impact-map.md

```markdown
# Impact Map: {feature description}

## Files Affected

| File | Action | Symbols | Reason |
|------|--------|---------|--------|
| `src/path/file.ts` | modify | `functionName()` | [why this file changes] |
| `src/path/new.ts` | create | — | [what this new file does] |
| `tests/path/test.ts` | create | — | [tests for what] |

## Existing Patterns to Follow

- [Pattern name]: See `file:line` — [how it applies here]

## Dependencies Touched

- [Module/package/service] — [how it's affected downstream]

## Risk Areas

- [File or module where a mistake would have outsized impact] — [why]
```

---

## plan.md

```markdown
# Plan: {feature description}

**Date**: {YYYY-MM-DD}
**Status**: Draft

## What This Delivers

[2-4 sentences. What will exist or be different when done. Plain language —
a non-technical stakeholder should understand.]

## Why

[The problem, who has it, and why it matters. No technology, no solution
description.]

## Scope

### In
- [thing this change builds or fixes]

### Out
- [thing this change does NOT build] — [why]

### Constraints (what must NOT change)
- [existing API, schema, or interface to preserve]
- [behavior that callers depend on]

## Architectural Decisions

### [Decision 1]
**Chosen**: [approach]
**Why**: [rationale]
**Rejected**: [alternative] — [why rejected]

## Implementation

### {Logical Section 1}

**Files**: `src/path/to/file.ts`

**What changes**: [Concrete description of the change]

**Proposed code**:
[Actual function signatures, type definitions, schema changes — the real
code that will be written, not pseudocode. When the AI has a concrete
reference, it implements against that reference instead of designing from
scratch.]

**Reference**: See `src/existing/similar.ts:42` for the pattern to follow

### {Logical Section 2}
...

## Trade-offs
[What was considered, what was chosen, and what was given up]

## Delivery Strategy

**Estimated total change size**: [rough line count based on impact map]
**PR strategy**: [Single PR / Stacked PRs]

[If single PR, omit the slice sections below.]

### Slice 1: [one-sentence description of the diff, not the goal]
- **Capabilities delivered**: [what works after this merges]
- **Files touched**: [list]

### Slice 2: [one-sentence description of the diff]
- **Capabilities delivered**: [what works after this merges]
- **Files touched**: [list]
- **Depends on**: Slice 1

[Each slice must leave the project in a working state with all tests passing.]

## What NOT to Do
[Explicit anti-patterns and boundaries for the implementer]

---

*This plan is ready for annotation. Do not implement yet.*
```

---

## tasks.md

```markdown
# Tasks: {feature description}

**Status**: Ready
**Total Tasks**: {N}

## 1. {Phase/Section Name}

### 1.1 {Task Title}
- **File**: `src/path/to/file.ts`
- **Symbol**: `createWebhookHandler()`
- **Reference**: See `src/existing/handler.ts:42` for the pattern
- **Must**: [single-concern description of what this task accomplishes]
- **Do NOT**: [explicit boundary — what adjacent work to avoid, which
  task owns it instead]
- **Done when**: [concrete, mechanically-verifiable condition]

### 1.2 {Task Title}
- **File**: `src/path/to/other.ts`
- **Symbol**: `WebhookRetryConfig`
- **Reference**: See `src/types/config.ts:10` for similar type
- **Must**: [...]
- **Do NOT**: [...]
- **Done when**: [...]

## 2. {Next Phase/Section}

### 2.1 {Task Title}
...

```

---

## Task JSON Schemas

### plan.json

Plan-level information stored at `.claude/features/{slug}/tasks/plan.json`:

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
  "risksAndRollback": "[from plan]",
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

One file per task at `.claude/features/{slug}/tasks/task_{N}.json`:

```json
{
  "id": "task_{N}",
  "slice": 1,
  "repository": ".",
  "title": "Task N: [Title]",
  "status": "PENDING",
  "implementer": "AI",
  "files": ["src/path/to/file.ts"],
  "symbol": "functionName()",
  "reference": "src/existing/pattern.ts:42",
  "blockedBy": [],
  "relevantFiles": [
    {"path": "src/path/to/file.ts", "action": "create"}
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
  "verificationCommand": "[single runnable command]",
  "scopeBoundaries": "[what this task owns] / [what others own]",
  "doNot": ["[explicit anti-scope]"],
  "doneWhen": "[mechanically-verifiable condition]",
  "executionNotes": ""
}
```
