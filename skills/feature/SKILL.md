---
name: feature
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[feature description or change request]"
description: >
  Standalone feature planning skill. Takes a free-form feature or change
  request, deeply researches the codebase, produces an impact map and
  implementation plan with real code snippets, then decomposes into tasks
  compatible with /execute. Human reviews via annotation cycle at each phase.
  Do NOT use for bugs (use /bug).
  Do NOT use for trivial one-line changes (just make the change).
---

# Feature Planner

> Takes a feature description or change request, deeply researches the
> codebase, produces an impact map and plan with actual code snippets, then
> decomposes into implementation tasks. Human reviews at each phase via an
> annotation cycle. Expect 15-30 minutes.

```
User describes feature
    |
/feature (this skill)
    |
    |-- Phase 0: Clarify intent → deep research → research.md
    |-- Phase 1: Impact map → impact-map.md
    |-- Phase 2: Plan with code snippets → plan.md
    |-- Phase 3: Annotation cycle (1-6 rounds)
    |-- Phase 4: Task breakdown → tasks.md + task JSON files
    |
    v
/execute .claude/features/{slug}/
```

All artifacts are written to `.claude/features/{slug}/` in the project root.
Task JSON files live under `tasks/` within that directory.

### Supporting Files

- [Templates](references/templates.md) — Markdown and JSON templates for all artifacts
- [Implementation Guidance](references/implementation-guidance.md) — Reference for effective execution
- [Common Failure Patterns](references/failure-patterns.md) — Known pitfalls and how to avoid them

### /execute Compatibility

This skill writes task JSON files to `.claude/features/{slug}/tasks/` so
`/execute` can pick them up. Pass the feature directory path to `/execute`:

```
/execute .claude/features/{slug}/
```

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **Existing feature directory** (path to a `.claude/features/{slug}/` directory):
   Enter **Resumption Mode** — check which artifacts exist and resume from the
   last incomplete phase:
   - No `research.md` → start at Phase 0
   - Has `research.md` but no `impact-map.md` → start at Phase 1
   - Has `impact-map.md` but no `plan.md` → start at Phase 2
   - Has `plan.md` with `Status: Draft` → start at Phase 3 (annotation cycle)
   - Has `plan.md` with `Status: Approved` but no `tasks.md` → start at Phase 4
   - Has `tasks.md` → tell the user: "This feature is fully planned. Run
     `/execute .claude/features/{slug}/` to implement."

2. **Free-form text description**: Use as the feature description. Generate a
   URL-safe slug from the first 3-5 significant words (e.g., "add webhook retry
   with exponential backoff" becomes `add-webhook-retry-exponential`). If
   `.claude/features/{slug}/` already exists, append a short numeric suffix
   (`-2`, `-3`). Create the directory and proceed to Phase 0.

3. **No input**: Ask the user to describe the feature or change they want:
   > "Describe the feature or change you want to implement. Be as specific as
   > you like — I'll research the codebase and ask clarifying questions."

---

## Phase 0: Deep Research (Pre-flight)

**This phase must complete before any planning begins.** The research artifact
is your review surface. If the research is wrong, the plan will be wrong, and
the implementation will be wrong. Correcting a wrong assumption here costs
nothing. Catching it in a pull request costs hours.

### Step 0: Clarify Intent and Gather Context

Before researching anything, confirm you understand what the user wants and
why. Wrong assumptions about intent lead to research that answers the wrong
questions.

**Part A — Confirm What and Why**

Evaluate `$ARGUMENTS` against two questions:

1. **What changes does the user want?** (the concrete change)
2. **Why is this change needed?** (the motivation, problem, or goal)

If both are clearly answerable from `$ARGUMENTS`, state your understanding
and ask the user to confirm or correct:

> "Before I research the codebase, let me confirm I understand:
> - **What**: [concrete change]
> - **Why**: [motivation or problem]
>
> Is that right, or would you adjust anything?"

If either is unclear or missing, ask specifically for the missing piece using
`AskUserQuestion`. Do not guess at the "why" — a wrong assumption about
motivation leads to a structurally correct but strategically wrong plan.

This must not feel like a bureaucratic gate. If the user's input already
answers both questions clearly, confirm and move on.

**Part B — External Context Check**

After confirming what and why, ask:

> "Is there any context outside this codebase that should inform my research?
> For example:
> - Architecture documents, user stories, or specs hosted elsewhere
> - Other repositories or services that will be affected
> - Business context or constraints (e.g., 'this is a throwaway prototype',
>   'this must ship by Friday', 'we're migrating off this soon')
> - URLs or documents I should review
>
> If not, just say 'no' and I'll proceed with codebase research."

Handle responses:
- **"No" or equivalent**: Note "No external context provided" and proceed.
- **URLs provided**: Use `WebFetch` to retrieve content. Summarize findings.
- **Text context provided**: Record verbatim.
- **File paths in other repos**: If accessible, read them directly. Otherwise
  ask the user to paste relevant content. Record the repository path — it
  will be used to tag tasks with their target repository in Phase 4.
- **WebFetch fails**: Note the failure, ask the user to paste content directly.

If the feature spans multiple repositories, record all repository paths.
During Phase 4 task breakdown, set each task's `repository` field to the
repo it targets. Set `repositories` in plan.json to the list of all repos.
For single-repo features, use `"."` as the repository value.

All gathered context (what, why, external context) feeds into `research.md`
and must be referenced by the explore agents in Step 2.

**Do not proceed to Step 1 until you have confirmed what, why, and whether
external context exists.**

### Step 1: Read Project Context

Read these files if they exist in the project root (or common locations).
Read them **in full** — do not skim or summarize from headers alone:

- `architecture.md`, `ARCHITECTURE.md`
- `spec.md`, `SPEC.md`
- `CLAUDE.md`
- `README.md`

These provide the architectural and domain context the feature must fit within.

### Step 2: Deep Codebase Exploration

Launch Explore agents via the Agent tool to **deeply and in great detail**
understand the codebase areas relevant to this feature. Use the confirmed
feature intent (what and why) and any external context from Step 0 to focus
exploration — the "why" determines which existing patterns and alternatives
are relevant. The agents must:

1. Read the full content of every file identified as relevant — do not
   summarize from file names or directory structure alone
2. **Understand the intricacies** of existing implementations in the
   affected areas — read function bodies, trace data flow, note patterns
3. Trace every caller and downstream consumer of code that will change —
   follow the call graph outward until reaching clear module boundaries
4. Search for existing code that does something similar to what the feature
   requires — note exact `file:line` references
5. Identify naming conventions, test patterns, error handling patterns,
   and architectural boundaries in the affected areas
6. Check `git log` for recent changes in affected areas

Each agent reports back structured findings with full file paths and
`file:line` references. Do not accept vague findings like "there's a
utility module" — demand specifics.

### Step 3: Answer Three Mandatory Questions

Before writing any plan, answer these questions **in writing** based on
the exploration findings. These prevent the most expensive failure mode:
implementations that work in isolation but ignore existing patterns,
duplicate logic, or violate conventions.

1. **Where does this change belong in the system?**
   Name specific modules, directories, and files. Explain why this location
   and not adjacent alternatives.

2. **Does something similar already exist that must be extended rather
   than duplicated?**
   If yes, cite the exact `file:line` reference. If no, explain what you
   searched and why nothing matched.

3. **Have we solved a related problem before whose pattern can be reused?**
   Cite patterns, utilities, or approaches with `file:line` references.

### Step 4: Write research.md

Write all findings to `.claude/features/{slug}/research.md` using the
[research.md template](references/templates.md#researchmd).

### Step 5: Challenge the Request (Devil's Advocate)

Before presenting findings, launch the `devils-advocate` agent via the Agent tool. 
Pass it:
- The original feature description
- The path to the research file: `.claude/features/{slug}/research.md`

The agent returns a structured challenge brief covering assumptions,
ambiguities, edge cases, scope creep risks, and a pre-mortem. Append the
challenge brief to the end of `research.md` under a `## Devil's Advocate
Challenge` heading.

### Step 6: Present and Validate

Present the research findings **and** the devil's advocate challenges to
the user together. Highlight:
- Where the change belongs and why
- Existing code to extend or patterns to follow
- Any open questions that need answers before planning
- The key challenges from the devil's advocate — especially assumptions
  that need verification and ambiguities that need clarification

> "Review the research and devil's advocate challenges above. If anything
> looks wrong or needs clarification, let me know now. Otherwise, I'll
> continue to the impact map."

If the user provides corrections or clarifications, update `research.md`
with their responses. If the user says nothing or confirms, proceed to
Phase 1. **Only block if there are unresolved open questions that would
make the plan structurally wrong.**

---

## Phase 1: Impact Map

Before individual tasks are written, scan the actual codebase and produce a
repository impact map — which files, which symbols, which patterns are
affected. The user reviews this map before anything else happens.

**The failure mode this catches:** structurally incorrect plans that produce
code that compiles but solves the wrong problem — wrong module, missed
dependency, nonexistent endpoint pattern.

### Step 1: Build the Impact Map

Using the research from Phase 0, identify every file and symbol that will
be created, modified, or affected by this feature. For each entry, note the
action (create/modify/delete) and the specific symbols involved.

### Step 2: Write impact-map.md

Write to `.claude/features/{slug}/impact-map.md` using the
[impact-map.md template](references/templates.md#impact-mapmd).

### Step 3: Present for Review

Present the impact map to the user:

> "Review the impact map above. If any files or areas are missing or
> incorrectly scoped, let me know. Otherwise, I'll continue to the plan."

If the user provides corrections, update the impact map. If the user
confirms or does not object, proceed to Phase 2. **Only block if the
impact map is clearly incomplete** (e.g., missing an entire module the
feature depends on).

---

## Phase 2: Plan Document

One plan file per feature. The plan holds the full intent, architectural
decisions, code snippets showing **actual changes** (not pseudocode, not
descriptions), file paths, and trade-offs.

### Step 1: Determine Delivery Strategy

Before writing the plan, estimate total change size from the impact map. Use
line counts from similar existing files, or rough estimates based on the
number of functions and types being created or modified.

- **Under ~500 lines total**: Single slice (one PR). Note "Single PR" in the
  Delivery Strategy section and proceed.
- **Over ~500 lines total**: Design the plan around multiple **vertical
  slices**. Each slice is one complete thin path through the system — database
  change + service logic + API endpoint + test for *one specific capability*.
  Never slice horizontally (all DB changes, then all service changes). Each
  slice must leave the project in a working, testable state when merged
  independently.

Document the delivery strategy in the plan using the
[Delivery Strategy template](references/templates.md#planmd).

### Step 2: Write plan.md

Write to `.claude/features/{slug}/plan.md` using the
[plan.md template](references/templates.md#planmd).

**Include actual code snippets.** Not pseudocode, not descriptions — the
actual proposed signatures, schema changes, and data shapes. When a reference
implementation exists in the codebase, paste the relevant section alongside
the proposed change. When the AI has a concrete reference, it implements
against that reference instead of designing from scratch.

**Explicitly forbid implementation.** The plan ends with "Do not implement
yet." Without this, the AI will jump to code the moment it thinks the plan
is good enough.

### Step 3: Present the Plan

Present the plan to the user and transition to the annotation cycle:

> "The plan is at `.claude/features/{slug}/plan.md`. You can:
>
> 1. **Annotate in your editor** — open the file, add inline notes starting
>    with `@NOTE:`, `@FIX:`, or `@REMOVE:` at the exact location of each
>    issue, then tell me 'review'
> 2. **Give feedback here** — describe corrections in chat and I'll update
>    the plan
> 3. **Approve** — say 'approve' if the plan is ready for task breakdown"

---

## Phase 3: Annotation Cycle

This is the highest-leverage step. The AI writes code-level detail. The
user injects judgment — product priorities, business constraints, and
engineering trade-offs the AI cannot know.

### How Inline Annotations Work

The user opens `plan.md` in their editor and adds notes directly into the
document at the exact location of each issue:

- `@NOTE: [correction or context]` — domain knowledge the AI lacks
- `@FIX: [what's wrong and what it should be]` — correcting an assumption
- `@REMOVE: [reason]` — rejecting a proposed approach

The `@` prefix avoids collisions with markdown blockquotes (`>`).

Real annotation examples:
- `@FIX: use drizzle:generate for migrations, not raw SQL`
- `@FIX: this should be a PATCH not a PUT`
- `@REMOVE: we don't need caching here`
- `@NOTE: the queue consumer already handles retries, this retry logic is redundant`
- `@FIX: the visibility field needs to be on the list, not individual items — restructure the schema section`

### Processing Annotations

When the user says "review" (or provides chat feedback):

1. Read the updated `.claude/features/{slug}/plan.md`
2. Find all annotation markers — match `@NOTE:`, `@FIX:`, `@REMOVE:`
   case-insensitively with flexible whitespace
3. Address **every** annotation — do not skip any
4. Remove the annotation markers from the updated plan
5. Write the updated plan back to `plan.md`
6. Present what changed in response to each annotation

### Cycle Counter

Track the annotation cycle count with an HTML comment in `plan.md`:

```
<!-- annotation-cycle: 1/6 -->
```

Insert this comment after the `**Status**` line when entering Phase 3.
Increment the counter each time annotations are processed. Read it on
each cycle to determine the current count — do not rely on session memory.

### Cycle Repetition

After addressing annotations, increment the cycle counter and ask:

> "I've addressed all your annotations (cycle {N}/6). Review the updated
> plan — add more notes or say 'approve' when satisfied."

If the plan is still not approved after 6 cycles, ask the user if the
feature scope needs to be reconsidered.

### On Approval

When the user says "approve":

1. Update the plan's `**Status**` to `Approved`
2. Write the updated `plan.md`
3. Proceed to Phase 4

---

## Phase 4: Task Breakdown

After the plan is approved, produce a granular task list as a separate
artifact. The plan carries the long-horizon intent; each task stays within
a bounded working set.

### Task Granularity Rules

- **Count decisions, not lines.** A task that touches 200 lines but makes
  one decision is better than a 30-line task requiring three design choices.
- **Single-concern scope.** Each task must target one logical concern,
  typically touching 1-3 files. An endpoint task that touches route +
  controller + types is one concern. A task that touches auth middleware +
  database schema + frontend component is three concerns.
- **The right size** is the smallest coherent unit that preserves
  architectural clarity — not so granular it fragments the mental model,
  not so broad it requires design choices during execution.
- **PR size ceiling.** Larger PRs receive less thorough review — keep PRs
  focused. Target under 200 lines per slice for genuine reviewer attention.
  If the task list for a single slice implies >500 lines of changes, split
  the slice further.
- **Size warning.** If the task list exceeds ~50 tasks, the feature is
  scoped too broadly. Split into multiple slices or reduce scope. If a single
  slice exceeds ~15 tasks, it is likely too large for one PR.

### Vertical Slices, Not Horizontal Layers

If the plan's Delivery Strategy specifies multiple slices, assign every task
to a slice. Tasks within a slice must form a complete vertical path — never
group by layer (all schema tasks, then all service tasks, then all API tasks).

Each slice must satisfy all four of these questions:
1. **Can a reviewer review this slice in 15 minutes?** If not, it's too large.
2. **Is there exactly one reason this slice would be reverted?** If it could
   be reverted for unrelated reasons, it combines separate concerns.
3. **Can you list every file it touches right now?** If not, the scope is
   unclear.
4. **Is the test for each task obvious before the code exists?** If not, the
   task is underspecified.

If any answer is "no," re-slice.

**One-sentence test:** Describe each slice's diff in one sentence. The sentence
must describe the *change* ("Add retry column to webhooks table and expose
retry count in the status endpoint"), not the *goal* ("Implement webhook
retries"). If you can't write that sentence, the slice is too big or too vague.

### Task Format

Each task must contain:

- **The file(s)** to touch (explicit paths, typically 1-3 files for one concern)
- **The specific function or symbol** to create or modify
- **A reference** to an existing pattern to follow (exact function name
  and `file:line`)
- **What NOT to do** — adjacent files or scope that must not change
- **A "done when" condition** that can be checked mechanically

Use **"must"** throughout task language. "Should" significantly reduces AI
adherence. "Must" aligns with technical standards language and the AI treats
it as a hard constraint.

### Step 1: Write tasks.md

Write to `.claude/features/{slug}/tasks.md` using the
[tasks.md template](references/templates.md#tasksmd).

### Step 2: Write Task JSON Files

Write each task as a JSON file to `.claude/features/{slug}/tasks/` using
the [task JSON schemas](references/templates.md#task-json-schemas):

- `tasks/plan.json` — plan-level information
- `tasks/task_{N}.json` — one per task (e.g. `task_0.json`, `task_1.json`)

### Step 3: Present Tasks for Review

Present the task breakdown to the user:

> "Task breakdown complete — {N} tasks in `.claude/features/{slug}/tasks.md`.
>
> Review the tasks. You can request changes or approve. When ready to
> implement, run:
>
> `/execute .claude/features/{slug}/`"

---

## Common Failure Patterns

See [references/failure-patterns.md](references/failure-patterns.md) for the full list of known pitfalls.
