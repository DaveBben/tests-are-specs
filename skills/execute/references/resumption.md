# Execution State & Resumption

## Checkpoint Format

After each task, write/update `.claude/{features|bugs}/{slug}/execution-state.json`:

```json
{
  "lastCompletedTask": "task_3",
  "branch": "feature/{slug}",
  "baseBranch": "main",
  "completedTaskCount": 4,
  "testBaseline": {
    "totalPassing": 142,
    "knownFailures": ["test_flaky_timeout"]
  },
  "consecutiveReviewFailures": 0,
  "timestamp": "2026-04-12T14:30:00Z"
}
```

## Resumption

If `execution-state.json` exists at startup:

1. Read last completed task, branch, and test baseline
2. Verify branch exists and check it out
3. If uncommitted changes: `git stash push -m "recovered-uncommitted-work"`,
   warn user
4. Run full test suite to verify consistent state
5. Re-read plan.json constraints (new session has no memory)
6. Present: "Tasks 0-N complete. Resuming from task N+1."
7. Skip completed tasks, restore completed task count for context gate

If no `execution-state.json` but task JSONs have `status: "DONE"`:
verify against `git log` for `"Task N:"` commits. Reset any DONE task
without a matching commit to PENDING.
