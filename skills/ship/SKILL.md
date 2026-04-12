---
name: ship
effort: low
model: sonnet
disable-model-invocation: false
argument-hint: "[story ID or story path]"
description: >
  Use when the user wants to create a pull request from a completed plan execution.
  Triggers on: "ship it", "create a PR", "open a pull request", "push this", "ship
  the plan". Reads the story's plan context to generate a well-structured PR
  description. Not applicable for plan creation (/task-decomposition) or execution
  (/execute).
---

# Ship

Create a pull request from a completed (or in-progress) plan execution. Uses the
story's plan context to generate a structured PR description so the reviewer gets the
full picture without reading the plan files.

## Workflow

### Input Resolution

If `$ARGUMENTS` were provided, resolve the plan context:

1. **Story ID** (matches `story_NNN`) — read the story from
   `~/.claude/backlog-driven-development/artifacts/stories/{id}.json`.
   Read the plan summary from `plan-summaries/plan_NNN.json`.
2. **Story file path** — read the story JSON directly, then look up
   the plan summary by story number.
3. **Legacy plan path** (`.claude/implementation-plans/*.md`) — read as before.
4. **No input** — read `index.json` from
   `~/.claude/backlog-driven-development/artifacts/` and look for stories
   with `status: "IN_PROGRESS"` or `"DONE"`. Confirm with the user.

### Step 1: Gather Context

1. Read the plan summary JSON (or legacy plan.md) — extract "What We Are Building",
   "Why This Exists", Scope (In/Out), and the Completion Summary (if present)
2. Check the plan summary's `status` field:
   - If `Complete`: proceed normally.
   - If `In Progress`: warn the user that execution is not finished. Ask whether
     to proceed with a partial PR or finish execution first with
     `/execute [story ID or path]`.
   - If `Approved` (not yet executed): tell the user to run
     `/execute [story ID or path]` first.
   - If `Draft`: tell the user to run `/task-decomposition [story ID or path]`
     to finalize the plan first.
3. Run `git log --oneline main..HEAD` (or the appropriate base branch) to see all
   commits that will be in the PR
4. Run `git diff --stat main..HEAD` to get the file change summary
5. Check current branch name — if on `main`, ask the user to create a branch first

### Step 2: Choose PR Strategy

Ask the user which strategy they prefer:

- **Single PR** (default): All commits in one PR. Simplest, good for most plans.
- **Grouped PRs**: Split by theme (e.g., backend tasks vs frontend tasks). Good for
  large plans where reviewers have different expertise.
- **Per-task PRs**: One PR per task commit. Maximum granularity but more ceremony.

If the user doesn't have a preference, default to Single PR.

### Step 3: Create PR

1. Push the current branch: `git push -u origin HEAD`
2. Build the PR description from plan context:

```
## Summary

[2-3 sentences from "What We Are Building" + "Why This Exists"]

## Changes

[Bullet list derived from task titles and their Covers: annotations]

## Scope

**In:** [from plan Scope section]
**Out:** [from plan Scope section]

## Test plan

[Derive from plan's Verification Commands and acceptance criteria]
- [ ] All automated tests pass
- [ ] [Manual verification items from Phase 6, if any]

## Plan

[Reference to plan summary artifact or .claude/implementation-plans/{slug}.md if legacy]
```

3. Create the PR: `gh pr create --title "[title]" --body "[description]"`
   - Title: Keep under 70 characters, derived from "What We Are Building"
   - Use a HEREDOC for the body to preserve formatting

4. Return the PR URL to the user.
5. Update the plan summary's status to `shipped` in its JSON file.
6. Present next steps:
   > "PR created: [URL]
   >
   > If this story spans multiple repositories and tasks remain in other repos,
   > run `/execute [story ID or path]` from each repo, then `/ship` again."

### For Grouped or Per-Task PRs

Create branches from the task commits, then create a PR for each group:

1. Identify commit ranges for each group
2. For each group: create a branch, cherry-pick the relevant commits, push, create PR
3. Note dependencies between PRs in the description (e.g., "Depends on #123")
4. Return all PR URLs to the user
