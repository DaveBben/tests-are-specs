---
name: deep-review
description: >
  Use when the user explicitly requests a thorough, deep, or comprehensive review of large diffs or changes touching multiple files. Dispatches 4 specialized Opus review agents in parallel (security, reliability, maintainability, performance) and consolidates their findings into a unified report with a verdict. Do NOT use for general code writing guidance, refactoring advice, or spec/design reviews. For a faster single-agent review, use /light-review instead.
argument-hint: "<base-branch-or-commit>"
effort: high
model: opus
disable-model-invocation: true
---

# Deep Code Review

Perform a thorough, multi-dimensional code review by dispatching 4 specialized review agents
in parallel and consolidating their findings into a single report.

## Input

If `$ARGUMENTS` is provided, use it as the base branch or commit to diff against.

If `$ARGUMENTS` is empty, review staged changes (`git diff --cached`). If nothing is staged,
diff against the main branch.

## Review Agents

Each agent is an independent specialist that reviews the diff through its own lens. All 4
run in parallel to minimize wall-clock time.

| Agent | Dimensions |
|-------|-----------|
| `security-reviewer` | Injection, access control, CSRF, data exposure, file upload, SSRF, path traversal, XSS, auth/session, misconfiguration, supply chain, rate limiting, subtle attack vectors |
| `reliability-reviewer` | Correctness, logical soundness, design quality (off-by-one, null deref, race conditions, boolean logic, state mutation, resource lifecycle, collection mutation, encoding, time/date, closures, abstraction quality) |
| `maintainability-reviewer` | Readability, backwards compatibility, dependency hygiene, consistency with codebase conventions, documentation accuracy, stale comments, missing API contracts, project doc drift, change amplification, code clones |
| `performance-reviewer` | N+1 queries, unbounded collections/queues, algorithmic complexity, blocking I/O, sequential awaits, retry storms, lock contention, resource leaks, missing pagination, query inefficiency, chatty I/O |

## Workflow

### Step 1: Determine the diff base

Determine the base reference for the review:
- If `$ARGUMENTS` provided → use as base branch or commit SHA
- If nothing provided → check for staged changes (`git diff --cached`)
- If nothing staged → diff against the main branch (`main` or `master`)

### Step 2: Dispatch all 4 agents in parallel

Launch all 4 review agents simultaneously using the Agent tool. Each agent receives the same
base reference so they all review the same diff. Send a single message with all 4 Agent tool
calls to ensure parallel execution.

**Prompt template for each agent** (substitute the agent's dimension focus):

| Agent | Dimension focus for prompt |
|-------|---------------------------|
| `security-reviewer` | security concerns |
| `reliability-reviewer` | reliability and correctness |
| `maintainability-reviewer` | maintainability and readability |
| `performance-reviewer` | performance and efficiency |

```
Review the code changes against [base reference], focusing on [dimension focus].
[Base reference] is the base branch or commit to diff against.
```

### Step 3: Consolidate findings

After all 4 agents return their reports:

1. **Collect** all findings from all 4 agents into a single list
2. **Deduplicate** by file:line — if multiple agents flag the same location:
   - Keep the highest-severity finding
   - Merge dimension tags (e.g., `[Reliability, Security]`)
   - Preserve the most detailed description
3. **Sort** by severity: BLOCKING first, then SHOULD_FIX, then SUGGESTIONS
4. **Compute verdict:**
   - Any BLOCKING → REQUEST CHANGES
   - Only SHOULD_FIX → REQUEST CHANGES
   - Only SUGGESTIONS or clean → APPROVE

### Step 4: Produce the consolidated report

Follow this format:

```markdown
# Deep Code Review

## Summary

- **Files changed**: X files (+Y/-Z lines)
- **Change type**: [Feature | Bug Fix | Refactor | Enhancement]
- **Scope**: [1-2 sentence description of what changed and why]
- **Agents dispatched**: security-reviewer, reliability-reviewer, maintainability-reviewer,
  performance-reviewer

## BLOCKING

- `file:line` — **[Dimension]** [Description]. Fix: [suggestion]

## SHOULD_FIX

- `file:line` — **[Dimension]** [Description]. Fix: [suggestion]

## SUGGESTIONS

- `file:line` — **[Dimension]** [Suggestion with rationale]

## Verdict

**[APPROVE | REQUEST CHANGES]** — [One sentence explanation]

### Action Items

1. [One-line summary of each BLOCKING and SHOULD_FIX item]
```

If a severity section has no findings, omit it. A clean review with 0 findings is a valid
outcome — do not manufacture findings to fill the template.

## Principles

- **Every finding needs a fix.** Show the concrete change, not just the problem.
- **Severity must be honest.** BLOCKING means "this will cause a real problem in production."
  Do not inflate to get attention or deflate to be polite.
- **False positives erode trust.** If an agent flags something that another agent's context
  reveals is safe, drop it during consolidation.
- **Adapt depth to change size.** A 5-line hotfix gets a quick pass. A 500-line feature gets
  the full treatment.
- **Empty sections are fine.** Do not manufacture findings to fill a template.
