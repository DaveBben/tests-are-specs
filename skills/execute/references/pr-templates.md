# PR Body Templates

The user creates PRs manually — these are body content only.

## Feature PR

**Title**: `[feature description]`

```markdown
## Summary
[From plan.json — whatWeAreBuilding and whyThisExists]

## Changes
[Bullet list from task titles]

## Test plan
- [ ] All automated tests pass
- [ ] [Manual verification items from acceptance criteria]

## Known Issues
[Unfixed findings from deep review, or "None"]

Generated with [Claude Code](https://claude.com/claude-code)
```

## Bugfix PR

**Title**: `Fix: [symptom title]`

```markdown
## Bug
**Symptom:** [from plan.json]

## Root Cause
[From plan.json]

## Fix
[From plan.json — whatThisDelivers]

## Test Plan
- [ ] Regression test passes
- [ ] Full test suite passes

## Known Issues
[Unfixed findings, or "None"]

Generated with [Claude Code](https://claude.com/claude-code)
```

## Multi-Slice Strategy

For `totalSlices > 1`:
1. Each slice gets its own PR
2. Slice 1 targets base branch; slice 2+ targets previous slice's branch
3. Mark slice 2+ as **draft** until parent merges
4. Title: `[feature] (slice N/M)`
