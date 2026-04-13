# Execution State & Resumption

## Execution State Checkpoint

After each task completes, write (or update) a checkpoint file at
`.claude/{features|bugs}/{slug}/execution-state.json`:

```json
{
  "lastCompletedTask": "task_3",
  "branch": "feature/{slug}",
  "baseBranch": "main",
  "dispatchCount": 16,
  "testBaseline": {
    "totalPassing": 142,
    "knownFailures": ["test_flaky_timeout"]
  },
  "consecutiveReviewFailures": 0,
  "timestamp": "2026-04-12T14:30:00Z"
}
```

This file is the single source of truth for resumption — no git log
parsing or commit message matching needed.

## Resumption

If `execution-state.json` exists:

1. Read it to determine the last completed task, branch, dispatch count,
   and test baseline
2. Verify the branch exists and check it out
3. Check `git status` — if there are uncommitted changes from a previous
   session, stash them: `git stash push -m "recovered-uncommitted-work"`.
   Warn the user about the stash.
4. **Run the full test suite** to verify the branch is in a consistent
   state. If tests fail unexpectedly (beyond the known baseline), warn
   the user before resuming.
5. Re-read plan.json constraints (the new session has no memory of them)
6. Present: "Tasks 0-N complete. Tasks N+1 through M remaining. Resuming
   from task N+1."
7. Skip completed tasks and begin from the first incomplete one
8. Restore the dispatch count from the checkpoint (for context gate tracking)

If `execution-state.json` does not exist but task JSONs have `status: "DONE"`:
fall back to verifying against `git log` — search for commits matching
`"Task N:"`. If a task is marked DONE but has no matching commit, reset
its status to `PENDING`.
