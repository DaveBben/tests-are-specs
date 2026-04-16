---
name: bug
effort: medium
model: opus
disable-model-invocation: true
argument-hint: "[bug symptom or .claude/bugs/{slug} path]"
description: >
  Bug investigation and fix skill. Captures the symptom, reproduces it
  programmatically, traces root cause, and produces task JSONs for /act.
  No separate plan.md — bugs are 2-4 tasks and go straight to task JSONs.
  Do NOT use for features (use /think). Do NOT use for trivial one-line
  fixes (just make the change).
---

# Bug — Symptom to Fix

> Bugs are different from features: the user has a symptom, not a change
> request. The highest-value step is reproduction — confirming the bug
> exists and producing a failing test. This skill goes from symptom to
> executable task JSONs with minimal intermediate artifacts.

```
User describes symptom → /cks:bug
  Phase 1: Capture (symptom, repro steps, severity)
  Phase 2: Investigate (trace code path, reproduce programmatically)
  Phase 3: Confirm (present findings, user confirms root cause)
  Phase 4: Task JSONs (produce tasks for /act)
```

Artifacts written to `.claude/bugs/{slug}/`.

---

## Input Handling

1. **Existing bug directory**: Resume from last incomplete phase based on which artifacts exist.
2. **Free-form text**: Generate a URL-safe slug from the symptom (max 40 chars). Create `.claude/bugs/{slug}/` and Phase 1.
3. **No input**: Ask user to describe the symptom, not the cause:
   > "Describe what you saw — the symptom, not the cause. For example: 'After saving, the old text still shows' rather than 'the cache doesn't invalidate.'"

---

## Phase 1: Capture

### Step 1 — Understand the Symptom

Listen to the user's description. Check for diagnosis leakage — if they describe a root cause instead of an observable symptom, redirect:

> "That sounds like a diagnosis. What did you actually see? What
> behavior was wrong?"

If description contains multiple bugs, split:
> "That sounds like two issues. Which is more urgent? We'll handle the other separately."

### Step 2 — Fill the Gaps

Conversationally (not as checklist), 1-2 questions at a time: repro steps, expected vs actual, severity, environment if relevant. Push back on vagueness.

### Step 3 — Confirm

Summarize: symptom title, numbered steps, expected/actual, severity.
Wait for confirmation before proceeding.

---

## Phase 2: Investigate

### Step 4 — Codebase Tracing

Read `CLAUDE.md` and any relevant `spec.md`. Then launch **2 parallel Explore agents**:

**Agent 1 — Code path:** trace repro steps through code (file:line per hop), find existing tests for the path, check `git log --oneline -10` for recent changes.

**Agent 2 — Blast radius:** other callers of affected function, shared state (caches, globals, singletons), working patterns elsewhere.

Cap returns to **3 lines per question**.

### Step 5 — Reproduce

1. If existing test already fails on the bug, note it and skip to 3.
2. Write draft reproduction test (asserts expected behavior → fails if bug exists). Save to `.claude/bugs/{slug}/repro-test.[ext]`, do NOT commit.
3. Run test. Record: **RED** (confirmed), **GREEN** (did not reproduce), or **ERROR** (infrastructure issue, do not block).

### Step 6 — Synthesize Root Cause

In the main session (not delegated), synthesize:
- **Root cause hypothesis**: where the bug lives (not where the symptom appears), what is going wrong, and the evidence supporting it
- **At-risk tests**: every existing test that exercises the affected code path — these could regress from the fix
- **Reference pattern**: the working implementation found by Agent 2 that the fix should follow

---

## Phase 3: Confirm

### Step 7 — Present Findings

Present to the user in three parts:

**Part 0 — Ask first (prevent anchoring):**
Ask: "Where do you think the bug lives?" Wait for answer. If no instinct, acknowledge and proceed.

**Part 1 — Root cause:**
State hypothesis with file:line evidence. Where user's instinct aligns, say so. Where it diverges, explain the evidence. Ask if they have additional context. Wait for response.

**Part 2 — At-risk tests (predict-before-reveal):**
Before presenting any test list, ask:

> "Which existing tests do you think could break from this fix?"

Wait for their answer. Then present the AI-identified list for comparison — highlight agreements and differences.

> "Here are the tests I found at risk: [list with reasons]. Combined with yours, does this look complete?"

**This requires human confirmation** — same rule as /think. Incorrect at-risk test context is worse than none.

Wait for confirmation.

### Step 8 — Boundaries

Present what the fix will and will NOT do (no refactoring, no unrelated fixes, no API changes unless required). Wait for confirmation.

---

## Complexity Gate (between Phase 3 and Phase 4)

Before producing task JSONs, check whether the fix exceeds bug-pipeline scope. If investigation revealed **>3 files affected**, the fix requires **changing a shared interface/type**, or would require **>4 tasks**, recommend escalating:

> "This looks larger than a typical bug fix — it touches {N} files across {concerns}. The bug pipeline skips approach selection and plan verification, which matter at this size. Recommend escalating to `/cks:think` → `/cks:plan` → `/cks:act`. I can pass the findings so far. Escalate or continue as bug?"

If the user chooses to continue, proceed — but note the decision in plan.json's `knownRisks`: "User opted to keep bug pipeline despite {N}-file scope."

---

## Phase 4: Task JSONs

Bugs follow a natural structure: **reproduction test → fix → edge case tests**. Expect 2-4 tasks.

### Step 9 — Write plan.json and task JSONs

Write to `.claude/bugs/{slug}/tasks/`.

Use the schemas in [bug templates](references/templates.md): plan.json (same as features + `type`, `severity`, `reproductionResult`, `rootCause`) and task JSONs (identical schema to feature tasks).

**Task structure for bugs:**

**Task 0 — Reproduction test** (if draft exists): write test that fails on the bug. `doNot`: no implementation code. Reference the draft repro-test path in `acceptanceCriteria`.

**Task 1 — Fix**: `blockedBy: ["task_0"]`, `atRiskTests` from Phase 3, `doneWhen`: repro test passes GREEN + regressionCheck passes.

**Task 2 — Edge cases** (optional): `blockedBy: ["task_1"]`, only if investigation found related scenarios.

### Step 10 — Validate and Present

Validate each task JSON:
- `files` has 1-4 entries
- `relevantFiles` paths match expected disk state
- `doNot` and `acceptanceCriteria` non-empty
- `regressionCheck` set when `atRiskTests` non-empty
- `reference` is a single verified file:line
- No `[TBD]` values
- If task_0 references `repro-test.[ext]` in `acceptanceCriteria` and `reproductionResult` was ERROR: verify the file exists on disk. If absent, remove the reference — let the agent write from scratch.

Present to user:
> "{N} tasks in `.claude/bugs/{slug}/tasks/`. Review, then run `/cks:act .claude/bugs/{slug}` to execute."
