# Error Handling & Plan Deviations

## When the Plan Is Wrong

- **File doesn't exist**: STOP. Report to user.
- **Interface changed**: STOP. Task context may need updating.
- **Test infrastructure missing**: Report. User decides how to proceed.
- **Task too large** (>200 lines changed): Report with line count. Recommend
  splitting. User decides.
- **Slice too large** (>500 lines cumulative): Warn. Recommend creating a
  new slice boundary at the current task. User decides.
- **Task touches files beyond what it declares**: Pause. Verify all changes
  are necessary for this task's acceptance criteria. If any changes serve a
  different concern, the task should have been split during planning.
- **Tests require unmerged work**: If the current task's tests cannot pass
  without uncommitted changes from a future task, the task ordering or
  boundaries are wrong. STOP and report — this indicates a planning error.
- **Task contradiction**: STOP. Back to `/cks:feature` or `/cks:bug` for revision.

For minor deviations (slightly different import path), adapt and note. For
scope or acceptance criteria changes, stop.

## Flagging Upstream Artifacts for Revision

During execution, if you discover that the plan is inadequate:

1. Note the specific issue and impact
2. Inform the user with a recommendation
3. Continue execution if possible, noting the deviation
