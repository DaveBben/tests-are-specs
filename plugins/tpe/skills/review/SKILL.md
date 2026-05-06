---
name: review
description: >
  Use when the user explicitly requests a thorough, deep, or comprehensive review of large diffs or changes touching multiple files. Dispatches 4 specialized review agents in parallel (security, reliability, performance, maintainability) and consolidates their findings through evidence auditing, cross-agent validation, and actionability filtering. Do NOT use for general code writing guidance, refactoring advice, or spec/design reviews. For a faster single-agent review, use vanilla Claude Code with plan mode instead.
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

Each agent is an independent specialist that reviews the diff through its own lens. All 4 run in parallel to minimize wall-clock time.

Each agent name in the table below corresponds to an agent definition file in `plugins/tpe/agents/` (e.g., `security-reviewer` → `plugins/tpe/agents/security-reviewer.md`). When dispatching, use the agent name as the `subagent_type` parameter of the Agent tool.

| Agent | Model | Dimensions |
|-------|-------|-----------|
| `security-reviewer` | opus | Injection, access control, CSRF, data exposure, file upload, SSRF, path traversal, XSS, auth/session, misconfiguration, supply chain, rate limiting, subtle attack vectors |
| `reliability-reviewer` | opus | Correctness, logical soundness (off-by-one, null deref, race conditions, boolean logic, state mutation, resource lifecycle, collection mutation, encoding, time/date, closures). Excludes design quality — maintainability-reviewer covers that |
| `performance-reviewer` | opus | N+1 queries, unbounded collections/queues, algorithmic complexity, blocking I/O, sequential awaits, retry storms, lock contention, resource leaks, missing pagination, query inefficiency, chatty I/O |
| `maintainability-reviewer` | opus | Backwards compatibility, documentation accuracy, dependency hygiene, consistency with codebase conventions, project doc drift, change amplification. Excludes pure readability/style nitpicks |

## Workflow

### Step 1: Determine the diff base

Determine the base reference for the review:
- If `$ARGUMENTS` provided → use as base branch or commit SHA
- If nothing provided → check for staged changes (`git diff --cached`)
- If nothing staged → diff against the default branch. Determine it via `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'`, falling back to `main` then `master` if that fails.

### Step 2: Build change context

Before dispatching agents, gather context centrally so each subagent does not re-fetch the same material. This buys back turns inside the subagents for actual review work.

1. Run `git diff --stat [base]` to get files changed and line counts
2. Run `git diff [base]` to capture the full diff. Save the output — it will be embedded in each agent's prompt. If the diff is very large (>2000 lines) and embedding it inline would dominate the prompt, fall back to passing only the file list and let the subagents fetch the diff themselves.
3. Read the most recent commit messages on the branch to understand intent
4. **Build a documentation map** for the maintainability reviewer: list candidate doc files at common locations — `find . -maxdepth 4 \( -name "*.md" -o -name ".env.example" -o -name "openapi.*" -o -name "swagger.*" \) -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./vendor/*"`. Capture this list (paths only, not contents).
5. **Classify the change** as exactly one of: **Feature** | **Bug Fix** | **Refactor** | **Enhancement**. This classification anchors the actionability filter in Step 4c — pick one, don't hedge.
6. **Look for artifact intent** — these paths are specific to projects using the TPE workflow; if the directories do not exist, skip this sub-step. Check `.claude/features/*/brainstorm.md` and `.claude/bugs/*/tasks/task_*.json` for context relevant to this branch or change. If found:
   - From `brainstorm.md`: extract the "What" and "Why" sections (the human-approved intent, not the full investigation)
   - From `task_{N}.json` files: extract the `intent` field from each task (one sentence per task describing why it exists)
   - Use this to distinguish deliberate decisions from accidental ones — a reviewer seeing a pattern deviation needs to know if it was intentional
   - **Do not inject** the full plan, implementation rationale, or chosen approach justification — this risks anchoring reviewers to the implementor's reasoning rather than providing independent review
7. Write a 2-3 sentence summary: what changed, why, and what areas are affected. Append any artifact intent as a brief "Intent context" note (1-2 sentences max).

Record the change type, summary, intent context, full diff, and doc map — they are passed to the agents in Step 3 (the diff goes to all four; the doc map goes only to the maintainability reviewer) and the summary/change type are reused in the Step 5 report. Research shows human-curated context improves review quality; however, over-injection anchors reviewers to the implementor's reasoning, so keep intent context minimal.

### Step 3: Dispatch all 4 agents in parallel

Launch all 4 review agents simultaneously using the Agent tool. Each agent receives the base reference, the change context summary, and the pre-fetched diff. The maintainability reviewer additionally receives the documentation map. Send a single message with all 4 Agent tool calls to ensure parallel execution.

**Prompt template for each agent** (substitute the agent's dimension focus, and append the doc-map block only for `maintainability-reviewer`):

```
Review the code changes against [base reference], focusing on [dimension focus].
[Base reference] is the base branch or commit to diff against.

Change context: [2-3 sentence summary from Step 2]

Intent context: [1-2 sentence artifact intent from Step 2, if found — omit this line if no artifacts were found]

Use intent context to distinguish deliberate decisions from accidental ones. Do not treat it as
justification for all choices — a stated intent does not make a security vulnerability acceptable.

Full diff (already fetched — do not re-run `git diff [base]`):

```diff
[Paste full `git diff [base]` output captured in Step 2. If the diff was too large to inline
and only the file list was captured, instead say: "Diff was too large to inline. Files changed:
[list]. Fetch the diff yourself with `git diff [base] -- <path>` for the paths you need."]
```

[Maintainability reviewer ONLY — append this block:]
Documentation map (candidate doc files in this repo — start here, you may still glob for more):

[Paste the doc-file list captured in Step 2, one path per line.]

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

After all 4 agents return their reports, consolidate through 4 sub-steps. If an agent fails or returns incomplete output, note the gap in the Review Coverage section of the report and proceed with the available reports.

Strip agent identity (which agent produced which finding) during evaluation (Steps 4a–4c) — this prevents majority bias from inflating low-quality findings that happen to appear in multiple agents. After evaluation, re-annotate merged findings with agreement count for the final report.

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
- **Does it contradict another agent's context?** When two agents
  disagree, decompose before resolving: (1) What does each agent
  claim? (2) Can both be true simultaneously? (3) Which agent's
  evidence is more specific — file:line trace vs general assertion?
  (4) Is there information neither agent had that resolves it? Do
  not default to "the more severe finding wins" or "the one that
  says it's fine wins." Drop only when the contradiction is clear
  from evidence; flag with a note if ambiguous.

#### 4c. Filter for actionability

Challenge each surviving finding against these criteria:

- **Is it specific enough to act on?** A developer should know exactly what to change. Drop findings that are vague observations without a concrete fix.
- **Is the confidence level reasonable for the severity?** A BLOCKING finding with LOW confidence should be downgraded to SHOULD_FIX or dropped. A SUGGESTION with HIGH confidence can stay as-is.
- **Would a developer act on this?** Step back and anchor this judgment to the **change type recorded in Step 2** (Feature / Bug Fix / Refactor / Enhancement). Do not re-classify here — use the Step 2 value. Apply these rules:
  - **Bug Fix**: Drop cosmetic and style findings. Drop performance suggestions unless they caused the bug. These are scope-creep.
  - **Refactor**: Cosmetic and structural findings are SHOULD_FIX. Performance findings are relevant only if the refactor changed hot paths.
  - **Feature**: Performance and maintainability findings are relevant. Cosmetic findings in new code are SUGGESTION at most.
  - **Enhancement**: Same as Feature.
  - When in doubt, drop — technically correct but low-value findings (style nitpicks, theoretical edge cases in cold paths) erode trust.

If aggressive filtering leaves fewer than expected findings, that is a GOOD outcome. An empty report with high trust is better than a noisy report that gets ignored.

#### 4d. Sort and compute verdict

1. Sort by severity: BLOCKING first, then SHOULD_FIX, then SUGGESTION
2. Compute verdict based solely on the severity of surviving findings (ignore sub-agent PASS/CONCERNS verdicts — those are per-agent assessments, not the consolidated verdict):
   - Any BLOCKING → REQUEST CHANGES
   - Any SHOULD_FIX (but no BLOCKING) → REQUEST CHANGES. Findings that survived Step 4c filtering have already been validated as genuinely actionable.
   - Only SUGGESTION or clean → APPROVE

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

## SUGGESTION

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
