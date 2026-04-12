---
name: refine
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[epic ID (epic_NNN), epic file path, or epic title to look up]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
  - TodoWrite
  - Skill
description: >
  Story decomposer. Takes an approved epic, discovers architecture and
  initiative documents for context, then creates the full story breakdown.
  Analyzes the architecture's per-epic detail to identify components,
  unknowns, and integration points, then produces spike stories (when
  unknowns exist) and feature stories with GIVEN/WHEN/THEN acceptance
  criteria. Runs the story-reviewer gate on each story.
  Best used AFTER an epic is approved and AFTER /architecture.
  Do NOT use for creating epics (use /epic). Do NOT use for single
  standalone stories (use /story directly). Do NOT use for task
  decomposition (use /task-decomposition).
---

# Story Decomposer

> Takes an approved epic and its architecture, then produces the
> complete story breakdown — spike stories for unknowns, feature stories
> for capabilities. The output is a backlog of sprint-ready stories,
> each with GIVEN/WHEN/THEN acceptance criteria.

Refinement bridges strategic planning and tactical execution. The epic
defines outcomes. Architecture defines constraints and components.
Refinement makes both actionable by decomposing them into stories that
respect architectural boundaries and deliver vertical slices of value.

**Refine creates the decomposition.** It analyzes the epic's scope and
the architecture's per-epic detail to propose and draft stories. It does
not require a pre-existing story map.

**Architecture is the primary decomposition driver.** When an
architecture document exists with per-epic component detail, the story
breakdown follows the component structure, unknowns, and integration
points. When no architecture exists, refine proposes a breakdown from
the epic's scope alone.

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **Epic ID** (matches `epic_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/epics/{id}.json`.
   Check `index.json` for existing stories under this epic — if some
   exist, enter **Resumption Mode**.
2. **Existing epic file path** (points to an artifact JSON file):
   Read the epic. Check `index.json` for existing stories — if some
   exist, enter **Resumption Mode**.
3. **Plain description**: Refine requires an existing epic. Tell the
   user:
   > "Refine works from an existing epic — it creates the story
   > breakdown. If you haven't created the epic yet, start with `/epic`.
   > If you have the epic, provide its ID (e.g., `epic_001`)."
4. **No input**: Read `index.json` from
   `~/.claude/backlog-driven-development/artifacts/`. If epics exist,
   ask which to refine. If none, redirect to `/epic`.

---

## Phase 1: Load Context

### Step 1: Load the Epic

Read the epic document and extract:
- Goal — what outcome this epic delivers
- Success metric — how we measure success
- Rough scope — what's included
- Out of scope — what's excluded
- Definition of done — what complete looks like
- Why this is [N] — ordering rationale and dependencies

### Step 2: Validate Epic Readiness

Check that the epic is ready for refinement:

- Is `status` set to `TODO`? If `BACKLOG`, warn:
  > "This epic hasn't been moved to TODO yet. Refinement works best from
  > a TODO epic. Proceed anyway?"
- Does it have a clear goal (not just "build X")?
- Is the scope specific enough to decompose?

### Step 3: Discover Architecture Document

Architecture provides the primary decomposition signal — component
boundaries, unknowns, schemas, and error handling strategies.

**Discovery:** Read `index.json` and search the `architectures` array:

1. Filter by `epicIds` containing this epic's ID — most specific match
2. If no match, filter by `initiativeId` matching the epic's parent
   initiative — picks up initiative-wide architectures
3. If the epic is standalone (no parent initiative), no architecture
   will be found via index. Check conversation context.
4. If conversation context includes an architecture, use that

**If found:** Extract the per-epic section for this epic:
- Components involved and their responsibilities
- Component detail (API shapes, technology specifics)
- Unknowns and spikes
- State / data model
- Error handling strategy
- What's deferred to later epics

Present a brief summary:

> "I found the architecture document. For this epic, it details [N]
> components: [list]. There are [N] unknowns flagged for spiking.
> I'll use this to drive the story breakdown."

**If not found:**

> "No architecture document found. I'll propose stories from the epic's
> scope alone. Consider running `/architecture` first for a more
> grounded decomposition."

### Step 4: Discover Initiative Document

If the epic has a `parentInitiative`, read the initiative from
`~/.claude/backlog-driven-development/artifacts/initiatives/{initiativeId}.json`.
Extract problem statement, success metrics, and guardrails for context.

---

## Phase 1B: Upstream Artifact Status Check

After loading context, check the status of all upstream artifacts
before proceeding.

### Step 1: Check for NEEDS_REFINEMENT / needs-revision

For each loaded document (epic, architecture, initiative), read its
`Status` field.

If ANY upstream artifact has `status: "NEEDS_REFINEMENT"`:

> "WARNING: Upstream artifact needs refinement:
>
> - **[artifact type]** `{id}`: Status is NEEDS_REFINEMENT
>   Reason: [revisionReason content]
>
> Stories derived from artifacts that need refinement may need rework.
> Would you like to:
>
> 1. Stop and address the refinement first
> 2. Proceed anyway (stories may need rework)"

If the user chooses to stop, tell them which skill to run.

### Step 2: Flag Upstream Issues During Work

During story decomposition, if you discover that an upstream artifact
is inadequate — e.g., the epic's scope doesn't cover a necessary
capability, the architecture doesn't account for a cross-cutting
concern, or acceptance criteria conflict — you MUST flag it:

1. **Mark the artifact** as `NEEDS_REFINEMENT` with a `revisionReason`
2. **Inform the user**:

   > "During story decomposition, I found that [artifact type] needs
   > refinement:
   >
   > **Issue**: [specific problem]
   > **Impact**: [how this affects the stories]
   >
   > I've updated `{id}` status to NEEDS_REFINEMENT. Address with
   > `/[skill] {id}` after we finish, or stop now."

3. **Continue** if the user chooses to proceed

---

## Phase 2: Propose Story Decomposition

**Goal: Analyze the epic and architecture to propose the full story
breakdown, then confirm with the user.**

### Step 1: Identify Stories

When architecture exists, derive stories from:

1. **Unknowns → Spike story.** If the architecture's per-epic section
   lists unknowns or spikes, the first story should be a time-boxed
   spike that resolves them. Spike stories have a different format
   (see Spike Story Format below).

2. **Components → Feature stories.** Each component the epic touches
   typically becomes one story. The architecture's component detail
   provides scope, API shape, and edge cases for each.

3. **Integration → Orchestration story.** If the epic involves
   connecting multiple components into a pipeline or workflow, the
   integration/orchestration layer is its own story that depends on
   the component stories.

4. **State / data → State story.** If the architecture defines a
   schema or state model, tracking state across the pipeline is often
   its own story (especially if it needs to be independently testable).

When no architecture exists, derive stories from:

1. **Epic scope items** — each major capability in the rough scope
2. **Dependency analysis** — what must exist before what
3. **Risk isolation** — high-risk areas get their own story

### Step 2: Determine Order

Order stories by dependency chain:

- Spike stories first (they validate assumptions other stories depend on)
- Foundation stories next (components that produce output other stories consume)
- Stories that can be built independently in parallel
- Integration stories last (they wire together the components)

### Step 3: Present the Decomposition

> "Based on the epic and architecture, I'd break this into [N] stories:
>
> **Story 0: Spike — [title]** (if unknowns exist)
> [one-sentence summary of what needs investigation]
>
> **Story 1: [title]**
> [one-sentence summary]
>
> **Story 2: [title]**
> [one-sentence summary]
>
> ...
>
> The ordering follows [dependency chain / risk sequencing]. Does this
> decomposition make sense? Would you add, remove, or reorder anything?"

Wait for user confirmation before drafting.

---

## Phase 3: Fill Gaps and Draft Stories

### Step 1: Identify Gaps

For each proposed story, check whether the epic + architecture provide
enough to draft:
- User story statement (who, what, why)
- Context
- Acceptance criteria (happy path + edge cases)
- Out of scope
- Dependencies

Most gap-filling information comes from the architecture's component
detail. Ask the user only for things that can't be inferred.

### Step 2: Ask Targeted Questions

If gaps exist, batch questions efficiently:

> "I have enough from the architecture to draft most of these. A few
> questions:
>
> - For Story 1: [specific question about behavior or edge case]
> - For Story 3: [specific question about error handling]"

Minimize questions. Infer where you can, confirm where you must.

### Step 3: Draft All Stories

Draft each story using the format below. Write all stories, then
present them together.

### Feature Story Format

```markdown
Story [N]: [Short descriptive title]

As a [specific persona with context],
I want [one specific capability],
so that [real business/user outcome].

Context: [2-3 sentences of background. Reference architecture decisions,
spike findings, or epic context that inform this story.]

Acceptance Criteria:

GIVEN [precondition]
WHEN [action]
THEN [observable outcome]

GIVEN [precondition]
WHEN [action]
THEN [observable outcome]

[Continue for all acceptance criteria — happy path, edge cases, failure
modes, boundary conditions. Do not separate into subsections. Aim for
5-9 ACs per story.]

Out of scope: [What this story does NOT cover. Reference which other
story handles excluded items when applicable.]

Dependencies: [What must exist before this story can be built. Reference
specific stories by number.]
```

**Drafting rules for feature stories:**

- **Persona**: Use the persona that genuinely benefits. For user-facing
  stories, this is the end user. For infrastructure/pipeline stories,
  "As a developer building [system]" is valid when the story genuinely
  serves developer needs.
- **Acceptance criteria**: GIVEN/WHEN/THEN format. Include happy path,
  edge cases, failure modes, and boundary conditions in a single flat
  list. Aim for 5-9 ACs per story. Each AC must pass the Two-Engineers
  Test: two engineers reading it independently would implement the same
  behavior.
- **Edge cases to always consider**: empty/null inputs, first-time
  startup, daemon restart during processing, corrupted or missing input,
  rapid succession of events, resource cleanup on success and failure.
- **Out of scope**: Must reference what's excluded and which story
  handles it. Prevents scope confusion.
- **Dependencies**: Reference story numbers. Stories with no
  dependencies should say so.

### Spike Story Format

```markdown
Story 0: Spike — [Title describing what's being investigated]

As a [developer/engineer] [building/setting up] [system context],
I want to [confirm/validate/investigate specific unknowns],
so that [remaining stories are built on verified assumptions / blocking
risks are identified before investing in production code].

Questions to answer:

[Numbered list of specific, answerable questions. Each question should
produce a concrete finding. Derive these from the architecture's
Unknowns and Spikes section.]

Definition of done:

[What "complete" looks like for a spike — focused on knowledge output:]
- Every question above has a documented answer with evidence
- Invalidated assumptions are flagged with proposed alternatives
- Findings are written into the architecture document
- Blockers are escalated immediately

Timebox: [Duration — typically 1-3 days. A spike that takes longer than
3 days is probably scoped too broadly.]

[Note: The output is knowledge, not production code. All code written
during the spike is throwaway.]
```

---

## Phase 4: Story Review

### Step 1: Run the Story Reviewer Gate

Before presenting stories to the user, run the `story-reviewer` agent
on each story.

- If **NOT_READY**: Fix STRUCTURAL issues silently. Present DECISIONAL
  and BLOCKING findings to the user and work through them.
- If **READY** (with SHOULD_FIX items): Present items alongside the
  walkthrough.

### Step 2: User Walkthrough

Present all stories together:

> "Here are the [N] stories for [Epic title], ordered by dependency
> chain:
>
> [Full story documents]
>
> Does the breakdown feel right? Any stories to add, remove, split,
> merge, or reorder?"

Keep the walkthrough concise. Focus on judgment calls and anything
you're unsure about.

Iterate until the user approves all stories.

---

## Phase 5: Save Stories

### Step 1: Ensure Artifact Directory Exists

```bash
mkdir -p ~/.claude/backlog-driven-development/artifacts/{initiatives,epics,architectures,stories,tasks,plan-summaries}
```

If `index.json` does not exist, create it with the empty scaffold.

### Step 2: Generate IDs

Read `index.json`. For each story, find the highest numeric suffix
among existing story IDs and increment. Zero-pad to 3 digits.

### Step 3: Write the Artifacts

Write each story as JSON to:
`~/.claude/backlog-driven-development/artifacts/stories/{id}.json`

Use the story JSON schema from the artifacts skill reference. Set
`parentEpic` to the epic ID.

### Step 4: Update the Index

For each story, add an entry to the `stories` array in `index.json`:

```json
{ "id": "story_001", "title": "...", "status": "TODO", "type": "feature", "epicId": "epic_001", "initiativeId": "init_001", "order": 1, "taskCount": 0 }
```

Add each story ID to the parent epic's `storyIds` array in `index.json`.

Update `lastModified`. Write `index.json` back.

### Next Steps

> "Stories saved. Next steps:
>
> Start with the Spike story if one exists — the spike must complete
> before dependent stories can begin.
>
> For each story, run `/task-decomposition {story_id}` to break it
> into implementation tasks, then `/execute` to build it.
>
> Recommended order:
> 1. `/task-decomposition {spike_story_id}` (spike)
> 2. `/task-decomposition {story_id}`
> ...
>
> The typical flow is: `/refine` → `/task-decomposition` → `/execute`
> → `/ship`"

---

## Resumption Mode

When `index.json` shows existing stories for this epic:

1. Read existing stories by filtering `index.json` stories where
   `epicId` matches, then load each from `stories/{id}.json`
2. Present what exists:
   > "This epic already has [N] stories:
   > - [Story 1 title]
   > - [Story 2 title]
   >
   > Would you like to add more stories, revise existing ones, or is
   > the epic fully decomposed?"
3. If more stories are needed, discover context (Phase 1) and continue
   from Phase 2

---

## Conversation Rules

- **Be investigative, not bureaucratic.** Help the user think through
  the decomposition, don't march through a checklist.
- **Ask the fewest questions possible.** The architecture and epic
  provide most of what you need.
- **Push back on scope creep.** If a story grows beyond one sprint or
  spans multiple unrelated concerns, name it: "That's becoming two
  stories. Let's split it."
- **Guard vertical slicing.** When you see "backend story" or "database
  story" emerging, redirect: "That's a horizontal slice. Let's
  restructure as a vertical slice that delivers end-to-end value."
  Exception: pipeline-stage stories (detect → classify → integrate)
  are valid vertical slices when each stage produces independently
  testable output.
- **Respect architecture boundaries.** Stories should not violate
  component boundaries or contradict architectural decisions.
- **Trace to the outcome.** Every story should connect back to the
  epic's goal. If a story doesn't serve the goal, question whether it
  belongs in this epic.

---

## Common Anti-Patterns to Catch

| Anti-Pattern | Signal | Response |
|---|---|---|
| Horizontal slicing | "Backend story," "Frontend story," "DB story" | Restructure as vertical slices |
| Foundational stories | "Set up the database schema" | Merge into first story that needs it, or make it the state tracker story |
| Too many stories | >12 stories | Epic needs splitting |
| Too few stories | <3 stories | This might be a single story |
| Scope creep | New capabilities emerge during refinement | Pause, check against epic scope |
| Ignoring architecture | Story contradicts architectural decision | Restructure to respect the decision |
| Missing spike | Architecture flags unknowns but no spike story | Add spike as Story 0 |
| Over-specified spike | Spike has acceptance criteria instead of questions | Reformat as questions + timebox |

---

## Relationship to Other Artifacts

```
/initiative  -->  Initiative document
    |
    +-- /epic  -->  Epic document (goal, scope, DoD)
         |
         +-- /architecture  -->  Architecture document
         |                       System overview + per-epic detail
         |
         +-- /refine  -->  Story decomposition (this skill)
                 |
                 | reads architecture + epic to create stories
                 |
                 +-- Story 0: Spike (if unknowns exist)
                 +-- Story 1: [feature]
                 +-- Story N: [feature]
                        |
                        v
                 /task-decomposition  -->  tasks (per story)
                        |
                        v
                 /execute  -->  TDD implementation
                        |
                        v
                 /ship  -->  PR
```
