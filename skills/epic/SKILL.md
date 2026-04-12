---
name: epic
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[initiative path, feature area description, or existing epic to refine]"
description: >
  Epic creator. When given an initiative, analyzes it and produces a
  complete set of epics with ordering rationale, dependency chains, and
  risk sequencing. When given a standalone description, produces a single
  epic. Each epic defines a goal, success metric, scope, and definition
  of done — ready for /architecture and /refine to decompose into stories.
  Epics are stored as JSON artifacts in
  ~/.claude/backlog-driven-development/artifacts/.
  Do NOT use for single stories (use /story). Do NOT use for task
  decomposition (use /task-decomposition). Do NOT use for story
  refinement (use /refine after the epic is approved).
---

# Epic Creator

> Produces well-defined epics from an initiative or standalone description.
> When working from an initiative, analyzes the full scope and produces
> all epics at once with ordering rationale. When standalone, produces a
> single epic through focused conversation.

An epic is a **container of related work** unified by a single outcome.
It captures the "what" and "why" at a strategic level; stories (created
downstream by `/refine`) capture the "what" at an implementable level.

**Trust the user.** If someone calls `/epic`, they've decided this is
epic-level work. Do not second-guess scope or redirect to `/story`.
Solo projects, personal tools, single-user apps — all valid contexts
for epics.

**Epics define outcomes, not outputs.** "Build a notification system" is
an output. "Users never miss a time-sensitive event" is an outcome.

**No story maps at this stage.** Epics define the container and its
boundaries. Story decomposition happens in `/refine`.

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **View request** — `$ARGUMENTS` contains an epic ID (`epic_NNN`)
   AND the word "view" (in any order: `epic_001 view`, `view epic_001`).
   Enter **View Mode**.
2. **Delete request** — `$ARGUMENTS` contains an epic ID (`epic_NNN`)
   AND the word "delete" (in any order: `epic_001 delete`,
   `delete epic_001`). Enter **Delete Mode**.
3. **Initiative ID** (matches `init_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/initiatives/{id}.json`.
   Enter **Initiative Mode** — analyze the initiative and produce all
   epics at once. Proceed to Phase 1A.
4. **Epic ID** (matches `epic_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/epics/{id}.json`.
   Enter **Refinement Mode** — evaluate the existing epic and guide the
   user through strengthening it.
5. **Epic ID with linking phrase** (e.g., `epic_001 link to init_001`
   or `epic_001 move to init_002`): Enter **Link/Move Mode** — update
   the epic's `parentInitiative` to the specified initiative. If the
   epic was previously linked to a different initiative, remove it from
   the old initiative's `epicIds` and add to the new one. Update both
   the epic JSON file and `index.json`. Confirm the change to the user.
6. **Existing epic file path** (points to an existing artifact JSON
   file): Enter **Refinement Mode**.
7. **Plain description** (no initiative context): Use as the seed for a
   single epic. Read `index.json` and check for existing initiatives.
   If initiatives exist, suggest linking:
   > "I found these initiatives — does this epic belong to one of them?
   > 1. `{init_id}`: [title]
   > 2. `{init_id}`: [title]
   > 3. **Standalone** — no initiative (you can link it later)
   >
   > Hint: If you expect to create multiple related epics, consider
   > running `/initiative` first to group them."
   Proceed to Phase 1B.
8. **No input**: Read `index.json`. If initiatives exist, ask the user
   which initiative to create epics from (or if they want a standalone
   epic). If none found, ask what they want to build. Include the hint:
   > "Hint: If you expect multiple related epics, start with
   > `/initiative` to create an initiative first."

---

## Phase 1A: Initiative Mode — Analyze and Decompose

**Goal: Read the initiative, identify the natural epic boundaries, and
propose the full decomposition.**

### Step 1: Load and Understand the Initiative

Read the initiative document in full. Extract:
- Problem statement and who it affects
- Proposed solution direction
- Success metrics and guardrail metrics
- Scope (in and out)
- Risks and dependencies
- Milestones (these often hint at epic boundaries)

### Step 2: Discover Existing Epics

Before proposing new epics, check if this initiative already has epics:

1. Read `index.json` and filter epics where `initiativeId` matches this
   initiative

**If existing epics are found:**

> "This initiative already has [N] epics:
>
> 1. **[Epic title]** — [goal summary] — Status: [status]
> 2. **[Epic title]** — [goal summary] — Status: [status]
>
> Would you like to:
> 1. **Add a new epic** — I'll analyze the initiative for gaps not
>    covered by existing epics
> 2. **Modify an existing epic** — pick one to refine
> 3. **Re-analyze the full decomposition** — propose all epics fresh
>    (existing epics are preserved until you approve replacements)"

If the user chooses to add a new epic: proceed to Step 4 (Identify
Epic Boundaries) but exclude scope already covered by existing epics.
Propose only new epics that fill gaps.

If the user chooses to modify: enter Refinement Mode for the selected
epic.

If the user chooses to re-analyze: proceed as if no epics exist, but
note which existing epics are being replaced.

**If no existing epics found:** Proceed to Step 4.

### Step 4: Identify Epic Boundaries

Look for natural decomposition points:
- **Pipeline stages**: If the solution is a pipeline (input → process →
  output), each stage is often an epic.
- **Milestone boundaries**: Initiative milestones frequently map to epics.
- **Risk isolation**: High-risk components should be their own epic so
  failure doesn't cascade.
- **Dependency chains**: If B depends on A, they should be separate epics
  with A first.
- **Integration boundaries**: Where the system touches external systems
  or APIs, that integration is often its own epic.
- **User-facing vs. operational**: The core functionality and the
  reliability/operational layer are usually separate epics.

### Step 4: Propose the Decomposition

Present the proposed epic decomposition to the user:

> "Based on the initiative, I'd break this into [N] epics:
>
> 1. **[Epic title]** — [one-sentence goal]
> 2. **[Epic title]** — [one-sentence goal]
> 3. **[Epic title]** — [one-sentence goal]
>
> The ordering is based on [dependency chain / risk sequencing / etc.].
>
> Does this decomposition make sense? Would you split or merge anything
> differently?"

### Step 5: Fill Gaps

For each proposed epic, check whether the initiative provides enough
information to draft all sections of the template. If gaps exist, ask
targeted questions — but batch them efficiently:

> "I have enough from the initiative to draft most of these. A few
> questions to fill gaps:
>
> - For Epic 2 (classification): What should happen when the LLM isn't
>   confident about the folder? Route to an inbox, skip it, or ask?
> - For Epic 4 (daemon): What's your threshold for acceptable RAM usage
>   while idle?"

Ask the fewest questions possible. Infer where you can, confirm where
you must.

### Step 6: Draft All Epics

Once the decomposition is confirmed and gaps are filled, draft all epics
using the template in [epic-template.md](references/epic-template.md).
Proceed to Phase 3.

---

## Phase 1B: Standalone Mode — Single Epic

**Goal: Understand what the user wants to build and produce a single
epic.**

### Step 1: Discover Parent Initiative (Optional)

Search for existing initiatives:
1. Read `index.json` and check the `initiatives` array. If initiatives
   exist, ask if this epic belongs to one of them.

If a parent initiative is found and relevant, load it for context but
don't switch to Initiative Mode — the user asked for a single epic.

### Step 2: Gap Analysis

Read the user's description. Map it against the epic template sections:
- Goal — what outcome does this deliver?
- Success metric — how will you know it worked?
- Rough scope — what's included?
- Out of scope — what's excluded?
- Definition of done — what does complete look like?

Classify each as covered, partially covered, or missing.

### Step 3: Investigative Conversation

Fill gaps through focused questioning. Same rules as the initiative
skill:
- Ask 1-2 questions at a time
- Be specific, not generic
- Infer where you can, confirm where you must
- Push back on vagueness
- Minimize the number of questions

**What to ask about (only for gaps):**

**Goal gaps:**
- What changes for the user once this exists? What becomes possible or
  stops being painful?
- How is this different from just a feature? What's the outcome?

**Metric gaps:**
- How will you know this worked? What's the number or threshold?
- Is there an existing baseline you're improving from?

**Scope gaps:**
- What would someone assume is included but isn't?
- What's the boundary between this epic and adjacent work?

**Definition of done gaps:**
- If you could demo this to someone, what would you show them?
- What's the end-to-end test that proves this epic is complete?

### Step 4: Draft the Epic

Once gaps are filled, draft using the template. Proceed to Phase 3.

---

## Phase 1C: Upstream Artifact Status Check

After loading context (Initiative Mode or Standalone Mode), check the
status of all upstream artifacts before proceeding. If no parent
initiative was loaded, skip this phase.

### Step 1: Check for Needs-Revision

For the loaded initiative, read its `Status` field.

If the initiative has `Status: Needs-Revision`:

> "WARNING: The parent initiative needs revision:
>
> - **Initiative** `{id}`: Status is Needs-Revision
>   Reason: [Revision-Reason content]
>
> Creating epics from an initiative that needs revision may produce
> epics that need rework. Would you like to:
>
> 1. Stop and address the initiative first (`/initiative {id}`)
> 2. Proceed anyway (epics may need rework)"

If the initiative has `Status: Proposed` (not yet Approved):

> "Note: The parent initiative is still in Proposed status. You may
> want to finalize it first. Proceed anyway?"

If no initiative context exists, skip this phase.

### Step 2: Flag Upstream Issues During Work

During epic creation, if you discover that the initiative is inadequate
— e.g., scope doesn't cover a capability the epic needs, success
metrics conflict, or constraints are missing — you MUST flag it:

1. **Mark the initiative** as `Needs-Revision` with a `Revision-Reason`
2. **Inform the user**:

   > "While creating epics, I found that the initiative needs revision:
   >
   > **Issue**: [specific problem]
   > **Impact**: [how this affects the epics]
   >
   > I've marked `{id}` as Needs-Revision. Address with
   > `/initiative {id}` after we finish, or stop now."

3. **Continue** if the user chooses to proceed

---

## Phase 2: Drafting Rules

Whether in Initiative Mode or Standalone Mode, apply these rules when
drafting:

- Set `Status: BACKLOG`.
- **Goal** must describe an outcome, not a feature list. 1-2 sentences.
- **Success Metric** must have a specific number or threshold. Keep to
  1-2 metrics maximum. This is an epic, not a dashboard.
- **Why This Is [N]** (Initiative Mode only) must explain the dependency
  chain, risk sequencing, or logical ordering. What does this epic
  depend on? What does it unblock?
- **Rough Scope** must be a paragraph — specific enough to know what's
  in, not so detailed it prescribes implementation. Describe capabilities
  and behaviors, not tasks.
- **Out of Scope** must have at least 1-2 specific exclusions. Reference
  which other epic handles excluded items when applicable.
- **Definition of Done** must be a concrete sentence that someone could
  verify by watching a demo. Describe the end-to-end outcome.

Scale to context. A small epic for a personal tool needs less depth than
a major cross-team effort. Match the document to the ambition.

---

## Phase 3: Epic Review

### Step 1: Run the Epic Reviewer Gate

Before presenting epics to the user, run the `epic-reviewer` agent on
each draft. This agent checks structural completeness, scope boundaries,
and common anti-patterns.

- If the verdict is **NOT_READY**: Fix STRUCTURAL issues silently.
  Present BLOCKING/SHOULD_FIX findings to the user and work through
  them.
- If the verdict is **READY** (possibly with SHOULD_FIX items): Present
  SHOULD_FIX items alongside the walkthrough.

### Step 2: User Walkthrough

Present the draft(s) to the user. For Initiative Mode, present all epics
together with their ordering rationale:

> "Here are the [N] epics for [initiative name]. They're ordered by
> dependency chain — each builds on the previous:
>
> [Full epic documents]
>
> Does the decomposition feel right? Any epics to split, merge, reorder,
> or adjust?"

Keep the walkthrough concise. The user can read the documents — focus on
judgment calls and anything you're unsure about.

Iterate until the user approves. Once approved, set `Status: TODO`
on each epic.

### Step 3: Check for NEEDS_REFINEMENT Status

If an epic was loaded with `status: "NEEDS_REFINEMENT"`, present the
`revisionReason` before starting the walkthrough:

> "This epic was flagged for refinement by a downstream skill:
>
> **Reason**: [revisionReason content]
>
> Let's address this before proceeding."

After addressing, set `Status: TODO`.

---

## Phase 4: Save the Epics

### Step 1: Ensure Artifact Directory Exists

```bash
mkdir -p ~/.claude/backlog-driven-development/artifacts/{initiatives,epics,architectures,stories,tasks,plan-summaries}
```

If `~/.claude/backlog-driven-development/artifacts/index.json` does not
exist, create it with the empty scaffold (see artifacts skill reference).

### Step 2: Generate IDs

Read `index.json`. For each epic, find the highest numeric suffix among
existing epic IDs and increment. Zero-pad to 3 digits. First epic is
`epic_001`.

### Step 3: Write the Artifacts

Write each epic as JSON to:
`~/.claude/backlog-driven-development/artifacts/epics/{id}.json`

Use the epic JSON schema from the artifacts skill reference. Set
`parentInitiative` to the initiative ID (or `null` for standalone).

### Step 4: Update the Index

For each epic, add an entry to the `epics` array in `index.json`:

```json
{ "id": "epic_001", "title": "...", "status": "TODO", "creator": "[You]", "initiativeId": "init_001", "order": 1, "createdAt": "...", "dueDate": null, "storyIds": [], "comments": [] }
```

If the epic has a parent initiative, add the epic ID to the initiative's
`epicIds` array in `index.json`.

Update `lastModified` to the current ISO 8601 timestamp.
Write `index.json` back.

### Next Steps Guidance

After saving, present next steps:

> "Epics saved. Next steps for each epic:
>
> - `/architecture {initiative_id}` — if the epic needs architectural
>   decisions before story refinement
> - `/refine {epic_id}` — to decompose the epic into fully-refined
>   user stories
>
> Recommended order:
> 1. **[Epic 1]**: `/refine {epic_id}`
> 2. **[Epic 2]**: `/refine {epic_id}`
> ...
>
> The typical flow is: `/epic` → `/architecture` (optional) → `/refine`"

**Do NOT auto-invoke `/refine` or `/architecture`.** The user runs each
step manually.

---

## View Mode

When triggered (Input Handling case 1):

1. Read the epic from `~/.claude/backlog-driven-development/artifacts/epics/{id}.json`
2. Read `index.json` to resolve relationships
3. Display in this format:

```
## Epic: {title}
**ID:** {id}  |  **Status:** {status}  |  **Order:** {order}  |  **Created:** {createdAt}

### Relationships
- **Parent Initiative:** {parentInitiative} — "{initiative title}" (or "None — standalone")

### Goal
{goal}

### Success Metric
{successMetric}

### Why This Order
{whyThisOrder}

### Rough Scope
{roughScope}

### Out of Scope
{outOfScope}

### Definition of Done
{definitionOfDone}

### Stories
| ID | Title | Type | Status | Tasks (P/IP/C) |
|----|-------|------|--------|----------------|
| {story_id} | {title} | {type} | {status} | {PENDING}/{IN_PROGRESS}/{DONE} |
...

**Overall Progress:** {total tasks} tasks — {N} PENDING, {N} IN_PROGRESS, {N} DONE
```

4. **Stop.** Do not enter any other phase or mode.

---

## Delete Mode

When triggered (Input Handling case 2):

### Step 1: Safety Check

1. Read `index.json` and find all stories where `epicId` matches this epic ID
2. For each story, find all tasks where `parentStory` matches
3. Check each task's `status` field
4. If ANY task has status `IN_PROGRESS` or `DONE`:

> "Cannot delete `{epic_id}`: work is in progress or completed on downstream tasks.
>
> Blocking tasks:
> - `{task_id}` (in `{story_id}`): "{title}" — status: {status}
>
> Resolve these tasks first (reset to PENDING or delete them individually)."

**Stop.** Do not proceed with deletion.

### Step 2: Cascade Preview

If all descendant tasks are `PENDING`, `BLOCKED`, or there are no tasks:

> "You are about to delete epic `{id}`: "{title}"
>
> This will remove:
> - The epic file
> - {N} story/stories: {list story IDs}
> - {N} task(s) across those stories
> - {N} plan summary/summaries
>
> Type "confirm" to proceed."

Use AskUserQuestion to get confirmation.

### Step 3: Execute Deletion

On "confirm":

1. For each child story, run the story deletion cascade:
   - Delete task files: `tasks/task_{storyNum}.*.json`
   - Delete plan summary: `plan-summaries/plan_{storyNum}.json` (if exists)
   - Delete story file: `stories/{story_id}.json`
2. Delete the epic file: `epics/{id}.json`
3. Update `index.json`:
   - Remove all deleted task entries from the `tasks` array
   - Remove all deleted story entries from the `stories` array
   - Remove the epic entry from the `epics` array
   - If `parentInitiative` is not null, remove this epic ID from the
     parent initiative's `epicIds` array
   - Remove this epic ID from any architecture's `epicIds` array
   - Update `lastModified`
4. Write `index.json`

### Step 4: Confirm

> "Deleted epic `{id}`: "{title}"
> Also removed: {N} story/stories, {N} task(s){, N plan summary/summaries}."

---

## Refinement Mode

When an existing epic is loaded (Input Handling cases 4 and 5):

1. Read the existing epic content
2. Run the `epic-reviewer` agent on it
3. Present findings:
   > "I reviewed the existing epic and found these areas to strengthen:
   > - [finding 1]
   > - [finding 2]
   > Let's work through these together."
4. Enter the gap-filling conversation but only for gaps identified —
   do not re-interview for things already well-defined
5. Proceed through Phase 3-4 as normal
6. If the epic is already complete: tell the user and point them to
   `/architecture` or `/refine`

---

## Conversation Rules

- **Be investigative, not bureaucratic.** Help the user think through
  their idea, don't march through a checklist.
- **Ask the fewest questions possible.** Infer from context, confirm
  when needed.
- **One or two questions at a time.** Build on answers.
- **Push back on vagueness.** "Improve the workflow" → "Improve it how?
  What's the measurable change?"
- **Guard the boundary between epic and story.** When the user dives
  into acceptance criteria or implementation details: "That detail
  belongs in story refinement. Let's capture the capability here and
  flesh it out in `/refine`."
- **Guard the boundary between epic and initiative.** When multiple
  unrelated outcomes appear: "These are separate epics. Let's focus on
  one outcome per epic."

---

## Common Anti-Patterns to Catch

| Anti-Pattern | Signal | Response |
|---|---|---|
| Feature list epic | Outcome is "build X, Y, Z" | Reframe as outcome: what changes for the user? |
| Unmeasurable success | "Users are happy," "system works well" | Push for specific metric with threshold |
| No out-of-scope | Everything is in scope | "What would make this 2x bigger? Exclude those." |
| Horizontal slicing | Epics split by technical layer | Restructure around outcomes or pipeline stages |
| Solution over-specced | Epic reads like a PRD | "Implementation details belong in stories." |
| Missing failure modes | Only happy path considered | "What goes wrong? What happens when it does?" |

---

## Relationship to Other Artifacts

```
Validated idea / opportunity
    |
/initiative  -->  Initiative document (investment areas)
    |
    +-- /epic  -->  Epic documents (this skill)
         |          One per investment area, ordered by dependencies
         |
         +-- /architecture  -->  Architecture (optional)
         |
         +-- /refine  -->  Story decomposition
         |       Invokes /story for each story
         |
         +-- /task-decomposition  -->  tasks (per story)
         |
         +-- /execute  -->  TDD implementation
         |
         +-- /ship  -->  PR

Backflow: any downstream skill can mark upstream artifacts as
Needs-Revision with a reason. The upstream skill checks for this
status when re-invoked.
```
