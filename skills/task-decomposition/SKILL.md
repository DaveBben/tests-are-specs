---
name: task-decomposition
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[story ID or bug ID]"
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
description: >
  Use when the user provides a story or bug ID and wants it decomposed into
  implementation tasks. Reads the story from JSON artifacts, discovers relevant
  repositories, validates readiness (story-reviewer gate), explores all involved
  codebases, then decomposes into individual task JSON files with
  parallel-optimized TDD structure. Only accepts stories and bugs — aborts on
  epics. Do NOT use for ad-hoc changes without a ticket (use Claude's plan mode).
  Do NOT use for executing an existing plan (use /execute).
---

# Story & Bug Decomposer

> Takes a story or bug from the JSON artifact store, discovers which
> repositories are involved, explores them all, then produces individual
> task JSON files ready for `/execute`. Expect 10-20 minutes.

The `implementation-plans` skill is preloaded — its templates, anti-patterns, and section
guidance are the rulebook for drafting. If `implementation-plans` is not available, stop
and tell the user before proceeding — the plan template is essential for executor
compatibility with `/execute`.

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **Story ID** (matches patterns like `story_001`, `story_012`, or a bare number):
   Read from `~/.claude/backlog-driven-development/artifacts/stories/{id}.json`.
   Proceed to Phase 0.
1b. **Bug ID** (matches `bug_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/bugs/{id}.json`.
   Note: for most bugs, `/triage` is the recommended path — it handles
   the full lifecycle (reproduce → isolate → test → fix → verify → PR).
   Use `/task-decomposition` only for complex bugs that genuinely need
   formal parallel decomposition into multiple tasks. Ask the user:
   > "For bugs, `/triage` handles the full investigation and fix lifecycle.
   > `/task-decomposition` is for complex bugs needing formal parallel tasks.
   >
   > Would you like to:
   > 1. **Use `/triage`** (recommended) — systematic debugging workflow
   > 2. **Continue here** — decompose into parallel implementation tasks"
   If the user chooses `/triage`, stop and tell them to run `/triage {id}`.
   Otherwise proceed to Phase 0.
2. **Artifact file path** (points to a story JSON file under the artifacts directory):
   Read the story from the file. Check for existing task files in
   `~/.claude/backlog-driven-development/artifacts/tasks/` matching this story's
   number — if found, enter the **existing tasks check** (below). Otherwise proceed
   to classification.
3. **Existing tasks or plan-summary path** (points to a task or plan-summary JSON file
   in the artifacts directory): enter resumption mode (below).
4. **Legacy plan path** (points to an existing `.claude/implementation-plans/` file):
   enter resumption mode (below).
5. **No input or unrecognized**: Ask the user for a story or bug ID.

This skill does NOT accept plain text descriptions. If the user describes a change without
a ticket, tell them: "This skill works with stories and bugs. Use `/story` to create one,
or use Claude's plan mode for ad-hoc changes."

### Resumption

If `$ARGUMENTS` points to an existing task file, plan-summary JSON, or legacy
plan file:

- Read the plan-summary JSON (or legacy plan.md). Check Open Questions. If unresolved,
  present them to the user.
- If Status is `Draft`, re-enter Phase 4.
- If `Approved`, tell the user to run `/execute [story ID or path]`.
- Do NOT re-run the readiness gate or exploration.

If the conversation is interrupted before tasks are written, the user must restart
the skill — interview state is not persisted between conversations.

### Existing Tasks Check

If a story ID is provided (case 1 or 2) and matching task files already exist
in `~/.claude/backlog-driven-development/artifacts/tasks/`:

1. Read the plan-summary JSON to get the current status and task count
2. List existing task files matching this story's number

Present to the user:

> "This story already has [N] tasks (Status: [status]):
>
> - Task 0: [title] — [status]
> - Task 1: [title] — [status]
> - ...
>
> Would you like to:
> 1. **Resume** — pick up from where you left off (enters Resumption mode)
> 2. **Replace** — discard existing tasks and re-decompose from scratch
> 3. **Cancel** — keep existing tasks as-is"

If the user chooses Resume, enter Resumption mode. If Replace, proceed
with fresh decomposition (existing task files will be overwritten in
Phase 7). If Cancel, stop.

---

## Phase 0: Fetch and Classify

### Fetching the Story/Bug

Read the story/bug from the JSON artifact store:

1. **Artifact store** (primary): Read from
   `~/.claude/backlog-driven-development/artifacts/stories/{id}.json`.
   Also read the parent epic if `epicId` is present in the story JSON (for context,
   not for decomposition) from `artifacts/epics/{epicId}.json`.

2. **User paste** (fallback): If the artifact file does not exist, ask the user to paste
   the story/bug content directly.

Present the story to the user after reading it.

### Classification

Determine whether this is a **story**, **bug**, or **epic**:

- **Epic**: Contains child stories/items, spans multiple features, has no specific
  acceptance criteria of its own, type field contains "epic" or "initiative." →
  **ABORT**: "This is an epic containing multiple stories. Run `/epic` to
  decompose it into stories first, then `/task-decomposition` on each story."
- **Bug**: Has reproduction steps, describes broken existing behavior, references
  errors or unexpected outcomes, type field contains "bug" or "defect."
- **Story**: Everything else — describes new desired behavior with acceptance criteria.

---

## Phase 0b: Repository Discovery

After fetching and classifying the story/bug, identify which code repositories are
involved before proceeding to the readiness gate.

### Step 1: Read the Registry

Read `~/.claude/backlog-driven-development/repos.json` (the registry managed by `/repos`).

**If the registry exists and has entries:**

If the story already has a **Target Repositories** section, cross-reference it
against the registry — match by name or path. Pre-select matching repos.

Present the registered repos and ask the user to select which apply:

> "Which repositories are involved in this story?
>
> Registered repos:
> 1. `{name}` — {path} {description if present}
> 2. `{name}` — {path} {description if present}
> ...
>
> Enter the numbers (e.g., `1 3`) or `all`. You can also type an unlisted path."

**If the registry is empty or does not exist:**

Fall back to asking directly:

> "Which code repositories are involved in implementing this story?
> List them as local filesystem paths (e.g. `/Users/you/repos/api-server`).
>
> Tip: Run `/repos add` to register your repos so you don't need to type paths each time."

If the story already has a **Target Repositories** section, pre-populate the list
and ask the user to confirm or modify:

> "The story lists these target repositories: [list]. Are these still correct?
> Add or remove any as needed."

### Step 2: Validate Access

For each selected or typed repository, verify the directory exists:

```bash
ls "{path}"
```

If a path does not exist:
> "Path not found: `{path}`. Check the path or clone the repo first."
Remove it from the list and re-ask.

Record each validated repo as `{name, path, access: "local"}`.

Store the validated repository list as working state for Phase 2.

### Step 3: Determine Artifact Paths

Establish the artifact paths for task output in Phase 7. The story's numeric ID
(e.g., `001` from `story_001`) determines the output paths:

- Tasks: `~/.claude/backlog-driven-development/artifacts/tasks/task_{storyNum}.{taskNum}.json`
- Plan summary: `~/.claude/backlog-driven-development/artifacts/plan-summaries/plan_{storyNum}.json`

---

## Phase 1: Story Readiness Gate

**This phase is mandatory. Do not skip it.**

### Step 0: Check Story Status

Before running the reviewer, check the story's `**Status**` field:

- If `status: "TODO"`: proceed to the reviewer gate.
- If `status: "BACKLOG"`: warn the user:
  > "This story is still in BACKLOG status. Run `/story [path]` to finalize and
  > move it to TODO before decomposing into tasks. Proceed anyway?"
- If `status: "NEEDS_REFINEMENT"`: present the `revisionReason` and warn:
  > "This story was flagged for refinement:
  >
  > **Reason**: [revisionReason content]
  >
  > Run `/story [path]` to address the refinement before decomposing. Proceed anyway?"

### Step 1: Run the Reviewer

Dispatch the `story-reviewer` agent via the Agent tool. Pass:
- The fetched story/bug content (full text)
- The item type (story or bug)

The story-reviewer returns **READY** or **NOT_READY** with specific missing items.

**If NOT_READY:**

Present the missing items to the user. Offer two paths:

> "This story/bug is missing information needed for decomposition:
> - [missing item 1]
> - [missing item 2]
>
> You can either:
> 1. Update the story in [tool] and re-run `/task-decomposition [ID]`
> 2. Provide the missing information here and I'll incorporate it"

If the user provides info verbally, incorporate it as supplementary context and proceed.
Do NOT re-run the story-reviewer — the user's verbal input is sufficient.

**If READY:** Proceed to Phase 2.

---

## Phase 1b: Upstream Artifact Status Check

After the story passes the readiness gate, discover and check the status of
upstream artifacts. This ensures the story is built on approved foundations.

### Step 1: Discover Upstream Artifacts

Search for associated artifacts using the story JSON and index.json:

1. **Story JSON** — read the story's `epicId` field from the story JSON
2. **Epic** — read the epic JSON from
   `~/.claude/backlog-driven-development/artifacts/epics/{epicId}.json`
3. **Initiative** — read `~/.claude/backlog-driven-development/artifacts/index.json`
   to find the parent initiative (where the epic's ID appears). Read the initiative
   from `artifacts/initiatives/{initiativeId}.json`
4. **Architecture** — read `index.json` to find architectures where `initiativeId`
   matches. Read from `artifacts/architectures/{archId}.json`

For each discovered artifact, read its `status` field.

### Step 2: Check for NEEDS_REFINEMENT

If ANY upstream artifact has `status: "NEEDS_REFINEMENT"`:

> "WARNING: Upstream artifact needs refinement before proceeding:
>
> - **[artifact type]** at [path]: Status is NEEDS_REFINEMENT
>   Reason: [revisionReason content]
>
> Proceeding with task decomposition on a story whose upstream artifacts
> need refinement may produce tasks that need to be redone. Would you like to:
>
> 1. Stop and address the upstream refinement first
> 2. Proceed anyway (tasks may need rework)"

If the user chooses to stop, tell them which skill to run to address the
revision (e.g., `/architecture [path]`, `/epic [path]`).

### Step 3: Flag Upstream Issues During Decomposition

During Phase 2 (exploration) and Phase 4 (decomposition), if you discover
that an upstream artifact is inadequate — e.g., the architecture doesn't
account for a critical integration, the story's acceptance criteria
contradict the epic scope, or the idea's constraints are missing — you
MUST flag it:

1. **Mark the upstream artifact** as `NEEDS_REFINEMENT` by updating its
   `status` field and adding a `revisionReason`
2. **Inform the user**:

   > "During decomposition, I found that [artifact type] needs refinement:
   >
   > **Issue**: [specific problem discovered]
   > **Impact**: [how this affects the current decomposition]
   >
   > I've marked [artifact path] as NEEDS_REFINEMENT. You can address this
   > by running `/[skill] [path]` after we finish here, or stop now."

3. **Record it as an Open Question** in the plan if the user chooses to
   proceed

---

## Phase 2: Silent Exploration + Verification

### Step 1: Multi-Repository Exploration

Read all involved codebases first. Every question you ask should be informed and specific.

For **each repository** identified in Phase 0b, launch an Explore agent in parallel
(via the Agent tool). Each agent receives:
- The story content (full text)
- The repository's access method and path or identifier
- Instructions to explore (see per-repo checklist below)

**For local repositories** (access: "local"), each agent should:

1. Read SPEC.md, architecture.md, CLAUDE.md, README.md, and project config
2. Run `git status` and `git branch` — confirm starting state, note uncommitted changes
3. Scan directory structure to understand project shape and module boundaries
4. Search for code directly related to the story — find affected files, functions, types, tests
5. **Trace every caller and downstream consumer of the code that will change** — follow the
   call graph outward until you reach clear module boundaries or external consumers
6. Search for other code depending on the same data shapes, contracts, or assumptions
7. Check `git log` for recent changes in affected areas — understand what's in flux
8. Note existing patterns, test infrastructure, naming conventions, architectural boundaries
9. Identify what already exists that could be reused — note `file:line`

All file paths must be prefixed with the repository's absolute path so they are
unambiguous across repositories.

Each agent reports back structured findings:
- Repository name and path
- Key findings (what exists, what needs to change)
- Affected files with full paths
- Existing patterns and conventions
- Reusable code with `repo:file:line` references

The orchestrator (main session) synthesizes findings from all repositories into a
unified view before the Verification Round.

### Step 1b: Research Gate (conditional)

After Multi-Repository Exploration, assess across all repos: **does this story
introduce technology, libraries, patterns, or external integrations not already
in any of the explored codebases?**

- If **no** (internal change using existing patterns): skip to Step 2.
- If **yes**: use the Agent tool to launch 2-3 parallel subagents (model: sonnet, with
  web search) before the verification round. Each agent focuses on one concern:
  - **Library/technology viability**: Right choice? Alternatives? Known pitfalls?
  - **Integration patterns**: How do others integrate this? Common mistakes?
  - **Similar implementations**: Solved before in the ecosystem? Emerging patterns?

  Feed research findings into the Assumption Ledger.

### Step 2: Single Verification Round

The story already contains requirements. This round focuses on **gaps between the story
and the codebase reality** — not a full interview.

**Produce an Assumption Ledger** — list every assumption you would need to make to
decompose this story right now:

Format: `A1. [Assumption] — if false: [consequence for decomposition]`

Present your findings:

> "From reading the codebases and the story, here's what I found:
> - [Key finding 1 — e.g., the API endpoint the story references already exists]
> - [Key finding 2 — e.g., the data model needs a new column]
> - [Key finding 3 — e.g., existing test infrastructure covers this area]
>
> I'm assuming:
> - A1. [assumption]
> - A2. [assumption]
>
> Please confirm or correct these before I decompose."

Ask 2-4 targeted questions about things the code cannot tell you. Focus on:
- Ambiguities in acceptance criteria
- Unstated constraints (what must NOT change)
- Behavioral choices the story leaves open
- Rollback expectations

**Do NOT accept vague answers.** If the user says "handle errors gracefully," restate in
specific, testable terms: "When you say handle errors gracefully, I interpret that as: if
the API call fails, show an error toast and revert the optimistic update within 3 seconds.
Is that right?"

---

## Phase 3: Decomposition Choice

After verification is complete, present the user with two options:

> **How would you like to break this down into tasks?**
>
> - **Option A** (default): I decompose the work into implementation tasks and present
>   them for your review.
> - **Option B**: You decompose first. I'll give you a plan template with the header,
>   What/Why/Scope sections pre-filled from the story and our verification. You fill in
>   the tasks. Meanwhile, I'll silently complete my own task breakdown in the background.

**If Option A:** Proceed directly to Phase 4.

**If Option B:**
1. First, dispatch a background Agent (model: sonnet) to complete your own full task
   breakdown using the Phase 4 algorithm. This runs while the user works on theirs.
2. Generate a partial plan with header, What We Are Building, Why This Exists, Scope,
   Downstream Impact, and Risks & Rollback pre-filled. Leave the Implementation Tasks
   section with a single placeholder: `### Task 0: [Your first task here]`
3. Present the template to the user and wait for them to fill in their tasks.
4. If the user submits zero tasks, prompt them to add at least one before continuing.
5. Once the user signals they are done, collect the background agent's result and present
   both side-by-side:
   - Show the user's breakdown and yours in a comparison format
   - Highlight differences in task granularity, ordering, and scope coverage
   - **This is the learning moment** — explain why you split things the way you did
   - The user chooses: adopt yours, keep theirs, or merge elements from both
6. The chosen breakdown proceeds to Phase 5 (Plan Review).

---

## Phase 4: Parallel-Optimized Decomposition

This is the core of the skill. Produce a plan.md using the implementation-plans template,
optimized for maximum parallel execution by `/execute`.

### Step 1: Classify and Split

**For stories** — apply vertical slicing (end-to-end behavior per task):

Task 0 is always contracts/interfaces — the legitimate horizontal prerequisite that
unlocks all downstream parallel work. Make it as thin as possible: interfaces, types,
and contracts only — zero business logic.

Apply the **PIDR** splitting patterns to find natural task boundaries:

- **Paths**: Different user paths through the same feature → separate tasks. Example:
  "User can log in with password" and "User can log in with OAuth" are two tasks.
- **Interfaces**: Different I/O interfaces (API endpoint, UI component, CLI command) →
  separate tasks when they can be built independently against the same contract.
- **Data**: Different data types or sources → separate tasks. Example: "Import from CSV"
  and "Import from JSON" are two tasks.
- **Rules**: Different business rules or validations → separate tasks. Example: "Basic
  discount calculation" and "Tiered loyalty discount" are two tasks.

**No spikes.** This skill only accepts stories and bugs that are ready for implementation.
If a story has unknowns requiring experimentation, it should not have passed the
story-reviewer gate. Send it back to the backlog for a spike first.

Also consider:
- **Workflow steps**: Each step in a sequential process → separate task
- **CRUD operations**: Each operation → separate task (Read before Write)
- **Simple/Complex**: Build the simple version first, then the edge cases

Each task must be a complete TDD cycle (50-200 lines target, 400 hard ceiling).

### Multi-Repository Task Assignment

Every task must include a `**Repository:**` field specifying which repo it
belongs to. Use the repository list from Phase 0b. This enables `/execute`
to filter tasks to the current repo.

- For each task, determine which repository it belongs to based on the files
  it touches and the type of work (API, UI, shared lib, infra, etc.)
- Tasks in different repos cannot have `Blocked By` dependencies on each
  other within the same batch — cross-repo dependencies must be sequential
  (different batches) since they execute in separate `/execute` runs
- If all tasks belong to a single repo, the `**Repository:**` field can be
  set once in the plan-summary JSON instead of per-task

**For bugs** — different decomposition flow:

Bugs are typically 2-4 tasks. Do NOT over-decompose.

- **Task 0**: Contracts/types (only if the fix requires new interfaces; otherwise skip
  Task 0 and start at Task 1)
- **Task 1**: Write a failing test that reproduces the bug (RED state = bug confirmed).
  This task's AC is: "A test exists that fails with the exact behavior described in the
  bug report."
- **Task 2**: Implement the fix to make the test pass (GREEN state = bug fixed).
- **Task 3** (if needed): Regression tests for related edge cases discovered during
  investigation.

### Steps 2-4: Build DAG, Compute Batches, Identify Critical Path

Read [references/parallel-optimization.md](references/parallel-optimization.md) for the
full algorithm. In summary:

- **DAG**: Each task is a node; edges represent `Blocked By` relationships. Minimize edges
  — prefer independent tasks. Extract shared concerns into Task 0.
- **Symbol dependencies**: When a task calls or imports a symbol (function, type, constant)
  produced by another task — even if they touch different files — declare it in
  `symbolDependencies` as `"TaskN.SymbolName"`. This prevents `/execute` from batching
  tasks that have no file overlap but would fail because one consumes code the other hasn't
  written yet. Zero file overlap is necessary but not sufficient for safe parallel execution.
- **Batches**: Apply Kahn's algorithm to group tasks into parallel batches (same algorithm
  `/execute` uses). Tasks in the same batch have no `Blocked By` dependency, no file
  overlap, AND no symbol dependencies on each other.
- **Critical path**: The longest dependency chain sets the minimum batch count. Present
  the execution schedule prominently in the plan with batch groupings and critical path.

### Step 5: Validate and Optimize

Before finalizing:

1. **Coverage check**: Every AC from the story maps to at least one task via `Covers:`.
   No orphan tasks (tasks that don't cover any AC or edge case).
2. **Size check**: Every task targets 50-200 lines. Split tasks over 200; merge tasks
   under 30 lines into adjacent tasks.
3. **Critical path optimization**: Can the critical path be shortened?
   - Can a blocking task be split so part of it runs in an earlier batch?
   - Can Task 0 be made thinner to unblock more tasks?
   - Is there a file appearing in many tasks' Relevant Files, creating a bottleneck?
4. **Constraint check**: Are all constraints from the story and verification round
   captured in the plan's Constraints section?

### Writing the Plan

Write the plan using the implementation-plans template. Follow its template structure,
validation checklist, and anti-patterns exactly. At this stage, compose the plan as a
single unified document internally — the distributed output (individual task files) is
produced in Phase 7.

**Additions specific to this skill:**

- Every task includes `**Implementer:** AI | Human` after the task heading. Default to
  `AI` — only use `Human` when the task requires human judgment, credentials, manual
  verification, or steps that cannot be automated (e.g., configuring a third-party
  service, approving a deployment, testing on a physical device)
- Every task includes `**Repository:**` identifying which repo it belongs to
- The story/bug ID is referenced in the plan header (not duplicated content — the story
  is read from the artifact store at planning time)
- The Parallel Execution Schedule section appears after the Implementation Tasks heading
  and before Task 0
- Reference existing code to reuse by `repo:file:line` — search for existing
  implementations first, cite them, never propose new code for what already exists
- Read the specific source files that will change before writing tasks
- Every task includes a `**Verification:**` section — a prose description of what
  "done" looks like (e.g., "Module compiles. Watcher detects new .m4a files in a
  temp directory. Tests pass."). This is more concrete than acceptance criteria
  alone and tells the executor exactly what to check.
- Every task includes a `**Do NOT:**` section — explicit anti-scope listing what
  the implementer must avoid (e.g., "Do NOT implement actual monitoring — that's
  Task 1.2"). This prevents scope creep within tasks and guards against common
  mistakes. Reference which task owns the excluded work.

### Self-review before presenting

Run the implementation-plans Validation Checklist (Must-Pass Gate). Additionally verify:
- Does every task have an `Implementer: AI | Human` label?
- Does every task have a `Verification:` section with prose description of done?
- Does every task have a `Do NOT:` section with explicit anti-scope?
- Are all assumptions from the Verification Round resolved in the plan or listed as
  Open Questions?
- Does the Parallel Execution Schedule match the `Blocked By` declarations?
- Is the critical path as short as possible given the task boundaries?

---

## Phase 5: Plan Review (Automated)

### Assemble Transient Unified File

Before dispatching reviewers, assemble the complete plan into a single temporary file
at `.claude/implementation-plans/plan_{storyNum}.md`. This unified file combines
plan-summary content and all individual tasks in the format reviewers expect. The
transient file is used only for review — the canonical output in Phase 7 is the
distributed JSON artifact format.

### Dispatch Reviewers

Dispatch **both** reviewers **in parallel** using the Agent tool:

1. **`plan-reviewer`** — verifies the plan is grounded in the actual codebase (file paths
   exist, symbols are real, task ordering is feasible, architecture is sound). Pass the
   transient unified plan file path.
2. **`test-reviewer`** — evaluates test quality, acceptance criteria strength, edge case
   coverage, mock discipline, and hidden dependencies. Pass the transient unified plan
   file path.

Launch both via the Agent tool simultaneously in a single message with two tool calls.

**Processing results:**

For the `plan-reviewer`:
- If **REPLAN**: address all BLOCKING findings, then re-run (max 1 re-run). If BLOCKINGs
  persist, surface them to the user in Phase 6.
- If **REVISE**: address SHOULD_FIX findings before proceeding.
- If **APPROVE**: no plan-reviewer changes needed.

For the `test-reviewer`:
- If **RETHINK**: address all CRITICAL findings, then re-run (max 1 re-run). If CRITICALs
  persist, surface them to the user in Phase 6.
- If **STRENGTHEN**: address SERIOUS findings before proceeding. Pay special attention to
  the "But What If..." edge case scenarios — incorporate missing edge cases into the plan's
  acceptance criteria and test scenarios.
- If **SOUND**: no test-reviewer changes needed.

After addressing findings from both reviewers, proceed to Phase 6.

Do not present the plan to the user before completing both reviews.

---

## Phase 6: User Review

Present the plan. Ask:
- "Does 'Why This Exists' capture the real motivation from the story?"
- "Is anything in the Out section that should be In, or vice versa?"
- "Are the Constraints complete — anything else that must not change?"
- "Does the Downstream Impact section cover everything you know about?"
- "Does the Risks & Rollback section capture the real risks?"
- "Are the acceptance criteria specific enough to test?"
- "Do the task boundaries make sense? Would you split or merge any?"
- "Does the Parallel Execution Schedule look right?"

**Open Questions are blocking gates.** Implementation cannot proceed until every
Open Question is resolved. If the user needs time, they can return with
`/task-decomposition [story ID]` to resume.

**Approval criteria:**
1. User confirms content is correct
2. ALL Open Questions resolved (every `- [ ]` checked)

Set Status: `Approved` if both conditions met, `Open Questions` if not.

---

## Phase 7: Finalize

### Step 1: Write Task JSON Files

Write each task as a JSON file to the artifact store:

```
~/.claude/backlog-driven-development/artifacts/
  plan-summaries/plan_{storyNum}.json    # plan-level information
  tasks/task_{storyNum}.0.json           # Task 0: contracts
  tasks/task_{storyNum}.1.json           # Task 1
  tasks/task_{storyNum}.2.json           # etc.
```

**plan_{storyNum}.json** contains all plan-level sections: Header (Date, Status,
Plan Size, Author, Repositories, Story ID, Project Spec), What We Are Building,
Why This Exists, Scope, Downstream Impact, Risks & Rollback, Parallel Execution
Schedule, Critical Reminders, and the full Appendix (Technical Context, Edge Cases,
Success Criteria, Dependencies & Assumptions, Key Decisions, Open Questions). Use
"None — all decisions resolved during planning." for Open Questions if none remain.

**task_{storyNum}.{taskNum}.json** contains the individual task with these fields:

```json
{
  "id": "task_001.0",
  "storyId": "story_001",
  "title": "Task 0: [Title]",
  "status": "PENDING",
  "assignee": null,
  "size": null,
  "implementer": "AI",
  "repository": "[repo name or path]",
  "blockedBy": ["task_001.M"],
  "covers": ["AC-01.2", "AC-01.4", "Edge: [name]"],
  "relevantFiles": [
    {"path": "src/module/file.py", "action": "create"}
  ],
  "contextToReadFirst": [
    {"path": "src/types/contracts.ts", "reason": "[why]"}
  ],
  "steps": [
    "Write failing tests based on acceptance criteria below",
    "Run tests to verify they fail (confirm RED state)",
    "Write minimal implementation to make tests pass",
    "Run tests to verify they pass (confirm GREEN state)"
  ],
  "acceptanceCriteria": [
    "GIVEN [precondition], WHEN [action], THEN [expected outcome]"
  ],
  "verificationCommand": "[single runnable command]",
  "scopeBoundaries": "[what this task owns] / [what others own]",
  "symbolDependencies": ["Task2.UserService.validateToken"],
  "executionNotes": ""
}
```

### Step 2: Update index.json

Add entries for the new plan-summary and task files to
`~/.claude/backlog-driven-development/artifacts/index.json` so other skills
can discover them.

### Step 3: Clean Up Transient Unified File (optional)

The transient unified file at `.claude/implementation-plans/plan_{storyNum}.md`
from Phase 5 can be kept as a convenience reference or deleted. Artifacts in
`~/.claude/` are not part of any git repository — no commit is needed.

Tell the user: "Next step: `/execute [story ID]` to begin implementation."

---

## Interview Rules

These rules apply to all phases where the user provides input:

- **Never silently resolve an ambiguity.** If you're filling a gap yourself, flag it.
- **Be skeptical of vague answers.** Push every vague statement into a specific,
  testable claim using the "Disagree and Commit" protocol.
- **When a decision is made, trace its ripple effects.** Does it change scope, surface
  new edge cases, or conflict with an earlier answer?
- **Assumption Ledger is non-negotiable.** Every assumption must be resolved before
  the plan is drafted.

---

## Common Failure Patterns to Avoid

- **Silent assumption resolution** — the most common failure. You filled a gap with a
  plausible guess instead of asking. If uncertain, surface it.
- **Rushing to decompose** — skipping the readiness gate or verification round because
  the story "looks complete." Stories always have hidden gaps.
- **Horizontal slicing** — splitting by layer (backend task, frontend task, DB task)
  instead of by behavior. Each task should deliver end-to-end value for one slice,
  except Task 0 (contracts).
- **Over-decomposing bugs** — a 2-task bug fix doesn't need 6 tasks. Match granularity
  to complexity.
- **Ignoring the critical path** — producing tasks that are all sequential when many
  could run in parallel. The DAG and batch computation exist to catch this.
- **Vague answers accepted** — "handle errors gracefully" is not an acceptance criterion.
  Use the Disagree and Commit protocol every time.
- **Proposing new code instead of finding existing** — always search for reusable
  implementations before proposing new ones. Cite `file:line`.
- **Epic in disguise** — the story-reviewer should catch this, but double-check: if
  decomposition produces more than 10 tasks, the story may need to be split first.

---

## Pipeline

`Story/Bug ID` → `story-reviewer gate` → `/task-decomposition` → `task JSON artifacts` → `/execute [story]` → `/ship` → `Complete`
