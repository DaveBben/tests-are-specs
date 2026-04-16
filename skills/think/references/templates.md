# Think Artifact Templates

## brainstorm.md

```markdown
# Brainstorm: {feature description}

**Date**: {YYYY-MM-DD}
**Status**: Draft | Approved
**Slug**: {slug}

## What and Why

**Change**: [One sentence — the concrete outcome when done]
**Why**: [The problem, who has it. No technology.]

## Scope

### In
- [Specific thing this change builds or changes]

### Out
- [Thing explicitly excluded] — [why]

### Constraints (must not change)
- [Existing API, schema, or interface to preserve]

## Impact Surface

| File | Concern | Why affected |
|------|---------|--------------|
| `src/path/file.ts` | [concern group] | [one sentence] |

### Dependency Chain
`[entry point]` → `[intermediate]` → `[target symbol]`

## At-Risk Tests

| Test file | Symbol | Why it could regress |
|-----------|--------|----------------------|
| `tests/path/test.ts` | `describe('...')` | [reason] |

> Tests marked [unverified] were not confirmed by the user.

## Chosen Approach

**Approach**: [name of chosen approach]
**Why chosen**: [the constraint or trade-off that decided it]
**Rejected**: [alternative] — [why not]

## Boundaries

### Do NOT
- [Explicit thing this change must not touch or do]

### Failure Modes Decided
- **[Failure mode]**: [how it should be handled — human decision]

## Open Questions
- [TBD items awaiting decision]
```

> **Target: under 200 lines.** If approaching the limit, cut empty
> sections, compress prose, and remove anything derivable from the code.
> The plan skill reads this file as its primary input — every line must
> earn its place by informing a decision the AI cannot make from the code
> alone.
