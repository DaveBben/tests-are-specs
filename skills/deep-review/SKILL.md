---
name: deep-review
description: >
  Use when the user explicitly requests a thorough, deep, or comprehensive review of large diffs or changes touching multiple files. Dispatches 4 specialized review agents in parallel (security, reliability, performance on Opus; maintainability on Sonnet for model diversity) and consolidates their findings through evidence auditing, cross-agent validation, and actionability filtering. Do NOT use for general code writing guidance, refactoring advice, or spec/design reviews. For a faster single-agent review, use /cks:check-work instead.
argument-hint: "<base-branch-or-commit>"
effort: high
model: opus
disable-model-invocation: false
---

# Deep Code Review

Perform a thorough, multi-dimensional code review by dispatching 4 specialized review agents in parallel and consolidating their findings into a single report.

## Input

If `$ARGUMENTS` is provided, use it as the base branch or commit to diff against.

If `$ARGUMENTS` is empty, review staged changes (`git diff --cached`). If nothing is staged, diff against the main branch.

## Review Agents

Each agent is an independent specialist that reviews the diff through its own lens. All 4 run in parallel to minimize wall-clock time. Agents use different models to maximize diversity of reasoning — research shows 2 diverse agents can outperform 16 homogeneous ones.

| Agent | Model | Dimensions |
|-------|-------|-----------|
| `security-reviewer` | opus | Injection, access control, CSRF, data exposure, file upload, SSRF, path traversal, XSS, auth/session, misconfiguration, supply chain, rate limiting, subtle attack vectors |
| `reliability-reviewer` | opus | Correctness, logical soundness (off-by-one, null deref, race conditions, boolean logic, state mutation, resource lifecycle, collection mutation, encoding, time/date, closures). Excludes design quality — maintainability-reviewer covers that |
| `performance-reviewer` | opus | N+1 queries, unbounded collections/queues, algorithmic complexity, blocking I/O, sequential awaits, retry storms, lock contention, resource leaks, missing pagination, query inefficiency, chatty I/O |
| `maintainability-reviewer` | sonnet | Backwards compatibility, documentation accuracy, dependency hygiene, consistency with codebase conventions, project doc drift, change amplification. Excludes pure readability/style nitpicks |

## Workflow

### Step 1: Determine the diff base

Determine the base reference for the review:
- If `$ARGUMENTS` provided → use as base branch or commit SHA
- If nothing provided → check for staged changes (`git diff --cached`)
- If nothing staged → diff against the main branch (`main` or `master`)

### Step 2: Build change context

Before dispatching agents, build a brief change context summary:

1. Run `git diff --stat [base]` to get files changed and line counts
2. Read the most recent commit messages on the branch to understand intent
3. Write a 2-3 sentence summary: what changed, why, and what areas are affected

This context is passed to every agent — research shows human-curated context improves review quality by ~4%.

### Step 3: Dispatch all 4 agents in parallel

Launch all 4 review agents simultaneously using the Agent tool. Each agent receives the same base reference AND the change context summary. Send a single message with all 4 Agent tool calls to ensure parallel execution.

**Prompt template for each agent** (substitute the agent's dimension focus):

```
Review the code changes against [base reference], focusing on [dimension focus].
[Base reference] is the base branch or commit to diff against.

Change context: [2-3 sentence summary from Step 2]

For every finding, include a Confidence level (HIGH / MEDIUM / LOW) indicating how
certain you are this is a real issue and not a false positive. HIGH = you traced the
full path and confirmed the issue. MEDIUM = pattern matches but you could not fully
verify. LOW = suspicious but could be intentional or safe.
```

| Agent | Dimension focus for prompt |
|-------|---------------------------|
| `security-reviewer` | security vulnerabilities |
| `reliability-reviewer` | correctness and logical soundness |
| `maintainability-reviewer` | backwards compatibility, documentation accuracy, and maintainability |
| `performance-reviewer` | performance and efficiency |

### Step 4: Consolidate findings

After all 4 agents return their reports, consolidate through 4 sub-steps. Strip agent identity (which agent produced which finding) before evaluating — this prevents majority bias from inflating low-quality findings that happen to appear in multiple agents.

#### 4a. Collect and deduplicate

1. Collect all findings from all agents into a single list
2. Deduplicate on TWO levels:
   - **By file:line** — if multiple agents flag the same location, merge into one finding
     with combined dimension tags (e.g., `[Reliability, Security]`)
   - **By concept** — if multiple agents flag the same logical issue at different line numbers (e.g., both flag "this class does too much"), merge into one finding at the most relevant location
3. For merged findings: keep the highest severity, preserve the most detailed description, note agreement count (e.g., `[2/4 agents]`)

#### 4b. Audit evidence quality

For each finding, evaluate the reasoning — not just the conclusion:

- **Does it include a trace?** A finding that says "SQL injection at line 42" without showing the data flow from user input to the query is unsubstantiated. Downgrade or drop.
- **Is the evidence specific?** "This could be slow" is noise. "This is O(n²) because of the nested loop at lines 15-22, processing the `orders` collection which grows unbounded" is signal.
- **Does it contradict another agent's context?** If the security reviewer flags a function as vulnerable but the reliability reviewer's analysis shows the input is already validated upstream, resolve the conflict. Drop the finding if the contradiction is clear; flag it with a note if ambiguous.

#### 4c. Filter for actionability

Challenge each surviving finding against these criteria:

- **Is it specific enough to act on?** A developer should know exactly what to change. Drop findings that are vague observations without a concrete fix.
- **Is the confidence level reasonable for the severity?** A BLOCKING finding with LOW confidence should be downgraded to SHOULD_FIX or dropped. A SUGGESTION with HIGH confidence can stay as-is.
- **Would a developer act on this?** Findings that are technically correct but low-value (style nitpicks, theoretical edge cases in cold paths) erode trust. When in doubt, drop.

If aggressive filtering leaves fewer than expected findings, that is a GOOD outcome. An empty report with high trust is better than a noisy report that gets ignored.

#### 4d. Sort and compute verdict

1. Sort by severity: BLOCKING first, then SHOULD_FIX, then SUGGESTIONS
2. Compute verdict:
   - Any BLOCKING → REQUEST CHANGES
   - Only SHOULD_FIX → REQUEST CHANGES
   - Only SUGGESTIONS or clean → APPROVE

### Step 5: Produce the consolidated report

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

- `file:line` — **[Dimension]** (Confidence: HIGH) [Description]. Trace: [data flow or
  logic path]. Fix: [suggestion]

## SHOULD_FIX

- `file:line` — **[Dimension]** (Confidence: HIGH/MEDIUM) [Description]. Trace: [data flow
  or logic path]. Fix: [suggestion]

## SUGGESTIONS

- `file:line` — **[Dimension]** (Confidence: MEDIUM/LOW) [Suggestion with rationale]

## Verdict

**[APPROVE | REQUEST CHANGES]** — [One sentence explanation]

### Action Items

1. [One-line summary of each BLOCKING and SHOULD_FIX item]
```

If a severity section has no findings, omit it. A clean review with 0 findings is a valid outcome — do not manufacture findings to fill the template.

## Principles

- **Every finding needs a fix.** Show the concrete change, not just the problem.
- **Every finding needs a trace.** Show the reasoning path (data flow, logic chain, or evidence) that led to the conclusion. Unsubstantiated findings get dropped.
- **Severity must be honest.** BLOCKING means "this will cause a real problem in production." Do not inflate to get attention or deflate to be polite.
- **False positives erode trust faster than false negatives.** Research shows developers ignore ALL AI feedback once false positive rates exceed ~70%. When in doubt, drop the finding. A clean report that developers trust is worth more than a thorough report they ignore.
- **The aggregator is the most consequential step.** Collecting and sorting is not enough. The consolidation step must actively audit reasoning quality, resolve cross-agent contradictions, and filter for actionability.
- **Adapt depth to change size.** A 5-line hotfix gets a quick pass. A 500-line feature gets the full treatment.
- **Empty sections are fine.** Do not manufacture findings to fill a template. A clean review with 0 findings is a valid and common outcome.
