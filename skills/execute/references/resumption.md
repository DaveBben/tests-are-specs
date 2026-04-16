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
  "executionNotes": {
    "task_2": ["High turn count — possible drift (42/50 turns)"],
    "task_3": ["Handoff check BLOCKED for task_4: missing export 'Config'"]
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
6. Restore `executionNotes` — if any pending task has a note (e.g.
   handoff BLOCKED), surface it to the user before resuming that task
7. Present: "Tasks 0-N complete. Resuming from task N+1."
   Include any executionNotes for the next task.
8. Skip completed tasks, restore completed task count for context gate

If no `execution-state.json` but task JSONs have `status: "DONE"`:
check `git log --oneline` for `task_{N}:` commit messages.

- If matching commits exist: reconstruct state from the highest
  committed task number, verify branch, run test suite, and resume
  from the next task.
- If no matching commits exist: the DONE statuses are unreliable.
  Reset all DONE tasks to PENDING and re-run from the beginning.
