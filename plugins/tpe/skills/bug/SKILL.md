---
name: bug
effort: max
model: opus
disable-model-invocation: true
argument-hint: "[bug symptom or .claude/bugs/{slug} path]"
description: >
  Bug investigation and fix skill. Captures the symptom, reproduces it
  programmatically, traces root cause, and produces task JSONs for /act.
  No plan.md — produces plan.json and task JSONs directly.
  Do NOT use for features (use /think). Do NOT use for trivial one-line
  fixes (just make the change).
---

# Bug — Symptom to Fix

> Bugs are different from features: the user has a symptom, not a change
> request. The highest-value step is reproduction — confirming the bug
> exists and producing a failing test. This skill goes from symptom to
> executable task JSONs with minimal intermediate artifacts.

```
User describes symptom → /tpe:bug
  Phase 1: Capture (symptom, repro steps, severity)
  Phase 2: Investigate (trace code path, reproduce programmatically)
  Phase 3: Confirm (present findings, user confirms root cause)
  Phase 4: Task JSONs (produce tasks for /act)
```

Artifacts written to `.claude/bugs/{slug}/`.

---

## Input Handling

Resolve `$ARGUMENTS` to one of three modes:

1. **Existing bug directory** (`$ARGUMENTS` is a path to `.claude/bugs/{slug}`): Resume from last incomplete phase based on which artifacts exist.
2. **Free-form text** (`$ARGUMENTS` is a symptom description): Generate a URL-safe slug from the symptom (max 40 chars). Create `.claude/bugs/{slug}/` and begin Phase 1.
3. **No input** (`$ARGUMENTS` is empty): Ask user to describe the symptom, not the cause:
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

Conversationally (not as checklist), 1-2 questions at a time. Target these four pieces of information:

1. **Repro steps** — numbered, concrete actions (not "use the feature")
2. **Expected vs actual** — what should happen, what happens instead
3. **Severity** — who is affected, how often, is there a workaround
4. **Environment** (if relevant) — browser, OS, config, data shape

**Stopping criterion:** you have enough when you could write a failing test from the description alone, without reading any code. If you can't, ask what's missing. If the user doesn't know (e.g. "it just crashes sometimes"), note the gap and proceed — Phase 2 investigation may fill it. Do not ask more than 2 rounds of questions.

### Step 3 — Confirm

Summarize: symptom title, numbered steps, expected/actual, severity.
Wait for confirmation before proceeding.

---

## Phase 2: Investigate

### Step 4 — Codebase Tracing

Read `CLAUDE.md` and, if present, any relevant `spec.md`. Then launch **2 parallel Explore agents** using the Agent tool with `subagent_type: "Explore"`. Issue both Agent tool calls in a single message to ensure parallel execution.

See [anti-patterns](references/anti-patterns.md) for diagnosis patterns to catch during investigation.

**Agent 1 — Code path:**
1. Starting from the entry point of the repro steps, trace the code path to the symptom location. Return: file:line per hop (max 5 hops).
2. Which test files import or call into any file on this path? Return: file path + test symbol.
3. `git log --oneline -10` on each file in the path — any recent changes that could have introduced the bug?

**Agent 2 — Blast radius:**
1. What other callers invoke the function where the bug manifests? Return: file:line per caller.
2. Does the affected function read or write shared state (caches, globals, singletons, class-level mutables)? Return: the state, where it's defined, and who else touches it.
3. Is there a working code path that does the same thing correctly (a different caller, a sibling method, an older pattern)? Return: file:line of the working implementation.

**Agent output format** — cap each answer to 3 lines:
```
Q: [question]
A: file:line — [finding]
Note: [one sentence max]
```
If no answer, return "not found" — do not invent.

**Scope cap:** if the combined agent findings touch more than 8 files, focus detailed analysis on the code path (Agent 1) and list blast radius files (Agent 2) by name only. Bugs should have a narrow fix — a wide blast radius is a signal to check the complexity gate early.

### Step 5 — Reproduce

1. If existing test already fails on the bug, note it and skip to 3.
2. Write draft reproduction test (asserts expected behavior → fails if bug exists). Save to `.claude/bugs/{slug}/repro-test.[ext]`, do NOT commit.
3. Before running, verify the test: does it exercise the exact code
   path from the repro steps? Does it assert *expected* behavior (fails
   on the bug), not *current* behavior (passes trivially)? A repro test
   that passes with the bug present is worse than no test — it gives
   false confidence that the fix works.
4. Run test. Record: **RED** (confirmed), **GREEN** (did not reproduce), or **ERROR** (infrastructure issue, do not block).

### Step 6 — Synthesize Root Cause

In the main session (not delegated), synthesize:
- **Root cause hypothesis** — identify through two frames and check
  convergence: (1) trace backward from symptom — what's the last
  correct state and where does it go wrong? (2) trace forward from the
  suspected cause — if this is broken, what symptoms would it produce,
  and do they match the report? If both frames point to the same
  location, confidence is high. If they diverge, surface the
  uncertainty to the user in Step 7 rather than picking one.
  **Confidence calibration:** state your confidence as one of:
  - *Confirmed* — repro test fails at the exact location, both frames converge, evidence is directly observable (e.g., a test fails at the exact line, a log shows the wrong value) rather than inferred from code reading
  - *Strong hypothesis* — both frames converge but no failing test yet, or test fails but at a slightly different location
  - *Candidate* — only one frame points here, or evidence is circumstantial (e.g. recent git change near the area)
  Present the label in Step 7 so the user knows how much weight to give the finding.
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

If the root cause is architectural (data layout, shared state, interface design) and a **symptom-layer fix** (input validation, caller adaptation, defensive check) could close the bug without touching the architecture, surface both options before moving on:
- *Fix at root* — eliminates this bug class at source; larger blast radius, more at-risk tests, architectural change
- *Fix at symptom layer* — smaller change; the architectural issue persists and may resurface as a different symptom

Do not recommend one. The engineer decides based on scope, urgency, and recurrence likelihood — some teams accept a shallow fix with a tracked debt item, others fix at root every time. The AI's job is to make sure both options are visible before committing to a fix location.

**Part 2 — At-risk tests (predict-before-reveal):**
Before presenting any test list, ask:

> "Which existing tests do you think could break from this fix?"

Wait for their answer. Then present the AI-identified list for comparison — highlight agreements and differences.

> "Here are the tests I found at risk: [list with reasons]. Combined with yours, does this look complete?"

**This requires human confirmation** — do not proceed until the user explicitly confirms the at-risk test list is complete. Incorrect at-risk test context is worse than none.

Wait for confirmation.

### Step 8 — Boundaries

Present what the fix will and will NOT do. At minimum, evaluate each category and include any that apply:

- **Fix scope**: which files change, which don't (no refactoring, no unrelated fixes)
- **Interface stability**: does the fix change any public API, CLI flag, or data format? If not, say so explicitly.
- **Test scope**: does the fix require modifying existing tests, or only adding new ones?
- **Data/state**: does the fix change persisted data, cached state, or migration behavior?

Skip categories where the fix does not touch that domain (e.g., skip "Data/state" if no persisted data is involved).

Wait for confirmation.

---

## Complexity Gate (between Phase 3 and Phase 4)

Before producing task JSONs, check whether the fix exceeds bug-pipeline scope. If investigation revealed **>3 files affected**, the fix requires **changing a shared interface/type**, or would require **>4 tasks**, recommend escalating:

> "This looks larger than a typical bug fix — it touches {N} files across {concerns}. The bug pipeline skips approach selection and plan verification, which matter at this size. Recommend escalating to `/tpe:think` → `/tpe:plan` → `/tpe:execute`. I can pass the findings so far. Escalate or continue as bug?"

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

**Verify acceptance criteria:** for each task, ask "Could I implement
this fix from only these criteria? Does each criterion test exactly one
observable behavior?" If a criterion is ambiguous or conflates multiple
behaviors, split or sharpen it — the code-implementor verifies against
these.

**Ambiguity signals to catch:**
- Criterion uses "correct" or "appropriate" without defining what that means for this bug
- Criterion names two behaviors joined by "and" — split into two criteria
- Criterion cannot be checked by running a command or reading a specific output — it's an aspiration, not an AC
- **Observable** means: the implementor can verify it by running a command, inspecting a file, or observing a behavior — not by reading the code and judging whether it "looks right"

Validate each task JSON:
- `files` has 1-4 entries
- `relevantFiles` paths match expected disk state
- `doNot` and `acceptanceCriteria` non-empty
- `regressionCheck` set when `atRiskTests` non-empty
- `reference` is a single verified file:line
- No `[TBD]` values
- If task_0 references `repro-test.[ext]` in `acceptanceCriteria` and `reproductionResult` was ERROR: verify the file exists on disk. If absent, remove the reference — let the agent write from scratch.

Present to user with a focused review guide. Identify the 1-2 highest-risk aspects of *this specific fix*. For bugs, common risk areas: whether the repro test actually exercises the bug (not a nearby path), whether the fix addresses root cause vs. symptom, whether at-risk tests are complete.

> "{N} tasks in `.claude/bugs/{slug}/tasks/`.
>
> **Highest-risk areas to scrutinize:**
> - [specific risk — e.g. "repro test asserts on return value but the bug is a side effect on cached state"]
>
> Review, then run `/tpe:execute .claude/bugs/{slug}` to execute."
