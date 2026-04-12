# PR Templates

Templates for creating pull requests via `gh pr create`. Choose based on source type.

---

## Feature PR

```
gh pr create --title "[feature description]" --body "$(cat <<'EOF'
## Summary
[From plan.json — whatWeAreBuilding and whyThisExists]

## Changes
[Bullet list from task titles]

## Test plan
- [ ] All automated tests pass
- [ ] [Manual verification items if any from task acceptance criteria]

## Known Issues
[Any unfixed BLOCKING/SHOULD_FIX from deep review, or "None"]

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Bugfix PR

```
gh pr create --title "Fix: [symptom title]" --body "$(cat <<'EOF'
## Bug

**Severity:** [from plan.json]
**Symptom:** [from plan.json — symptomTitle]

## Root Cause

[From plan.json — rootCause]

## Fix

[From plan.json — whatThisDelivers]

## Test Plan

- [ ] Regression test reproduces the bug (RED before fix)
- [ ] Fix makes the regression test pass (GREEN after fix)
- [ ] Full test suite passes
- [ ] [Edge case tests if applicable]

## Known Issues
[Any unfixed BLOCKING/SHOULD_FIX from deep review, or "None"]

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Multi-Slice PR Strategy

For features with `totalSlices > 1`:

1. Each slice gets its own PR
2. Slice 1 PR targets the base branch (main)
3. Slice 2+ PRs target the previous slice's branch
4. Mark slice 2+ PRs as **draft** until their parent slice is merged
5. PR title format: `[feature description] (slice N/M)`
6. PR body includes which slice this is, what it delivers independently,
   and its dependency on prior slices

This implements stacked PRs — reviews can happen in parallel with
implementation of subsequent slices.
