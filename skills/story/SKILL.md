---
name: story
effort: high
model: opus
argument-hint: "[feature idea, rough description, or existing story to refine]"
description: >
  Conversational user story creator. Guides the user through crafting a single,
  well-formed user story with INVEST-quality acceptance criteria and edge cases.
  Pushes back when the request is really an epic or spans multiple stories.
  Saves the story as a JSON artifact in ~/.claude/backlog-driven-development/artifacts/.
  Do NOT use for decomposing stories into tasks (use /task-decomposition).
  Do NOT use for ad-hoc code changes (use Claude's plan mode).
---

# User Story Creator

> Interactive conversation that produces a single, high-quality user story.
> Expect 10-20 minutes of back-and-forth. The output is a story ready for
> `/task-decomposition` or direct backlog grooming.

This skill embodies the **3 C's** of user stories (Ron Jeffries):

- **Card** — a concise placeholder for a conversation, not a requirements doc
- **Conversation** — the dialogue between you and the user that fills in the
  details the card cannot capture
- **Confirmation** — acceptance criteria that define when the story is done

The conversation IS the skill. A story written without dialogue is a guess.

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **View request** — `$ARGUMENTS` contains a story ID (`story_NNN`)
   AND the word "view" (in any order: `story_001 view`, `view story_001`).
   Enter **View Mode**.
2. **Delete request** — `$ARGUMENTS` contains a story ID (`story_NNN`)
   AND the word "delete" (in any order: `story_001 delete`,
   `delete story_001`). Enter **Delete Mode**.
3. **Story ID** (matches `story_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/stories/{id}.json`.
   Enter **Refinement Mode** — evaluate the existing story and guide
   the user through improving it rather than starting from scratch.
4. **Existing story file path** (points to an existing artifact JSON
   file): Enter **Refinement Mode** — read the story and strengthen it.
5. **Plain description with epic context** (e.g., `"add retry logic"
   epic:epic_001` or description provided while an epic ID is in the
   conversation): Load the epic from
   `~/.claude/backlog-driven-development/artifacts/epics/{epicId}.json`
   for context (goal, scope, success metric). The story's `parentEpic`
   will be set to this epic ID. Proceed to Phase 1 with epic context.
6. **Plain description** (no epic context): Use as the seed for a
   story. Read `index.json` and check for existing epics. If epics
   exist, try to infer which epic this story relates to based on the
   description and epic goals/scopes. Suggest the best match:
   > "Based on your description, this sounds like it could belong to:
   > 1. `{epic_id}`: [title] — [goal summary]
   > 2. **Standalone** — no epic (you can link it later)
   >
   > Hint: If you expect to create multiple related stories, consider
   > running `/epic` first to group them."
   Set `parentEpic` accordingly. Proceed to Phase 1.
7. **No input**: Read `index.json`. If epics exist, ask if the story
   belongs to one of them or is standalone. Include the hint:
   > "Hint: If you expect multiple related stories, start with `/epic`
   > to create an epic first."
   Then ask what feature or behavior they want to describe.

---

## Phase 1: Understand the Request

**Goal: Determine whether this is a story, an epic, or something else entirely.**

Start by listening. Ask the user to describe what they want in their own words.
Do not jump to format — let them talk first.

After hearing the initial description, run the **Scope Sniff Test** before
doing anything else:

### Scope Sniff Test

Check for epic signals. If **two or more** of these are true, push back:

- The description contains multiple unrelated user goals joined by "and"
- It spans more than one user persona
- It would take more than one sprint to build (even roughly)
- It touches 3+ independent system boundaries or services
- You cannot state a single "done" condition in one sentence
- The user says "and also" or "while we're at it" more than once

**If epic detected:**

> "What you're describing sounds like it contains multiple stories. A single
> user story should deliver one coherent behavior change for one persona.
> Here's how I'd suggest splitting this:
>
> 1. [Story A — one-sentence summary]
> 2. [Story B — one-sentence summary]
> 3. [Story C — one-sentence summary]
>
> Which one would you like to write first? We can do the others after."

Do NOT proceed with an epic-sized request. The user must pick one story to
focus on. If they resist splitting, explain: "An oversized story leads to vague
acceptance criteria, unpredictable delivery, and tasks that are impossible to
estimate. Splitting now saves pain later."

**If the request is a technical task** (no user-facing value, pure refactoring,
infrastructure work):

> "This sounds like a technical task rather than a user story. Technical work
> is valid, but it should still be framed in terms of the value it enables.
> Who benefits from this work, and what becomes possible (or stops breaking)
> once it's done?"

Help them reframe as: "As a [beneficiary], I want [technical outcome framed as
capability], so that [value unlocked]."

---

## Phase 1b: Discover Context (when invoked standalone)

When `/story` is invoked standalone (not via `/refine`), attempt to discover
upstream context for richer story refinement. Skip this phase if context was
already provided by `/refine`.

### Step 1: Discover Architecture

If the story has a parent epic, search `index.json` for architectures
where `epicIds` contains the epic's ID. If no match, try filtering by
`initiativeId` matching the epic's `parentInitiative`.

If found, read the architecture JSON and extract key constraints
(container boundaries, key decisions, cross-cutting patterns) to inform
acceptance criteria during the story conversation. Present a brief note:

> "I found architecture `{arch_id}`. I'll use its constraints to
> inform this story's acceptance criteria."

### Step 2: Discover Epic

If the story has a `parentEpic`, read the epic from
`~/.claude/backlog-driven-development/artifacts/epics/{epicId}.json`.
Extract the business outcome, personas, and scope to ground the story
conversation.

If no epic context exists, proceed without — stories can be standalone.

---

## Phase 1c: Upstream Artifact Status Check

After discovering context, check the status of all upstream artifacts
before proceeding. Skip this phase if no upstream artifacts were found
(standalone story).

### Step 1: Check for NEEDS_REFINEMENT

For each discovered artifact (epic, architecture, initiative), read its
`status` field. If ANY has `status: "NEEDS_REFINEMENT"` (epics, architectures)
or `status: "needs-revision"` (initiatives):

> "WARNING: Upstream artifact needs refinement:
>
> - **[artifact type]** `{id}`: Status is NEEDS_REFINEMENT / needs-revision
>   Reason: [revisionReason content]
>
> Creating a story from artifacts that need revision may produce a
> story that needs rework. Would you like to:
>
> 1. Stop and address the revision first
> 2. Proceed anyway (story may need rework)"

If the user chooses to stop, tell them which skill to run.

### Step 2: Flag Upstream Issues During Work

During the story conversation, if you discover that an upstream
artifact is inadequate — e.g., the epic's scope doesn't cover the
capability being described, the architecture contradicts a requirement,
or constraints are missing — you MUST flag it:

1. **Mark the artifact** as `NEEDS_REFINEMENT` with a `revisionReason`
2. **Inform the user**:

   > "While creating this story, I found that [artifact type] needs
   > refinement:
   >
   > **Issue**: [specific problem]
   > **Impact**: [how this affects the story]
   >
   > I've updated `{id}` status to NEEDS_REFINEMENT. Address with
   > `/[skill] {id}` after we finish, or stop now."

3. **Continue** if the user chooses to proceed

---

## Phase 2: The Story Conversation

This is the core of the skill. Work through these topics conversationally —
do NOT present them as a checklist. Ask 1-2 questions at a time, build on
answers, and push back on vagueness.

**These rounds organize YOUR thinking — they are not a script to follow
literally.** The user's answers will naturally jump between rounds. Follow
their thread, cover the gaps organically, and only use the round structure
to check that nothing was missed before drafting.

### Round A: Who and Why

- **Who is the user?** Not "users" generically — a specific persona. "As a
  free-tier user who just hit the usage limit" is better than "As a user."
- **What do they want?** One specific capability or behavior change.
- **Why do they want it?** The "so that" clause. This must be a real business
  or user outcome, not a restatement of the "want." Bad: "so that I can do X"
  (circular). Good: "so that I don't lose unsaved work when my session expires."

**Pushback triggers:**
- If the persona is "a user" or "an admin" with no qualifying context, ask:
  "Which kind of user? What's their situation when they need this?"
- If the "so that" is circular, call it out: "That restates the goal — what
  real-world outcome does this enable?"

### Round B: Happy Path and Behavior

- Walk through the happy path step by step. What does the user do? What does
  the system do in response? What do they see?
- Ask about the **entry condition**: What state is the system in when this
  story begins? What must be true before the user can even start?
- Ask about the **exit condition**: What state is the system in when this
  story is done? What has changed?

### Round C: Edge Cases and Failure Modes (The Nervous Nelly Round)

This is where most stories fall apart. Be relentless here.

**Systematic edge case discovery — ask about each category:**

1. **Empty/null states**: What if there's no data? What if the input is empty?
   What if the list they're acting on has zero items?
2. **Boundary values**: What about the first item? The last item? The maximum
   allowed? One over the maximum?
3. **Permissions and access**: What if the user doesn't have permission? What
   if their permission changes mid-action?
4. **Concurrency**: What if two users do this at the same time? What if the
   user double-clicks? What if they navigate away mid-action?
5. **Failure and recovery**: What if the network drops? What if the downstream
   service is down? What if the save fails?
6. **State transitions**: What if the entity they're acting on changed since
   they loaded the page? What if it was deleted by someone else?
7. **Scale**: What if there are 10,000 items instead of 10? Does the behavior
   degrade gracefully?

Do NOT let the user hand-wave these: "Oh, we'll handle errors later." Push
back: "If we don't define the error behavior now, whoever implements this will
either guess wrong or skip it entirely. What should happen when [specific
failure]?"

For each edge case the user confirms is relevant, it becomes an acceptance
criterion.

### Round D: Target Repositories

Stories often span multiple repositories (e.g., a backend API repo and a
frontend repo, or a shared library and a consuming service). Identifying
the repositories now ensures task decomposition can assign tasks to the
right repos and `/execute` can filter to the current repo.

- "Which repositories will this story touch?" Ask for the specific repo
  names or paths. For each repo, ask what kind of work happens there
  (API changes, UI changes, shared library updates, infrastructure, etc.).
- If the user isn't sure, help them think through it: "Where does the
  backend logic live? Where does the frontend live? Are there shared
  libraries or infrastructure repos involved?"
- If the story only touches one repository, that's fine — record it.

### Round E: Scope Boundaries

Explicitly define what is NOT in this story:

- "Are there related features you're intentionally leaving out?"
- "Is there a simpler version of this we should build first?"
- "What would make this story twice as big? Let's make sure that's out of scope."

---

## Phase 3: Draft the Story

Once the conversation has covered all five rounds, draft the story using this
format:

```markdown
# US: [Short descriptive title]

**Status**: BACKLOG | TODO | NEEDS_REFINEMENT
**revisionReason**: [Only present when Status is NEEDS_REFINEMENT — which downstream skill flagged this and why]

## User Story

As a [specific persona with context],
I want [one specific capability],
so that [real business/user outcome].

## Context

[2-3 sentences of background that someone unfamiliar with the project would
need. Why does this matter now? What's the current state?]

## Acceptance Criteria

### Happy Path

- **GIVEN** [precondition]
  **WHEN** [action]
  **THEN** [observable outcome]

- **GIVEN** [precondition]
  **WHEN** [action]
  **THEN** [observable outcome]

### Edge Cases

- **GIVEN** [edge case precondition]
  **WHEN** [action]
  **THEN** [specific handling behavior]

- **GIVEN** [edge case precondition]
  **WHEN** [action]
  **THEN** [specific handling behavior]

### Out of Scope

- [Explicitly excluded behavior 1]
- [Explicitly excluded behavior 2]

## Target Repositories

- `[repo-name-or-path]` — [what changes here: API, UI, shared lib, infra, etc.]
- `[repo-name-or-path]` — [what changes here]

## Dependencies

- [Upstream dependency, if any]
- [External system dependency, if any]
- None (if self-contained)

## Open Questions

- [ ] [Anything unresolved from the conversation]
- None — all decisions resolved during conversation.

## Notes

[Any additional context, links, or references from the conversation]
```

**Drafting rules:**

- Set `**Status**: BACKLOG` in the document header. Status will be upgraded to
  `TODO` after the story-reviewer gate passes and the user approves.
- Every acceptance criterion must be **GIVEN/WHEN/THEN** format. No exceptions.
  This forces specificity. "The system handles errors gracefully" is not an AC.
  "GIVEN the payment API returns a 503, WHEN the user clicks Submit, THEN the
  system shows 'Payment temporarily unavailable, please try again' and does NOT
  create a pending order" is an AC.
- There must be at least **3 happy path ACs** and at least **3 edge case ACs**
  for non-trivial stories. If you have fewer, the conversation didn't go deep
  enough — go back to Round C. For genuinely simple stories (label change,
  config tweak), use judgment — the minimum exists to catch underspecified
  stories, not to inflate trivial ones.
- The "Out of Scope" section is mandatory. If nothing is out of scope, the story
  is probably too big.
- Acceptance criteria must describe **observable behavior**, not implementation.
  No mention of databases, APIs, frameworks, or code structure. If the user
  provides a tech-laden AC ("use Redis for caching"), reframe it as what the
  user experiences ("cached results appear instantly on repeat visits") and
  confirm with the user.
- The story statement itself must be free of technology references. "As a user,
  I want the system to call the Stripe API" is an implementation directive, not
  a user story. Reframe: "As a customer, I want to pay with my credit card."
- Never write ACs from the system's perspective. "The API returns a 200" is not
  an AC. "The user sees a confirmation message" is.

---

## Phase 4: Story Review

After drafting, dispatch the **`story-reviewer`** agent via the Agent tool.
Pass the full story text and item type "story".

**Processing results:**

- **If NOT_READY**: The reviewer will surface specific missing items. Present
  these to the user as questions that need answers. For each missing item:
  - If it's about **missing acceptance criteria or edge cases**: Ask the user
    to decide. "The reviewer flagged that we haven't defined what happens when
    [scenario]. What should the behavior be?"
  - If it's about **structural issues** (format, missing sections): Fix these
    yourself silently without bothering the user.
  - If it's about **scope concerns** (epic in disguise): Revisit the Scope
    Sniff Test with the user.

  After the user answers all questions, update the draft and re-run the
  reviewer (max 1 re-run).

- **If READY**: Present the final story to the user for approval. Once
  approved, set `**Status**: TODO` in the document header.

### Check for NEEDS_REFINEMENT Status

If the story document was loaded and has `status: "NEEDS_REFINEMENT"`, present
the `revisionReason` to the user before starting the review:

> "This story was flagged for revision by a downstream skill:
>
> **Reason**: [revisionReason content]
>
> Let's address this before proceeding."

Focus the conversation on the revision reason. After addressing it, clear
the revision status by setting `**Status**: TODO`.

---

## Phase 5: Save the Story

Once the user approves, save the story:

### Step 1: Ensure Artifact Directory Exists

```bash
mkdir -p ~/.claude/backlog-driven-development/artifacts/{initiatives,epics,architectures,stories,tasks,plan-summaries}
```

If `index.json` does not exist, create it with the empty scaffold.

### Step 2: Generate ID

Read `index.json`. Find the highest numeric suffix among existing story
IDs and increment. Zero-pad to 3 digits. First story is `story_001`.

### Step 3: Write the Artifact

Write the story as JSON to:
`~/.claude/backlog-driven-development/artifacts/stories/{id}.json`

Use the story JSON schema from the artifacts skill reference. Set
`parentEpic` to the epic ID from conversation context, or `null` for
standalone stories.

### Step 4: Update the Index

Add an entry to the `stories` array in `index.json`:

```json
{ "id": "story_001", "title": "...", "status": "TODO", "type": "feature", "creator": "[You]", "assignee": null, "storyPoints": null, "comments": [], "epicId": "epic_001", "initiativeId": "init_001", "order": 1, "taskCount": 0 }
```

If the story has a parent epic, add the story ID to the epic's
`storyIds` array in `index.json`.

Update `lastModified`. Write `index.json` back.

### Step 5: Report to User

Tell the user the story ID and: "Next step: `/task-decomposition {story_id}`
when you're ready to break this into implementation tasks."

---

## View Mode

When triggered (Input Handling case 1):

1. Read the story from `~/.claude/backlog-driven-development/artifacts/stories/{id}.json`
2. Read `index.json` to resolve relationships
3. Display in this format:

```
## Story: {title}
**ID:** {id}  |  **Type:** {type}  |  **Status:** {status}  |  **Created:** {createdAt}

### Relationships
- **Parent Epic:** {parentEpic} — "{epic title}" (or "None — standalone")

### User Story
As a {persona}, I want {want}, so that {soThat}.

### Context
{context}

### Acceptance Criteria
1. **GIVEN** {given} **WHEN** {when} **THEN** {then}
2. ...

### Out of Scope
{outOfScope}

### Dependencies
{dependencies list}

### Tasks
| ID | Title | Status | Implementer |
|----|-------|--------|-------------|
| {task_id} | {title} | {status} | {implementer} |
...

**Progress:** {N} pending, {N} in-progress, {N} complete
```

4. **Stop.** Do not enter any other phase or mode.

---

## Delete Mode

When triggered (Input Handling case 2):

### Step 1: Safety Check

1. Read `index.json` and find all tasks where `parentStory` matches this story ID
2. Check each task's `status` field
3. If ANY task has status `in-progress` or `complete`:

> "Cannot delete `{story_id}`: {N} task(s) have work in progress or completed.
>
> Blocking tasks:
> - `{task_id}`: "{title}" — status: {status}
>
> Resolve these tasks first (reset to pending or delete them individually)."

**Stop.** Do not proceed with deletion.

### Step 2: Cascade Preview

If all tasks are `pending`, `failed`, or there are no tasks, show what will
be removed:

> "You are about to delete story `{id}`: "{title}"
>
> This will remove:
> - The story file
> - {N} task(s): {list task IDs}
> - {1 plan summary if exists}
>
> Type "confirm" to proceed."

Use AskUserQuestion to get confirmation.

### Step 3: Execute Deletion

On "confirm":

1. Delete all task files: `tasks/task_{storyNum}.*.json`
2. Delete plan summary if it exists: `plan-summaries/plan_{storyNum}.json`
3. Delete the story file: `stories/{id}.json`
4. Update `index.json`:
   - Remove all deleted task entries from the `tasks` array
   - Remove the story entry from the `stories` array
   - If `parentEpic` is not null, remove this story ID from the parent
     epic's `storyIds` array
   - Update `lastModified`
5. Write `index.json`

### Step 4: Confirm

> "Deleted story `{id}`: "{title}"
> Also removed: {N} task(s){, 1 plan summary if applicable}."

---

## Refinement Mode

When an existing story is loaded (Input Handling case 3):

1. Read the existing story content
2. Run the **`story-reviewer`** agent on it first
3. Present the reviewer's findings to the user:
   > "I reviewed the existing story and found these areas that could be
   > strengthened: [findings]. Let's work through these together."
4. Enter Phase 2 (The Story Conversation) but only for the gaps identified
   by the reviewer — do not re-interview for things already well-defined
5. Update the story and proceed through Phase 4-5 as normal

---

## INVEST Quality Gate

Before presenting any draft to the user, mentally verify against INVEST:

- **Independent**: Can this be built and delivered without waiting for another
  story? If not, note the dependency explicitly.
- **Negotiable**: Are the ACs describing behavior, not implementation? Could a
  team negotiate HOW to build this without changing WHAT it does?
- **Valuable**: Does the "so that" clause describe real value to a real person?
  "So that the code is cleaner" is not user value.
- **Estimable**: Is there enough detail that a developer could estimate the
  effort? If you read this story cold, could you give a rough size?
- **Small**: Can this be completed in one sprint? If not, it needs splitting.
- **Testable**: Can every AC be verified with a concrete test? "The system is
  fast" fails. "The page loads in under 2 seconds on a 3G connection" passes.

If any dimension fails, fix it before presenting.

---

## Conversation Rules

- **One question at a time.** Do not dump a list of 10 questions. Ask the most
  important one, build on the answer, then ask the next.
- **Push back on vagueness.** Every vague statement gets the "Disagree and
  Commit" treatment: restate in specific, testable terms and ask the user to
  confirm. "When you say 'handle it gracefully,' I interpret that as [specific
  behavior]. Is that right?"
- **Name the anti-pattern.** When you see a common mistake, name it:
  "That sounds like an epic in disguise," or "That 'so that' clause is
  circular," or "That AC describes implementation, not behavior."
- **Celebrate good input.** When the user provides a crisp, specific answer,
  acknowledge it: "That's a great edge case — adding it as an AC."
- **Do not write the story silently.** The conversation IS the deliverable.
  A story that skips the conversation will have gaps.

---

## Common Anti-Patterns to Catch

When you notice any of these during the conversation, name the anti-pattern
explicitly and help the user fix it. Do NOT silently accept bad input.

| Anti-Pattern | Signal | Response |
|---|---|---|
| Epic in disguise | Multiple unrelated goals, "and also" | Split into separate stories |
| Circular "so that" | "...so that I can [restates the want]" | Ask for the real-world outcome |
| Vague AC | "handles errors," "is performant," "works correctly" | Restate as GIVEN/WHEN/THEN |
| Implementation AC | "uses Redis," "calls the API," "stores in the DB" | Reframe as observable behavior |
| Technology leakage | Database, framework, API names in story text | Remove tech; describe user-observable behavior |
| Solution-prescribed | "Add a button in the top-right corner" | Ask what the user needs, not how to build it |
| System perspective | "The system will..." "The platform sends..." | Reframe from the user's point of view |
| "As a developer" | Persona is a technical role, not end user | Ask what user-facing value this enables |
| Missing persona | "As a user" with no context | Ask which user, in what situation |
| No failure modes | Only happy path ACs | Run through Round C edge case categories |
| Kitchen sink | Story tries to do everything | Apply Scope Sniff Test, split |
| Technical task | No user-facing value | Reframe in terms of enabled value |
| NFR in disguise | "Page loads in under 3s" as the whole story | Attach NFR as AC on a real user story |
| Negative framing | "Users should not be able to..." | Reframe as positive value: "Users' data is private" |
| Copy-paste story | Generic template with blanks filled in | Add unique context from the conversation |

---

## Relationship to Other Artifacts

```
Feature idea or request
    |
/story  -->  User Story (this skill)
    |
story-reviewer gate (READY / NOT_READY)
    |
/task-decomposition  -->  plan.md (implementation tasks)
    |
/execute  -->  TDD implementation
    |
Complete (all tests pass, all ACs verified)
```
