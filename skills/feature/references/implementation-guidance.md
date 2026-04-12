# During Implementation

Reference guidance for when the user runs implementation, either via
`/execute` or manually using the implementation command from tasks.md.
These are not phases the `/feature` skill executes — they are patterns
for effective execution.

---

## Corrections Must Be Terse

One sentence. The AI has the full plan and session context.

- "You didn't implement deduplicateByTitle."
- "That belongs in the admin app, not the main app — move it."
- "Wrong — use PATCH, not PUT."

Long explanations during execution pollute the implementation context.

## Revert and Re-scope, Don't Patch

When something goes in the wrong direction, discard the git changes and
re-scope:

> "I reverted everything. Now all I want is X — nothing else."

Narrowing scope after a revert consistently produces better results than
incrementally fixing a bad approach.

## Protect Interfaces Explicitly

> "The signatures of these three functions must not change — the caller
> should adapt, not the library."

The AI will change interfaces unless explicitly told not to.

## Reference Existing Code Instead of Describing Design

> "This table should look exactly like the users table — same header,
> same pagination, same row density."

Pointing at a reference communicates all the implicit requirements without
spelling them out.

## Right-Sizing During Execution

### One Change at a Time

Each task is one code change. Each slice is one reviewable PR. If you find
yourself needing to explain two unrelated things in a commit message, the
task was too broad.

### The Working State Rule

After every task commit, run tests. If they fail because a future task hasn't
been implemented yet, that's a planning error — report it immediately rather
than pressing forward. Working software after every commit is non-negotiable.

### When a Slice Is Growing Too Large

If the cumulative diff for the current slice passes 500 lines, tell the user.
They may want to:
1. Continue (the remaining tasks are small)
2. Draw a new slice boundary here and PR what's done
3. Revisit the plan

Don't silently produce a 1500-line PR.
