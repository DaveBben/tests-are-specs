---
name: triage
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[bug ID (bug_NNN) or bug file path]"
allowed-tools:
  - Agent
  - Skill
  - TodoWrite
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
description: >
  Systematic debugging skill. Takes a bug card and walks through reproduction,
  root cause analysis, failing test, fix implementation, verification, and
  cleanup. This is the execution path for bugs — the equivalent of
  /task-decomposition + /execute combined for bug fixes.
  Do NOT use for creating bug reports (use /bug).
  Do NOT use for feature implementation (use /task-decomposition + /execute).
---

# Bug Triage and Fix

> Takes a bug card from the artifact store and walks through a systematic
> debugging process: reproduce, investigate, isolate, test, fix, verify,
> and ship. Expect 20-60 minutes depending on complexity.

This skill is the **execution path for bugs**. Where stories go through
`/task-decomposition` → `/execute`, bugs go through `/bug` → `/triage`.
The debugging methodology IS the task decomposition — the 12 phases below
replace formal task planning with a disciplined investigation workflow.

**Why a separate path from `/execute`?** Bug fixes follow a fundamentally
different workflow than feature implementation. Features start with known
requirements and decompose into parallel tasks. Bugs start with a symptom
and require investigation before you even know what to change. Forcing bugs
through the feature pipeline adds overhead without value.

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **Bug ID** (matches `bug_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/bugs/{id}.json`.
   Proceed to Phase 0.
2. **Bug file path** (points to an existing artifact JSON file):
   Read the bug from the file. Proceed to Phase 0.
3. **No input or unrecognized**: Ask the user for a bug ID.

This skill does NOT accept plain text descriptions. If the user describes a
bug without a card, tell them: "This skill works with bug cards. Use `/bug`
to create one first, then `/triage` to investigate and fix it."

### Resumption

If the bug's status is `IN_PROGRESS`:

1. Check `git branch` — look for an existing `bugfix/{bug-slug}` branch
2. Check `git log` on that branch for existing commits (failing test, fix)
3. Present the current state:
   > "This bug is already in triage. Current state:
   > - Branch: `bugfix/{bug-slug}`
   > - Commits: [list commits on branch]
   >
   > Would you like to continue from where you left off?"
4. Resume at the appropriate phase based on what's been done

---

## Phase 0: Pre-flight

### Step 1: Read and Present the Bug Card

Read the full bug card from the artifact store. Present it to the user:

> "Bug `{id}`: {title}
>
> **Severity:** {severity}
> **Symptom:** {symptom}
> **Steps to Reproduce:** {steps summary}
>
> I'll now investigate and fix this bug. Here's my approach:
>
> 1. Reproduce the bug
> 2. Investigate and isolate the root cause
> 3. Write a failing test
> 4. Implement the minimal fix
> 5. Verify and ship
>
> Let's start."

### Step 2: Check Bug Status

- If `status` is `TODO`: Proceed.
- If `status` is `BACKLOG`: Warn:
  > "This bug hasn't been reviewed yet. Run `/bug {id}` to finalize the
  > card first. Proceed anyway?"
- If `status` is `DONE`: Warn:
  > "This bug is already marked as resolved. Are you re-investigating it?"
- If `status` is `NEEDS_REFINEMENT`: Present the revision reason and warn:
  > "This bug was flagged for revision: {revisionReason}. Consider running
  > `/bug {id}` to address the revision first. Proceed anyway?"

### Step 3: Discover Repositories

Read the bug's `targetRepositories` field. For each repository:

1. Verify the local directory exists
2. If not found, ask the user for the correct path
3. Check `git status` — warn about uncommitted changes
4. Record the base branch

### Step 4: Create Branch

For the primary repository:

```
git checkout -b bugfix/{bug-slug}
```

If the branch already exists (resumption), check it out instead.

### Step 5: Set Status

Update the bug's `status` to `in-triage` in both the bug JSON file and
`index.json`. Update `lastModified`.

---

## Phase 1: Reproduce the Bug

> **Principle: Understand the bug before touching anything.**
> A bug you can't reproduce consistently is much harder to fix.

### Step 1: Follow the Steps to Reproduce

Read the bug card's `stepsToReproduce` field and follow the steps literally
in the target repository. Use the environment details from the bug card.

If the reproduction involves running the application:
- Check if the required environment matches (OS, versions, config)
- Note any differences between the bug reporter's setup and the current one

### Step 2: Confirm Reproducibility

**If reproducible:**

> "Bug confirmed. I can reproduce the issue by following the steps in the
> bug card. [Describe what you observed]."

Proceed to Phase 2.

**If NOT reproducible:**

Do NOT skip ahead. Investigate why:

1. Check environment differences — is the local setup different from where
   the bug was reported?
2. Check if the code has changed since the bug was filed — has someone
   already partially fixed it?
3. Ask the user for more context:
   > "I cannot reproduce this bug with the steps provided. Here's what I
   > tried: [steps]. The behavior I see is: [what happened].
   >
   > Possible reasons:
   > - Environment difference: [specific difference]
   > - Code may have changed since the bug was filed
   > - Steps may be incomplete
   >
   > Can you provide more detail about the conditions when you saw this?"

4. If the user provides new information, retry reproduction
5. If still not reproducible after two attempts, ask the user to decide:
   > "I've been unable to reproduce this bug after two attempts. Would you like to:
   > 1. **Investigate anyway** — I'll analyze the code path for potential issues
   > 2. **Update the bug card** — add more reproduction detail via `/bug {id}`
   > 3. **Close as unreproducible** — mark the bug with a note"

---

## Phase 2: Understand Expected vs Actual Behavior

> **Principle: Check your assumptions.**
> Many bugs come from incorrect assumptions about data types, ranges,
> ordering, or state.

### Step 1: Confirm Expected Behavior

Read the bug card's `expectedBehavior`. Verify this is correct by checking:
- The feature's specification or acceptance criteria (if available)
- The code's intent (read function names, comments, tests)
- Ask the user if anything is ambiguous

### Step 2: Document Actual Behavior

Observe the actual behavior firsthand during reproduction. Note:
- Exact error messages (copy them verbatim)
- Stack traces
- Return values or HTTP status codes
- Visual state (if applicable)
- Timing (does it happen immediately? After a delay?)

### Step 3: Note Discrepancies

If the actual behavior you observe differs from what the bug card says:

> "Note: the bug card says [X], but I'm seeing [Y]. This may be a slightly
> different manifestation or the behavior may have changed. I'll investigate
> both."

---

## Phase 3: Gather Information

> **Principle: Read the code you're about to change.**
> Before editing, understand what the surrounding code is doing. Bugs are
> often introduced by changes that break an assumption the original code
> relied on.

### Step 1: Read Error Messages and Logs

- Check application logs for errors, warnings, or unexpected entries
- Read stack traces to identify the call chain
- Note timestamps and sequence of events

### Step 2: Trace the Code Path

Using the reproduction steps as a guide, trace through the codebase:

1. Identify the **entry point** — what function or handler receives the
   user's action?
2. Follow the code path from entry to the point where behavior diverges
   from expected
3. Read every function in the chain, not just the one you think is broken
4. Note the **data flow** — what values are passed, transformed, stored?

Use Grep and Read to search the codebase. Use Explore agents for complex
codebases with multiple modules.

### Step 3: Check Recent Changes

```
git log --oneline -20 -- [affected files]
```

Look for recent changes that might have introduced the bug. This gives
context, not blame.

### Step 4: Search for Related Code

Search for other code that:
- Calls the same functions
- Uses the same data structures
- Makes the same assumptions

This helps you understand if the fix will have ripple effects.

---

## Phase 4: Form a Hypothesis

> **Principle: Find the root cause, not just the symptom.**
> Fixing a surface symptom often masks the real problem. Ask "why"
> repeatedly (the "5 Whys" technique) until you reach the underlying cause.

### Step 1: State Your Hypothesis

Based on what you've gathered, formulate a hypothesis:

> "Based on my investigation, I believe the root cause is:
>
> **[Specific technical explanation]**
>
> Evidence:
> - [Evidence 1 — e.g., 'The function at file:line uses X but should use Y']
> - [Evidence 2 — e.g., 'The log shows Z happening before W']
>
> Does this match your understanding?"

### Step 2: Apply the 5 Whys

Don't stop at the first "why":

1. **Why** does stale text display? → The cached transcription is served
2. **Why** is the cached version served? → The dedup check uses file path only
3. **Why** doesn't it check the content hash? → The original design assumed
   file paths are unique forever
4. **Why** was that assumed? → Voice memos weren't expected to be re-recorded
   at the same path
5. **Root cause**: The state tracker's deduplication logic doesn't account for
   file content changes at existing paths

The root cause is often 2-3 levels deeper than the surface symptom.

### Step 3: Validate the Hypothesis

Before proceeding to fix, verify the hypothesis is consistent with ALL
observed behavior:
- Does it explain why the bug happens under the reported conditions?
- Does it explain why it DOESN'T happen under other conditions?
- Are there any observations that contradict this hypothesis?

If contradictions exist, return to Phase 3 with new questions.

---

## Phase 5: Isolate the Root Cause

> **Principle: Isolate the problem.**
> Narrow down where the bug lives before trying to fix it. Use a
> divide-and-conquer approach.

### Step 1: Narrow to Specific Code

From your hypothesis, identify:
- The **exact file(s)** containing the bug
- The **exact function(s)** or code block(s) responsible
- The **exact line(s)** where behavior diverges from expected

Read these files carefully. Understand not just what the code does, but
what it was intended to do.

### Step 2: Verify the Isolation

Confirm that the identified code is actually the source:
- Add mental trace points: if this line does X, then the observed behavior
  follows logically
- Check if there are other code paths that could produce the same symptom
- Verify there isn't a second bug masking or compounding the first

### Step 3: If the Hypothesis Is Wrong

If the isolated code doesn't match your hypothesis:

> "My initial hypothesis was wrong. The code at [location] actually does [X],
> not what I expected. Returning to investigation with new information:
> [what I learned]."

Return to Phase 3 with the new information. This is normal — debugging is
iterative. Do NOT try to force-fit a fix based on a wrong hypothesis.

---

## Phase 6: Write a Failing Test

> **Principle: Write a failing test first.**
> Before fixing the bug, write a test that reproduces it. This confirms
> you've found the right spot and gives you a safety net.

### Step 1: Design the Test

Write a test that:
- Sets up the preconditions from the bug's reproduction steps
- Performs the action that triggers the bug
- Asserts the **expected** behavior (which will fail, proving the bug exists)

The test name should reference the bug: `test_bug_NNN_[symptom_description]`

### Step 2: Write and Run the Test

Write the test using the project's existing test framework and conventions.

Run the test to confirm it **fails** (RED state):

> "Failing test written and confirmed RED:
> - Test: `test_bug_001_stale_transcription_after_rerecord`
> - Expected: [expected behavior]
> - Actual: [bug behavior]
> - This confirms the bug exists at the location I identified."

### Step 3: Commit the Failing Test

```
git add [test file]
git commit -m "Add failing test for bug_NNN: [symptom title]"
```

### Step 4: Run /check

Run `/check` on the commit. Fix any BLOCKING or SHOULD_FIX findings, then
commit fixes.

---

## Phase 7: Implement the Fix

> **Principle: Make one change at a time.**
> Avoid fixing multiple things simultaneously. Make the smallest possible
> change that addresses the root cause.

### Step 1: Plan the Minimal Fix

Identify the smallest change that:
- Addresses the root cause (not just the symptom)
- Doesn't break existing behavior
- Follows the codebase's existing patterns and conventions

> "The fix I propose:
>
> **File:** [path]
> **Change:** [description of the change]
> **Why this is minimal:** [why not a larger refactor]"

### Step 2: Implement

Make the change. Resist the temptation to:
- Refactor surrounding code
- Fix unrelated issues you noticed
- Add features or improvements
- "Clean up while you're in there"

Those are separate work items. Stay focused on the bug.

### Step 3: Run the Failing Test

Run the test from Phase 6 to confirm it now **passes** (GREEN state):

> "Fix implemented and confirmed GREEN:
> - Test: `test_bug_001_stale_transcription_after_rerecord`
> - Previously: FAIL (stale text returned)
> - Now: PASS (new transcription returned)"

---

## Phase 8: Verify the Fix

> **Principle: Verify thoroughly.**
> Run the full test suite to make sure nothing else broke.

### Step 1: Run Full Test Suite

Run the project's complete test suite:

```
[project test command]
```

If any tests fail that weren't failing before your change:
- Investigate whether your fix broke them
- If yes: adjust the fix to not break existing behavior
- If no (pre-existing failure): note it but don't fix it in this branch

### Step 2: Manual Verification

Re-run the bug's reproduction steps manually to confirm the fix works
end-to-end, not just in the unit test.

> "Manual verification:
> 1. [Step] — [result]
> 2. [Step] — [result]
> 3. [Step] — Bug is fixed: [what I now see]"

### Step 3: Commit the Fix

```
git add [changed files]
git commit -m "Fix bug_NNN: [symptom title]

[1-2 sentence explanation of root cause and fix]"
```

### Step 4: Run /check

Run `/check` on the commit. Fix any BLOCKING or SHOULD_FIX findings.

---

## Phase 9: Test Edge Cases

> **Principle: Go beyond the automated tests.**
> Try boundary values, unexpected inputs, and related features that might
> be affected by your change.

### Step 1: Identify Related Edge Cases

Based on the root cause, think about:
- What other inputs or conditions exercise the same code path?
- What boundary values might trigger similar behavior?
- What related features depend on the same logic?

Identify 2-3 specific edge cases to verify.

### Step 2: Test Each Edge Case

For each edge case:
1. Test it manually or write an automated test
2. Confirm correct behavior
3. If a new bug is found: add a test, fix it if trivial (same root cause),
   or create a new bug card via `/bug` if it's a separate issue

### Step 3: Add Missing Tests

If any edge cases lack test coverage:

```
git add [test files]
git commit -m "Add edge case tests for bug_NNN fix"
```

---

## Phase 10: Review and Clean Up

> **Principle: Re-read your changes with fresh eyes.**
> Remove any debug statements or temporary code you added during investigation.

### Step 1: Self-Review

Read through all changes on the branch:

```
git diff main...HEAD
```

Check for:
- Debug statements (`console.log`, `print`, `debugger`)
- Temporary code or commented-out blocks
- TODO comments that should be addressed now
- Code that doesn't match the codebase's style

Remove anything that shouldn't be in the final commit.

### Step 2: Run /deep-review

Run `/deep-review` on the full branch (diff from base branch).

For BLOCKING or SHOULD_FIX findings:
1. Fix the issues
2. Commit: `"Address review findings for bug_NNN"`
3. If BLOCKING findings existed, run `/deep-review` one more time (single
   retry, not a loop)

---

## Phase 11: Document and Commit

> **Principle: Write a clear commit message explaining what the bug was
> and how you fixed it.**

### Step 1: Update the Bug Card

Update the bug's JSON file with the resolution:

```json
{
  "resolution": {
    "rootCause": "[1-2 sentence explanation of the root cause]",
    "fix": "[1-2 sentence explanation of what was changed]",
    "testsAdded": [
      "[test name and what it covers]"
    ],
    "resolvedAt": "2026-04-11",
    "branch": "bugfix/{bug-slug}",
    "pr": null
  }
}
```

### Step 2: Update Bug Status

Update the bug's `status` to `resolved` in both:
- The bug JSON file (`artifacts/bugs/{id}.json`)
- `index.json` (the entry in the `bugs` array)

Update `lastModified` in `index.json`.

### Step 3: Push and Create PR

```
git push -u origin bugfix/{bug-slug}
```

If `gh` CLI is available, create a PR:

```
gh pr create --title "Fix bug_NNN: [symptom title]" --body "$(cat <<'EOF'
## Bug

**ID:** bug_NNN
**Severity:** [severity]
**Symptom:** [symptom]

## Root Cause

[1-2 sentence explanation]

## Fix

[1-2 sentence explanation of what was changed]

## Test Plan

- [x] Failing test reproduces the bug (RED before fix)
- [x] Fix makes the test pass (GREEN after fix)
- [x] Full test suite passes
- [x] Manual reproduction confirms fix
- [ ] [Additional edge case tests if applicable]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Update the bug card's `resolution.pr` field with the PR URL.

---

## Phase 12: Post-deployment Monitoring Guidance

> **Principle: Monitor after deployment.**
> Once the fix is live, watch logs and error reports to confirm the bug is
> truly gone.

This phase is advisory — present recommendations to the user, don't automate
monitoring.

> "The fix is ready for review. After the PR is merged and deployed:
>
> **Watch for:**
> - [Specific log entry or metric that would indicate the bug is recurring]
> - [Related error patterns that might surface]
>
> **Verify in production:**
> - [Specific action to confirm the fix works in the deployed environment]
>
> **If the bug recurs:**
> - The failing test will catch regressions in CI
> - If it manifests differently, create a new bug card via `/bug`"

Present the final summary:

> "Bug `{id}` triage complete:
> - **Branch:** `bugfix/{bug-slug}`
> - **PR:** [URL]
> - **Root cause:** [1 sentence]
> - **Fix:** [1 sentence]
> - **Tests added:** [count]
>
> Review and merge the PR to close this bug."

---

## Best Practices Reference

These principles are embedded throughout the phases above. They're collected
here as a quick reference for the debugging mindset.

### Understand Before Touching (Phases 1-2)

Reproduce the bug reliably first. Read error messages carefully — they often
tell you exactly what went wrong and where. Don't start editing code until
you can trigger the bug on demand.

### Isolate the Problem (Phase 5)

Narrow down where the bug lives before trying to fix it. Use a
divide-and-conquer approach: add logging, use a debugger, trace the call
chain. The goal is to find the exact line or logic responsible.

### Find the Root Cause, Not the Symptom (Phase 4)

Fixing a surface symptom often masks the real problem. Ask "why" repeatedly
until you reach the underlying cause. A null pointer crash might really be
a missing validation step upstream.

### Read the Code You're About to Change (Phase 3)

Before editing, understand what the surrounding code is doing. Bugs are
often introduced by changes that break an assumption the original code
relied on. Know those assumptions before you change anything.

### Make One Change at a Time (Phase 7)

Avoid fixing multiple things simultaneously. If you change several things
and the bug disappears (or a new one appears), you won't know which change
caused it. Keep the fix minimal and focused.

### Write a Failing Test First (Phase 6)

Before fixing the bug, write a test that reproduces it. This confirms you
understand the problem and ensures the bug won't silently come back later
as a regression.

### Check Your Assumptions (Phase 2)

Many bugs come from incorrect assumptions about data types, ranges, ordering,
or state. Verify what you think is true actually is. Print the actual values.
Read the actual code. Don't trust your mental model — trust the evidence.

---

## When to Escalate

Some situations require stopping and consulting the user rather than
continuing autonomously:

- **Security vulnerability discovered**: If the bug reveals a security issue
  beyond the original symptom, flag it immediately
- **Data corruption risk**: If the fix could affect stored data integrity
- **Root cause is in a dependency**: If the bug is in a library or external
  service you don't control
- **Multiple bugs interacting**: If you discover the symptom is caused by
  two or more independent bugs
- **Fix requires breaking changes**: If the minimal fix would change a public
  API or data format

> "I've discovered something that changes the scope of this investigation:
> [explanation]. This needs your input before I proceed."

---

## Pipeline

```
Bug card (/bug)
    |
/triage (this skill)
    |
    ├── Phase 0: Pre-flight (read bug, create branch)
    ├── Phase 1: Reproduce (confirm the bug)
    ├── Phase 2: Understand (expected vs actual)
    ├── Phase 3: Gather (logs, traces, code paths)
    ├── Phase 4: Hypothesize (5 Whys, root cause theory)
    ├── Phase 5: Isolate (narrow to exact code)
    ├── Phase 6: Failing test (RED) + /check
    ├── Phase 7: Fix (minimal change, GREEN)
    ├── Phase 8: Verify (full suite + manual) + /check
    ├── Phase 9: Edge cases (related scenarios)
    ├── Phase 10: Review (/deep-review) + cleanup
    ├── Phase 11: Document (update bug card, PR)
    └── Phase 12: Monitor (advisory)
    |
Complete (bug resolved, PR ready for review)
```
