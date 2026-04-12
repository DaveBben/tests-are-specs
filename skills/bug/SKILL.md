---
name: bug
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[bug description, symptom, or existing bug directory path]"
description: >
  Bug investigation and fix planning skill. Guides the user through capturing
  a well-formed symptom report, deeply researches the codebase to trace the
  bug's code path, attempts to reproduce the bug programmatically, then
  produces an impact map and implementation plan with tasks compatible with
  /execute. Human reviews via annotation cycle.
  Do NOT use for feature requests (use /feature).
  Do NOT use for trivial one-line fixes (just make the change).
---

# Bug Investigator

> Takes a bug symptom, captures it conversationally, deeply researches the
> codebase, attempts programmatic reproduction, produces an impact map and
> plan with actual code snippets, then decomposes into implementation tasks.
> Human reviews at key phases. Expect 15-30 minutes.

### Supporting Files

- [Templates](references/templates.md) — Markdown and JSON templates for all artifacts
- [Anti-Patterns](references/anti-patterns.md) — Common mistakes to catch during symptom capture

### /execute Compatibility

This skill writes task JSON files to `.claude/bugs/{slug}/tasks/` so
`/execute` can pick them up:

```
/execute .claude/bugs/{slug}/
```

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **Existing bug directory** (path to a `.claude/bugs/{slug}/` directory):
   Enter **Resumption Mode** — check which artifacts exist and resume from
   the last incomplete phase:
   - No `research.md` → start at Phase 0 (symptom capture)
   - Has `research.md` but no `impact-map.md` → start at Phase 3
   - Has `impact-map.md` but no `plan.md` → start at Phase 4
   - Has `plan.md` with `Status: Draft` → start at Phase 5 (annotation cycle)
   - Has `plan.md` with `Status: Approved` but no `tasks.md` → start at Phase 6
   - Has `tasks.md` → tell the user: "This bug is fully planned. Use the
     implementation command at the bottom of tasks.md to implement, or run
     `/execute .claude/bugs/{slug}/`."

2. **Free-form text description**: Use as the symptom seed. Generate a
   URL-safe slug from the first 3-5 significant words of the symptom (e.g.,
   "stale text displays after re-recording" becomes
   `stale-text-after-rerecording`). If `.claude/bugs/{slug}/` already exists,
   append a short numeric suffix (`-2`, `-3`). Create the directory and
   proceed to Phase 0.

3. **No input**: Ask the user what bug they observed. Include the hint:
   > "Describe what you saw — the symptom, not the cause. For example:
   > 'After saving a memo, the old text still shows' rather than
   > 'the cache doesn't invalidate.'"

---

## Phase 0: Symptom Capture

**Goal: Capture what the user observed through conversation. The output is
structured symptom data that feeds the research and reproduction phases.**

A good bug report answers one question: **what did you observe, and how can
someone else observe it too?**

### Step 1: Understand the Symptom

Start by listening. Ask the user to describe what happened in their own words.

After hearing the description, check for **diagnosis leakage** — is the user
describing a root cause instead of an observable symptom?

**Diagnosis signals to push back on:**

- Technical jargon as the primary description ("race condition," "null pointer,"
  "cache invalidation bug," "memory leak")
- The description explains *why* something happens rather than *what* happens
- The user leads with a code location ("the bug is in `handleSubmit`")

**If diagnosis detected:**

> "That sounds like a diagnosis of the cause. Let's capture the symptom first —
> what did you or the user actually see? For example, instead of 'race
> condition in the save handler,' what observable behavior happened? Did data
> disappear? Did the page freeze? Did stale content display?"

Help them reframe. The diagnosis may be correct, but it belongs in the
research phase, not the symptom description.

**Scope check:** If the description contains multiple distinct bugs ("and also,
there's another issue where..."), push back:

> "That sounds like two separate bugs. Let's capture one at a time — which one
> is more urgent? We'll create a card for the other one after."

See [references/anti-patterns.md](references/anti-patterns.md) for the full
list of patterns to watch for during this phase.

### Step 2: The Bug Conversation

Work through these topics conversationally — do NOT present them as a
checklist. Ask 1-2 questions at a time, build on answers, and push back on
vagueness.

**These rounds organize YOUR thinking — they are not a script to follow
literally.** The user's answers will naturally jump between rounds. Follow
their thread, cover the gaps organically, and only use the round structure
to check that nothing was missed before moving to research.

#### Round A: Environment

Establish where and when this bug was observed:

- Operating system and version
- Browser or runtime and version (if applicable)
- Application version or build number
- Deployment environment (production, staging, local dev)
- Any relevant configuration (feature flags, user role, account type)

Don't ask for every field if they're not relevant. A backend API bug doesn't
need a browser version. Use judgment.

#### Round B: Steps to Reproduce

Walk through what the user did, step by step:

- **Start state**: What was true before the bug appeared?
- **Actions**: What did they do, in what order?
- **Observation**: At which step did the unexpected behavior appear?

**Push back on vagueness:**

- "It just breaks" → "What exactly do you see when it breaks?"
- "Sometimes it happens" → "Can you describe the last time it happened?"
- "It doesn't work" → "What specifically doesn't work? What did you expect
  to see vs. what appeared?"

The goal is **a sequence someone else can follow to trigger the bug
consistently.** If the user can't reproduce it reliably, note that explicitly.

#### Round C: Expected vs Actual Behavior

Both must be concrete and specific:

- **Expected**: What should have happened? If the user doesn't know the
  expected behavior, help them reason about it from the feature's intent.
- **Actual**: What did happen? Include specifics: error messages (exact text),
  visual state, data returned, HTTP status codes, timing.

#### Round D: Severity and Impact

Establish the business impact:

- **Who is affected?** All users? A specific segment? Just one user?
- **How often?** Every time? Intermittently? Only under specific conditions?
- **Is there a workaround?** Can users accomplish their goal another way?
- **What's the blast radius?** Data loss? Security exposure? Feature unusable?

**Severity levels:**

| Level | Criteria |
|-------|----------|
| Critical | Data loss, security vulnerability, complete feature outage, no workaround |
| High | Core feature broken, significant user impact, no reasonable workaround |
| Medium | Feature broken but workaround exists, or non-core feature broken |
| Low | Cosmetic issue, minor inconvenience, edge case with easy workaround |

Help the user calibrate — people tend to overrate severity of bugs they
personally encountered.

#### Round E: Evidence

Ask what evidence exists:

- Screenshots or screen recordings
- Error messages (exact text, not paraphrased)
- Log output or stack traces
- Network requests/responses (HTTP status, response body)

If the user has none: "Can you reproduce the bug now and capture the error
message or a screenshot?"

### Step 3: Confirm Before Research

Before proceeding to automated phases, summarize the symptom back to the
user:

> "Here's what I've captured:
>
> **Symptom**: [title — must describe the symptom, not the cause]
> **Environment**: [key details]
> **Steps to Reproduce**: [numbered steps]
> **Expected**: [what should happen]
> **Actual**: [what does happen]
> **Severity**: [level] — [impact summary]
>
> I'll now research the codebase and attempt to reproduce this
> programmatically. Anything to correct before I proceed?"

**Do not proceed to Phase 1 until the user acknowledges the summary.**

---

## Phase 1: Codebase Research

**This phase must complete before any planning begins.** The research
artifact is the review surface. If the research is wrong, the plan will be
wrong, and the fix will be wrong.

### Step 1: Read Project Context

Read any project architecture or spec files not yet loaded in this session
(e.g., `architecture.md`, `ARCHITECTURE.md`, `spec.md`, `SPEC.md`). These
provide the domain context the bug exists within. Skip files already read.

### Step 2: Deep Codebase Exploration

Launch Explore agents via the Agent tool to **deeply trace the code path
involved in the reported symptom**. The agents must:

1. **Trace the reproduction steps through code** — starting from the entry
   point (what handler/function receives the user action), follow the code
   path step by step until reaching where the symptom manifests
2. Read the full content of every file along the code path — do not
   summarize from file names or directory structure alone
3. **Understand the intended behavior** of each function in the path —
   read function bodies, comments, tests, and related documentation
4. Trace every caller and downstream consumer of code that will change
5. Search for existing code that handles the same scenario correctly
   elsewhere — note exact `file:line` references
6. Check `git log --oneline -20 -- [affected files]` for recent changes
   in affected areas

Each agent reports back structured findings with full file paths and
`file:line` references. Do not accept vague findings like "there's a
utility module" — demand specifics.

### Step 3: Answer Three Mandatory Questions

Before any planning, answer these in writing based on the exploration:

1. **Where does this symptom originate in the system?**
   Name the specific module, file, and function. Explain why this location
   and not adjacent alternatives. Distinguish between where the symptom
   *appears* and where the bug *lives* — they may be different.

2. **What is the intended behavior of this code path?**
   Describe what the code was designed to do. Reference tests, comments,
   or specifications that document the expected behavior.

3. **What has changed recently in this area?**
   Check `git log` for affected files. Note any recent commits that might
   have introduced or relate to the bug.

---

## Phase 2: Bug Reproduction Attempt

**This is the key differentiator from `/feature`.** Before planning a fix,
attempt to reproduce the bug programmatically. This validates the symptom
and provides concrete evidence for the research.

### Step 1: Check Existing Test Coverage

Search for existing tests that exercise the affected code path:

1. Grep for test files related to the affected module/function
2. Run those tests. Note if any already fail — they may be testing the
   same scenario
3. If existing tests pass, note what scenarios they cover and what gap
   the bug falls into

### Step 2: Write a Draft Reproduction Test

Write a test that reproduces the bug:

1. Set up the preconditions from the reproduction steps (Phase 0)
2. Perform the action that triggers the bug
3. Assert the **expected** behavior (so the test fails if the bug exists)
4. Follow the project's existing test conventions (detected during Phase 1)

Name the test descriptively: `test_[slug]_[symptom_description]`

### Step 3: Run the Reproduction Test

Run the test and record the result:

- **RED (test fails)**: Bug confirmed programmatically. Capture the exact
  failure output — assertion message, stack trace, actual vs expected values.
- **GREEN (test passes)**: Bug did not reproduce in the test environment.
  Note possible reasons: environment-specific, intermittent, already fixed,
  or test setup doesn't match real conditions closely enough.
- **ERROR (infrastructure issue)**: Test couldn't run. Note what failed
  (missing fixture, wrong framework, compilation error). Do not block on this.

### Step 4: Save but Do NOT Commit

The reproduction test is a **draft artifact**. Do not commit it. Save the
test file to `.claude/bugs/{slug}/draft-reproduction-test.[ext]` so it can
be referenced later. It will be:
- Included in `research.md` as evidence
- Added to the first task's `testContext` so the TDD test-writer can use
  it as a starting point rather than writing from scratch

---

## Phase 3: Write research.md and impact-map.md

### Step 1: Write research.md

Write all findings to `.claude/bugs/{slug}/research.md` using the
[research.md template](references/templates.md#researchmd).

Include:
- The symptom summary from Phase 0
- The reproduction findings from Phase 2 (including the draft test code
  and its output)
- The codebase findings from Phase 1 (with file:line references)
- The root cause hypothesis (clearly labeled as a hypothesis)
- Existing patterns that inform what the fix should look like
- Recent changes from git log
- Open questions for the user

### Step 2: Write impact-map.md

Write to `.claude/bugs/{slug}/impact-map.md` using the
[impact-map.md template](references/templates.md#impact-mapmd).

Bug fixes typically touch fewer files than features. The map should include:
- The file(s) containing the bug (action: modify)
- The regression test file (action: create)
- Edge case test files if applicable (action: create)
- Any files with related code that might be similarly affected

### Step 3: Present for Review

Present the research findings and impact map to the user. Highlight:
- Whether the bug was reproduced programmatically (and the test output)
- The root cause hypothesis and supporting evidence
- The code path trace from entry point to symptom
- Any open questions

> "Review the research and impact map above. Does the root cause hypothesis
> match your understanding? Is anything missing from the impact map?"

**Do not proceed to Phase 4 until the user acknowledges the research.**

---

## Phase 4: Plan Document

### Step 1: Write plan.md

Write to `.claude/bugs/{slug}/plan.md` using the
[plan.md template](references/templates.md#planmd).

**Include actual code snippets.** Not pseudocode, not descriptions — the
actual proposed fix and test code. The draft reproduction test from Phase 2
serves as the starting point for the regression test section.

Bug fix plans should be focused:
- 2-3 implementation sections (test, fix, edge cases)
- Explicit "What NOT to Do" section preventing scope creep
- "Do not implement yet" at the end

### Step 2: Present the Plan

Present the plan to the user and transition to the annotation cycle:

> "The plan is at `.claude/bugs/{slug}/plan.md`. You can:
>
> 1. **Annotate in your editor** — open the file, add inline notes starting
>    with `@NOTE:`, `@FIX:`, or `@REMOVE:` at the exact location of each
>    issue, then tell me 'review'
> 2. **Give feedback here** — describe corrections in chat and I'll update
>    the plan
> 3. **Approve** — say 'approve' if the plan is ready for task breakdown"

---

## Phase 5: Annotation Cycle

Same mechanism as `/feature` but lighter — bug fixes are smaller scope and
should need fewer rounds.

### How Inline Annotations Work

The user opens `plan.md` in their editor and adds notes directly:

- `@NOTE: [correction or context]` — domain knowledge
- `@FIX: [what's wrong and what it should be]` — correcting an assumption
- `@REMOVE: [reason]` — rejecting a proposed approach

The `@` prefix avoids collisions with markdown blockquotes (`>`).

### Processing Annotations

When the user says "review" (or provides chat feedback):

1. Read the updated `.claude/bugs/{slug}/plan.md`
2. Find all annotation markers — match `@NOTE:`, `@FIX:`, `@REMOVE:`
   case-insensitively with flexible whitespace
3. Address **every** annotation — do not skip any
4. Remove the annotation markers from the updated plan
5. Write the updated plan back to `plan.md`
6. Present what changed in response to each annotation

### Cycle Counter

Track the annotation cycle count with an HTML comment in `plan.md`:

```
<!-- annotation-cycle: 1/3 -->
```

Insert this comment after the `**Status**` line when entering Phase 5.
Increment the counter each time annotations are processed.

### Cycle Repetition

After addressing annotations, increment the cycle counter and ask:

> "I've addressed all your annotations (cycle {N}/3). Review the updated
> plan — add more notes or say 'approve' when satisfied."

If the plan is still not approved after 3 cycles, ask the user if the
bug scope needs to be reconsidered.

### On Approval

When the user says "approve":

1. Update the plan's `**Status**` to `Approved`
2. Write the updated `plan.md`
3. Proceed to Phase 6

---

## Phase 6: Task Breakdown

After the plan is approved, produce a granular task list. Bug fixes are
naturally smaller than features — expect 2-4 tasks, not 10+.

### Task Granularity Rules

- **Single-concern scope.** Each task targets one logical concern
  (typically 1-3 files).
- **Bug fixes have a natural structure**: regression test → fix → edge
  case tests. Follow this unless the plan indicates otherwise.
- **Feed the reproduction test to the first task.** If a draft reproduction
  test was saved during Phase 2, add its path to the first task's
  `testContext` with reason `"draft reproduction test — use as starting
  point for the regression test"`. The TDD test-writer can adopt its
  reproduction logic while applying proper structure and assertions.
- **Size warning.** If the task list exceeds ~8 tasks, the bug may be
  more complex than expected. Consider splitting into multiple bugs.
- Use **"must"** throughout task language. "Should" reduces AI adherence.

### Task Format

Each task must contain:

- **The file(s)** to touch (explicit paths, typically 1-3 files for one concern)
- **The specific function or symbol** to create or modify
- **A reference** to an existing pattern to follow (exact `file:line`)
- **What NOT to do** — adjacent concerns or scope that must not change
- **A "done when" condition** that can be checked mechanically

### Step 1: Write tasks.md

Write to `.claude/bugs/{slug}/tasks.md` using the
[tasks.md template](references/templates.md#tasksmd).

### Step 2: Write Task JSON Files

Write each task as a JSON file to `.claude/bugs/{slug}/tasks/` using
the [task JSON schemas](references/templates.md#task-json-schemas):

- `tasks/plan.json` — plan-level information (includes `"type": "bugfix"`)
- `tasks/task_{N}.json` — one per task (e.g. `task_0.json`, `task_1.json`)

### Step 3: Present Tasks

Present the task breakdown to the user:

> "Task breakdown complete — {N} tasks in `.claude/bugs/{slug}/tasks.md`.
>
> Review the tasks. When ready to implement, run:
>
> `/execute .claude/bugs/{slug}/`"

---

## Conversation Rules

- **One question at a time.** Do not dump a list of 10 questions — multiple
  questions overwhelm users and produce lower-quality answers as they rush
  through items.
- **Push back on vagueness.** Every vague statement gets restated in specific
  terms: "When you say 'it breaks,' I interpret that as [specific behavior].
  Is that right?"
- **Name the anti-pattern.** When you see a common mistake, name it:
  "That's a diagnosis, not a symptom," or "That reproduction step assumes
  too much."
- **Celebrate good input.** When the user provides a clear reproduction
  sequence or exact error message, acknowledge it — positive reinforcement
  helps them know what detail level is useful.
- **The conversation IS the Phase 0 deliverable.** Do not write the symptom
  summary silently.

---

## Common Failure Patterns

- **Skimming instead of reading** — Phase 1 exists because the AI reads at
  signature level and moves on. Force deep reading: "read the full function
  body", "trace every caller."
- **Planning before researching** — Research must complete BEFORE any plan.
- **Pseudocode in the plan** — The plan must contain actual code snippets.
- **Scope creep into refactoring** — Bug fixes must be minimal. The "What
  NOT to Do" section prevents this.
- **Reproduction test committed prematurely** — The Phase 2 test is a draft.
  Do not commit it. The task breakdown assigns proper test writing to the
  TDD agent.
- **Diagnosis in the symptom title** — The title describes what the user
  sees, not what the code does wrong.
