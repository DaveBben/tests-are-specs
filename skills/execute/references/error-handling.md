# Error Handling & Plan Deviations

## Hard Stops (report to user immediately)

- **File doesn't exist** that the task says to modify
- **Interface changed** since planning — task context may be stale
- **Task contradicts codebase** — acceptance criteria conflict with reality
- **Tests require unmerged work** — task ordering is wrong (planning error)
- **Test infrastructure missing**

## Soft Stops (adapt and note)

- **Task exceeds 200 lines**: report with count, recommend splitting
- **Slice exceeds 500 lines cumulative**: warn, recommend new slice boundary
- **Task touches undeclared files**: pause, verify all changes serve this
  task's acceptance criteria
- **Minor path differences** (import path changed): adapt and note

## Flagging Plan Issues

1. Note the specific issue and impact
2. Inform user with recommendation
3. Continue if possible, noting deviation in `executionNotes`
