---
name: initiative
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[validated idea, opportunity description, or existing initiative to refine]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, TodoWrite, Skill
description: >
  Initiative creator. Takes a validated product idea and through focused,
  investigative conversation fills in the gaps needed to produce a structured
  initiative JSON artifact stored in ~/.claude/backlog-driven-development/artifacts/.
  Covers problem statement, strategic alignment, proposed solution, success
  metrics and guardrails, prioritization rationale, alternatives considered,
  scope, risks, and milestones. Produces an initiative whose investment
  areas feed into /epic.
  Do NOT use if the problem is still unvalidated — validate first.
  Do NOT use for epics (use /epic). Do NOT use for stories (use /story).
  Do NOT use for task decomposition (use /task-decomposition).
---

# Initiative Creator

> Investigative conversation that produces a structured initiative document.
> The user arrives with a raw idea — maybe a paragraph, maybe a few
> sentences. Your job is to figure out what's missing, ask about it, and
> produce a complete initiative document.

An initiative is a **commitment document.** It answers: what are we
investing in, why, how we'll know it worked, and what's out of scope.
The user arrives with a validated idea — evidence of pain, a rough sense
of the solution direction, and a belief this is worth investing in.

**Trust the user.** If someone calls `/initiative`, they've decided this
is an initiative. Do not second-guess scope or redirect to `/epic`. Solo
projects, personal tools, single-user apps — all valid initiatives.

**The solution is held loosely.** At this stage, the proposed solution is
a direction, not a spec. It's explicitly open to change as engineering
and design engage. Over-speccing at initiative stage is an anti-pattern —
capture the "what we're thinking" without locking in "how we'll build it."

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **View request** — `$ARGUMENTS` contains an initiative ID (`init_NNN`)
   AND the word "view" (in any order: `init_001 view`, `view init_001`).
   Enter **View Mode**.
2. **Delete request** — `$ARGUMENTS` contains an initiative ID (`init_NNN`)
   AND the word "delete" (in any order: `init_001 delete`,
   `delete init_001`). Enter **Delete Mode**.
3. **Initiative ID** (matches `init_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/initiatives/{id}.json`.
   Enter **Refinement Mode** — evaluate the existing initiative and
   guide the user through strengthening it.
4. **Existing initiative file path** (points to an existing artifact
   JSON file): Load it. Enter **Resumption Mode** — check which
   investment areas have epics created and resume from where the user
   left off.
5. **Plain description**: Use as the seed for the conversation. Proceed
   to Phase 1.
6. **No input**: Read `index.json` from
   `~/.claude/backlog-driven-development/artifacts/`. If initiatives
   exist, ask the user if they want to refine one or create a new
   initiative. If none exist, ask what validated idea or opportunity
   they want to formalize.

---

## Phase 1: Gap Analysis

**Goal: Read what the user gave you, identify what's already covered,
and figure out what you still need to ask about.**

Read the input carefully. Map it against the sections of the initiative
template (see [initiative-template.md](references/initiative-template.md)):

- Problem Statement — who is affected, what's broken, what evidence exists
- Strategic Alignment — what goal this supports, why now
- Proposed Solution — direction, key technology choices, user experience
- Alternatives Considered — what else was evaluated
- Prioritization Rationale — why this over other things
- Success Metrics — specific measurable outcomes
- Guardrail Metrics — what must not get worse
- Scope — what's in, what's explicitly out
- Risks and Dependencies — what could go wrong
- Milestones — delivery checkpoints

For each section, classify what you have:

- **Covered**: The input provides enough to draft this section.
- **Partially covered**: Some information present but gaps remain.
- **Missing**: Nothing in the input addresses this.

Do NOT show this analysis to the user. Use it internally to drive the
conversation.

---

## Phase 2: Investigative Conversation

**Goal: Fill the gaps identified in Phase 1 through focused questioning.**

### How to ask

- **Start with what's missing, prioritized by importance.** Problem
  statement gaps first, then metrics, then risks, then the rest.
- **Ask 1-2 questions at a time.** Do not dump a list. Build on answers.
- **Be specific, not generic.** Don't ask "tell me about the problem."
  Ask "You mentioned voice memos pile up unprocessed — roughly how many
  memos per day are we talking about, and what percentage actually get
  reviewed?"
- **Infer where you can, confirm where you must.** If the input strongly
  implies something (e.g., a solo project means no cross-team
  dependencies), draft that section yourself and confirm it rather than
  asking an obvious question.
- **Push back on vagueness.** If an answer is too vague to write a
  concrete section, ask a follow-up. "Improve the workflow" → "Improve
  it how? What's the measurable change?"

### What to ask about (only for gaps)

**Problem Statement gaps:**
- Who specifically feels this pain? In what context?
- What evidence do you have — observed or assumed? (Both are valid, but
  we track them differently.)
- How often does this happen? How many people/instances are affected?
- What's the cost of leaving it unsolved?

**Strategic Alignment gaps:**
- What goal does this support? For personal projects: what personal
  productivity or capability goal?
- Why now? What changed — new technology, new behavior, new constraint —
  that makes this the right time?

**Metrics gaps:**
- How will you know this worked? What's the specific number or threshold?
- What must NOT get worse while you're building this? (Resource usage,
  battery, reliability, speed of existing workflows)

**Alternatives gaps:**
- What else did you consider? Other tools, other approaches, doing
  nothing?
- Why were those rejected?

**Scope gaps:**
- What would someone assume is included but isn't? What would make this
  2-3x bigger?

**Risks gaps:**
- What's the biggest thing that could go wrong? What assumptions are you
  making that might be wrong?
- Any platform dependencies, API stability concerns, or third-party
  reliability issues?

**Milestones gaps:**
- What are the meaningful checkpoints? What can you demonstrate or test
  at each stage?

### When to stop asking

Stop when you have enough information to draft every section of the
template with specific, concrete content — not placeholders or vague
statements. A good signal: you can write every success metric with a
number and every risk with a specific concern.

You do NOT need to ask about every section. If the input is rich, you
may only need 2-3 rounds of questions. If it's sparse, you may need
more. **Minimize the number of questions — be efficient, not exhaustive.**

---

## Phase 3: Draft the Initiative

Once you have enough information, draft the initiative using the template
in [initiative-template.md](references/initiative-template.md).

**Drafting rules:**

- Set `Status: Proposed`.
- **Problem Statement** must be grounded — reference evidence where it
  exists, and honestly name assumptions where it doesn't. No evidence
  tables — write it as narrative prose.
- **Strategic Alignment** must name a specific goal. For personal/solo
  projects, a personal productivity or capability goal is valid. "Why
  now" must reference an external change, not just internal motivation.
- **Proposed Solution** must be a paragraph of direction, not a feature
  spec. Enough to convey approach and key choices.
- **Alternatives Considered** must have at least 2-3 entries including
  "do nothing." Each alternative gets a name and 1-2 sentences on why
  it was rejected.
- **Prioritization Rationale** must explain the deliberate choice — why
  this over the alternatives competing for the same time/energy.
- **Success Metrics** must have specific numbers or thresholds. Bullet
  list format.
- **Guardrail Metrics** must name at least 1-2 things that must not
  get worse. Bullet list format.
- **Scope** must have specific in-scope items and at least 2-3 specific
  out-of-scope exclusions.
- **Risks and Dependencies** must include internal risks (assumptions,
  complexity) not just external ones. Each risk is a short paragraph.
- **Milestones** must describe meaningful, independently testable
  delivery checkpoints.

Scale the document to scope. A small personal tool doesn't need 12 risks
and 8 milestones. A major multi-team investment warrants more depth.
Match the depth to the ambition.

---

## Phase 4: Initiative Review

### Step 1: Run the Initiative Reviewer Gate

Before presenting the initiative to the user, run the `initiative-reviewer`
agent on the draft. This agent checks structural completeness, evidence
grounding, metrics quality, scope discipline, and scans for anti-patterns.

- If the verdict is **NOT_READY**: Fix all STRUCTURAL issues silently.
  Present BLOCKING/SHOULD_FIX findings to the user and work through them
  before proceeding.
- If the verdict is **READY** (possibly with SHOULD_FIX items): Present
  SHOULD_FIX items to the user alongside the walkthrough below.

### Step 2: User Walkthrough

Present the draft to the user and walk through it:

- "Does the Problem Statement capture the real pain?"
- "Is the proposed solution at the right level — directional but not
  over-specced?"
- "Do the success metrics feel right? Are the guardrails the right ones?"
- "Is anything missing from scope or risks?"

Keep the walkthrough concise. Don't re-read every section aloud — the
user can read the document. Focus on the judgment calls and anything
you're unsure about.

Iterate until the user approves. Once approved, set `Status: Approved`.

### Step 3: Check for Needs-Revision Status

If the initiative document was loaded and has `Status: Needs-Revision`,
present the `Revision-Reason` to the user before starting the walkthrough:

> "This initiative was flagged for revision by a downstream skill:
>
> **Reason**: [Revision-Reason content]
>
> Let's address this before proceeding."

After addressing the revision reason, clear the status by setting
`Status: Approved`.

---

## Phase 5: Save the Initiative

### Step 1: Ensure Artifact Directory Exists

```bash
mkdir -p ~/.claude/backlog-driven-development/artifacts/{initiatives,epics,architectures,stories,tasks,plan-summaries}
```

If `~/.claude/backlog-driven-development/artifacts/index.json` does not
exist, create it with the empty scaffold (see artifacts skill reference).

### Step 2: Generate ID

Read `index.json`. Find the highest numeric suffix among existing
initiative IDs (e.g., `init_003` → next is `init_004`). If no
initiatives exist, start at `init_001`. Zero-pad to 3 digits.

### Step 3: Write the Artifact

Write the initiative as JSON to:
`~/.claude/backlog-driven-development/artifacts/initiatives/{id}.json`

Use the initiative JSON schema from the artifacts skill reference.
Set `status` to the approved status from Phase 4.

### Step 4: Update the Index

Add an entry to the `initiatives` array in `index.json`:

```json
{ "id": "init_001", "title": "...", "status": "approved", "epicIds": [] }
```

Update `lastModified` to the current ISO 8601 timestamp.
Write `index.json` back.

### Step 5: Report to User

Tell the user the initiative ID and file path.

---

## Phase 6: Next Steps Guidance

After saving, guide the user without auto-invoking the next steps.

> "The initiative is saved as `{id}`. Here are your next steps:
>
> **Optional: System-level architecture**
> If this initiative involves a new platform, shared infrastructure across
> investment areas, or foundational technology decisions, run:
> `/architecture {id}`
>
> **Create epics:**
> Run `/epic {id}` to analyze the initiative and produce all
> epics at once. The epic skill will identify the natural decomposition,
> propose ordering based on dependencies and risk, and draft all epics.
>
> **Full pipeline after epic creation:**
> `/epic` → `/architecture` (optional) → `/refine` → `/task-decomposition`
> → `/execute`"

**Do NOT auto-invoke `/epic` or `/architecture`.** The user runs each
step manually in a fresh conversation. This skill's job ends after saving
the initiative and presenting next steps.

---

## View Mode

When triggered (Input Handling case 1):

1. Read the initiative from `~/.claude/backlog-driven-development/artifacts/initiatives/{id}.json`
2. Read `index.json` to resolve relationships
3. Display in this format:

```
## Initiative: {title}
**ID:** {id}  |  **Status:** {status}  |  **Owner:** {owner}  |  **Created:** {createdAt}

### Problem Statement
{problemStatement}

### Strategic Alignment
- **Goal:** {strategicAlignment.goal}
- **Why Now:** {strategicAlignment.whyNow}

### Proposed Solution
{proposedSolution}

### Success Metrics
- {metric 1}
- {metric 2}
...

### Guardrail Metrics
- {guardrail 1}
...

### Scope
**In:** {inScope list}
**Out:** {outOfScope list}

### Risks
- {risk 1}
...

### Milestones
- {milestone 1}
...

### Epics
| ID | Title | Status | Stories | Tasks (P/IP/C) |
|----|-------|--------|---------|----------------|
| {epic_id} | {title} | {status} | {N} | {pending}/{in-progress}/{complete} |
...

### Architectures
| ID | Title | Status |
|----|-------|--------|
| {arch_id} | {title} | {status} |
...

**Overall Progress:** {total tasks} tasks — {N} pending, {N} in-progress, {N} complete
```

4. **Stop.** Do not enter any other phase or mode.

---

## Delete Mode

When triggered (Input Handling case 2):

### Step 1: Safety Check

1. Read `index.json` and find all epics where `initiativeId` matches
2. For each epic, find all stories where `epicId` matches
3. For each story, find all tasks where `parentStory` matches
4. Check each task's `status` field
5. If ANY task has status `in-progress` or `complete`:

> "Cannot delete `{init_id}`: work is in progress or completed on downstream tasks.
>
> Blocking tasks:
> - `{task_id}` (in `{story_id}` → `{epic_id}`): "{title}" — status: {status}
>
> Resolve these tasks first (reset to pending or delete them individually)."

**Stop.** Do not proceed with deletion.

### Step 2: Cascade Preview

If all descendant tasks are `pending`, `failed`, or there are no tasks:

> "You are about to delete initiative `{id}`: "{title}"
>
> This will remove:
> - The initiative file
> - {N} architecture(s): {list arch IDs}
> - {N} epic(s): {list epic IDs}
> - {N} story/stories across those epics
> - {N} task(s) across those stories
> - {N} plan summary/summaries
>
> Type "confirm" to proceed."

Use AskUserQuestion to get confirmation.

### Step 3: Execute Deletion

On "confirm":

1. For each child epic, run the epic deletion cascade:
   - For each child story of the epic:
     - Delete task files: `tasks/task_{storyNum}.*.json`
     - Delete plan summary: `plan-summaries/plan_{storyNum}.json` (if exists)
     - Delete story file: `stories/{story_id}.json`
   - Delete epic file: `epics/{epic_id}.json`
2. Delete all child architecture files: `architectures/{arch_id}.json`
3. Delete the initiative file: `initiatives/{id}.json`
4. Update `index.json`:
   - Remove all deleted task entries from the `tasks` array
   - Remove all deleted story entries from the `stories` array
   - Remove all deleted epic entries from the `epics` array
   - Remove all deleted architecture entries from the `architectures` array
   - Remove the initiative entry from the `initiatives` array
   - Update `lastModified`
5. Write `index.json`

### Step 4: Confirm

> "Deleted initiative `{id}`: "{title}"
> Also removed: {N} architecture(s), {N} epic(s), {N} story/stories, {N} task(s){, N plan summary/summaries}."

---

## Refinement Mode

When an existing initiative is loaded (Input Handling case 3):

1. Read the existing initiative JSON
2. Run the `initiative-reviewer` agent on it first
3. Present the reviewer's findings to the user:
   > "I reviewed the existing initiative and found these areas to
   > strengthen:
   > - [finding 1]
   > - [finding 2]
   > Let's work through these together."
4. Enter Phase 2 but only for the gaps identified — do not re-interview
   for things already well-defined
5. Proceed through Phase 3-5 as normal, then Phase 6
6. For investment areas: check `index.json` for epics with
   `initiativeId` matching this initiative. Only guide the user to run
   `/epic` for new or substantially changed areas.

---

## Resumption Mode

When `$ARGUMENTS` points to an existing initiative (Input Handling
case 2):

1. Read the initiative JSON
2. Check the `status` field — if `needs-revision`, present the
   `revisionReason` and focus on addressing it
3. Read `index.json` and filter epics where `initiativeId` matches this
   initiative. Compare against the initiative's investment areas.
4. If all areas have epics: tell the user the initiative is fully seeded
5. If areas remain: present the remaining areas and guide them to `/epic`

---

## Conversation Rules

- **Be investigative, not bureaucratic.** Your job is to help the user
  think through their idea, not march through a checklist.
- **Ask the fewest questions possible.** If you can infer it from the
  input, draft it and confirm. Only ask when you genuinely don't know.
- **One or two questions at a time.** Do not dump a list. Build on
  answers.
- **Push back on vagueness.** "We want to improve retention" gets:
  "Retention measured how? From what baseline to what target?"
- **Separate evidence from assumption.** When the user states something
  as fact, consider: is that observed or assumed? Both are valid, but
  assumptions are risks.
- **Guard the boundary between direction and spec.** When the solution
  section gets too detailed: "We're spec-ing too early. At initiative
  stage, we want direction, not design."

---

## Common Anti-Patterns to Catch

| Anti-Pattern | Signal | Response |
|---|---|---|
| Solution over-specced | Initiative reads like a PRD | "This is too detailed for initiative stage — direction only" |
| Evidence-free problem | No data, interviews, or observation | "Name these as assumptions — they're investment risks" |
| Vague strategic alignment | "Supports our growth goals" | "Which specific goal, measured how?" |
| Internal "why now" | "We've been planning this" | "What external change makes NOW right?" |
| No guardrails | Only primary metrics named | "What metric must not regress while you optimize for [KPI]?" |
| Unmeasured success | "Users will be happier" | "What's the proxy metric? What's the baseline?" |
| No alternatives | Nothing was considered | "What would you do instead? That's your first alternative." |
| Unbounded scope | No non-goals | "What would make this 3x bigger? Exclude those things." |
| Risk-free plan | Only external risks listed | "What internal assumptions could be wrong?" |

---

## Relationship to Other Artifacts

```
Validated idea / opportunity
    |
/initiative  -->  Initiative document (this skill)
    |
    |  (user runs each step manually in a fresh conversation)
    |
    +-- /architecture  -->  System-level architecture (optional)
    |                       For platform decisions spanning all epics
    |
    +-- Investment areas
         |
         +-- /epic  -->  Epic 1
         |       |
         |       +-- /architecture  -->  Epic-level architecture (optional)
         |       |
         |       +-- /refine  -->  Story decomposition
         |            |             Discovers architecture + initiative
         |            +-- /story  -->  User Stories
         |                    |
         |                    v
         |             /task-decomposition  -->  tasks (per story)
         |                    |
         |                    v
         |             /execute  -->  TDD implementation
         |                    |
         |                    v
         |             /ship  -->  PR
         |
         +-- /epic  -->  Epic 2
         +-- /epic  -->  Epic N

Backflow: any downstream skill can mark upstream artifacts as
Needs-Revision with a reason. The upstream skill checks for this
status when re-invoked.
```
