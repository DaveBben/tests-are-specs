---
name: light-review
description: >
  Use proactively when the user requests a review of their code changes. Launches a single-agent code review covering security, reliability, performance, and maintainability in one pass. Appropriate for any code change — cost-efficient alternative to /deep-review. For a thorough 4-agent Opus review, use /deep-review instead. Do NOT use for reviewing existing code without a diff context.
argument-hint: "<base-branch-or-commit>"
effort: medium
disable-model-invocation: false
---

# Fast Code Review

Dispatch a single `generic-code-reviewer` agent using the Agent tool to perform a rapid review of
code changes. Covers all four review dimensions in one pass, focusing only on findings that must
be fixed.

## Input

If `$ARGUMENTS` is provided, use it as the base branch or commit to diff against.

If `$ARGUMENTS` is empty, review staged changes (`git diff --cached`). If nothing is staged,
diff against the main branch.

## Workflow

1. Launch a single `generic-code-reviewer` agent using the Agent tool with:
   ```
   Review the code changes against [base reference]. [Base reference] is the base branch
   or commit to diff against.
   ```
2. Return the agent's report directly — no consolidation needed (single agent)
