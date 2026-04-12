---
name: bug
effort: medium
model: opus
argument-hint: "[bug description, symptom, or existing bug ID to refine]"
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
  - AskUserQuestion
description: >
  Conversational bug report creator. Guides the user through creating a
  well-formed bug card with reproduction steps, expected vs actual behavior,
  severity, and evidence. Pushes back on diagnoses — titles describe symptoms,
  not causes. Saves the bug as a JSON artifact in
  ~/.claude/backlog-driven-development/artifacts/bugs/.
  Do NOT use for proposing fixes (use /triage after the bug card is complete).
  Do NOT use for feature requests (use /story).
---

# Bug Report Creator

> Interactive conversation that produces a single, well-formed bug card.
> Expect 5-15 minutes of back-and-forth. The output is a bug card ready for
> `/triage`.

A good bug report answers one question: **what did you observe, and how can
someone else observe it too?** It does NOT propose a fix — that's `/triage`'s
job. The conversation focuses entirely on capturing the symptom, environment,
reproduction steps, and evidence needed for effective debugging.

**Key discipline: symptom, not cause.** The title and description capture what
the user *observed*, not what they *think* went wrong. "Stale transcription
text displays after re-recording" is a symptom. "Cache invalidation bug" is
a diagnosis. Diagnoses belong in `/triage`, not here.

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **View request** — `$ARGUMENTS` contains a bug ID (`bug_NNN`)
   AND the word "view" (in any order: `bug_001 view`, `view bug_001`).
   Enter **View Mode**.
2. **Delete request** — `$ARGUMENTS` contains a bug ID (`bug_NNN`)
   AND the word "delete" (in any order: `bug_001 delete`,
   `delete bug_001`). Enter **Delete Mode**.
3. **Bug ID** (matches `bug_NNN`): Read from
   `~/.claude/backlog-driven-development/artifacts/bugs/{id}.json`.
   Enter **Refinement Mode** — evaluate the existing bug card and guide
   the user through improving it rather than starting from scratch.
4. **Existing bug file path** (points to an existing artifact JSON
   file): Enter **Refinement Mode** — read the bug and strengthen it.
5. **Plain description with epic context** (e.g., `"stale text after save"
   epic:epic_001` or description provided while an epic ID is in the
   conversation): Load the epic from
   `~/.claude/backlog-driven-development/artifacts/epics/{epicId}.json`
   for context. The bug's `parentEpic` will be set to this epic ID.
   Proceed to Phase 1 with epic context.
6. **Plain description** (no epic context): Use as the seed for a
   bug card. Read `index.json` and check for existing epics. If epics
   exist, try to infer which epic this bug relates to based on the
   description and epic goals/scopes. Suggest the best match:
   > "Based on your description, this bug sounds like it could relate to:
   > 1. `{epic_id}`: [title] — [goal summary]
   > 2. **Standalone** — no epic (you can link it later)
   >
   > Which one?"
   Set `parentEpic` accordingly. Proceed to Phase 1.
7. **No input**: Ask what bug they observed. Include the hint:
   > "Describe what you saw — the symptom, not the cause. For example:
   > 'After saving a memo, the old text still shows' rather than
   > 'the cache doesn't invalidate.'"

---

## Phase 1: Understand the Symptom

**Goal: Capture what the user observed and ensure the title describes the
symptom, not the cause.**

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

Help them reframe. The diagnosis may be correct, but it belongs in `/triage`'s
investigation, not in the bug card.

**Scope check:** If the description contains multiple distinct bugs ("and also,
there's another issue where..."), push back:

> "That sounds like two separate bugs. Let's capture one at a time — which one
> is more urgent? We'll create a card for the other one after."

---

## Phase 2: The Bug Conversation

Work through these topics conversationally — do NOT present them as a
checklist. Ask 1-2 questions at a time, build on answers, and push back on
vagueness.

**These rounds organize YOUR thinking — they are not a script to follow
literally.** The user's answers will naturally jump between rounds. Follow
their thread, cover the gaps organically, and only use the round structure
to check that nothing was missed before drafting.

### Round A: Environment

Establish where and when this bug was observed:

- Operating system and version
- Browser or runtime and version (if applicable)
- Application version or build number
- Deployment environment (production, staging, local dev)
- Any relevant configuration (feature flags, user role, account type)

Don't ask for every field if they're not relevant. A backend API bug doesn't
need a browser version. Use judgment.

### Round B: Steps to Reproduce

Walk through what the user did, step by step:

- **Start state**: What was true before the bug appeared? Was the user logged
  in? Had they just performed another action? Was the system in a specific mode?
- **Actions**: What did they do, in what order?
- **Observation**: At which step did the unexpected behavior appear?

**Push back on vagueness:**

- "It just breaks" → "What exactly do you see when it breaks? An error message?
  A blank screen? Wrong data?"
- "Sometimes it happens" → "Can you describe the last time it happened? What
  were you doing? Can you make it happen right now?"
- "It doesn't work" → "What specifically doesn't work? What did you expect to
  see vs. what appeared?"

The goal is **a sequence someone else can follow to trigger the bug
consistently.** If the user can't reproduce it reliably, note that explicitly
— intermittent bugs are valid, but the card should document what's known about
the conditions.

### Round C: Expected vs Actual Behavior

Both must be concrete and specific:

- **Expected**: What should have happened? Describe the correct behavior. If
  the user doesn't know the expected behavior, help them reason about it from
  the feature's intent.
- **Actual**: What did happen? Include specifics: error messages (exact text),
  visual state, data returned, HTTP status codes, timing.

**Push back on vagueness:**

- "It should work correctly" → "What does 'correctly' mean here? What specific
  output, screen, or behavior should you see?"
- "It shows the wrong thing" → "What exactly does it show? And what should it
  show instead?"

### Round D: Severity and Impact

Establish the business impact:

- **Who is affected?** All users? A specific segment? Just one user?
- **How often?** Every time? Intermittently? Only under specific conditions?
- **Is there a workaround?** Can users accomplish their goal another way?
- **What's the blast radius?** Data loss? Security exposure? Feature unusable?
  Cosmetic only?

**Severity levels:**

| Level | Criteria |
|-------|----------|
| Critical | Data loss, security vulnerability, complete feature outage, no workaround |
| High | Core feature broken, significant user impact, no reasonable workaround |
| Medium | Feature broken but workaround exists, or non-core feature broken |
| Low | Cosmetic issue, minor inconvenience, edge case with easy workaround |

Help the user calibrate — people tend to overrate severity of bugs they
personally encountered. Ask: "If this happened to a new user who didn't know
the workaround, how bad would it be?"

### Round E: Evidence

Ask what evidence exists:

- Screenshots or screen recordings
- Error messages (exact text, not paraphrased)
- Log output or stack traces
- Network requests/responses (HTTP status, response body)
- Database state or query results

If the user has none: "Can you reproduce the bug now and capture the error
message or a screenshot? Evidence makes the bug much easier to investigate."

Record whatever they provide. Note what evidence is missing but would be
useful — `/triage` can gather it during investigation.

### Round F: Relevant Repositories

Same pattern as `/story`:

- "Which repositories does this bug likely affect?"
- If the user isn't sure, help them reason: "Where does the feature that's
  broken live? Is it frontend, backend, or both?"
- For each repo, note what area is likely affected (e.g., "API — auth
  middleware," "UI — settings page")

---

## Phase 3: Draft the Bug Card

Once the conversation has covered all rounds, draft the bug card. The card
does NOT contain a proposed solution or root cause analysis.

**Draft format:**

```markdown
# BUG: [Title describing the symptom]

**Status**: BACKLOG
**Severity**: [Critical | High | Medium | Low]

## Symptom

[1-2 sentence description of what the user observes]

## Environment

- **OS**: [...]
- **Version/Build**: [...]
- [other relevant env details]

## Steps to Reproduce

1. [Prerequisite state]
2. [Action]
3. [Action]
4. [Observe: actual behavior]

## Expected Behavior

[What should happen — concrete and specific]

## Actual Behavior

[What does happen — concrete and specific, with error messages if available]

## Severity and Impact

[Who is affected, how many, how often, workaround status]

## Evidence

- [Screenshot link, log excerpt, stack trace, error message]
- [Additional evidence]

## Target Repositories

- `[repo-name-or-path]` — [what area is likely affected]

## Resolution

[Left blank — to be filled by /triage after the fix is verified]
```

**Drafting rules:**

- Set `**Status**: BACKLOG` in the document header.
- The title must describe the **symptom**, not the cause. Review it one more
  time before presenting.
- Steps to Reproduce must be a numbered list starting from a known state. If
  the bug is intermittent, note the conditions and frequency.
- Expected and Actual behavior must be specific enough that someone unfamiliar
  with the feature can tell the difference.
- Resolution is always blank at this stage. It gets filled by `/triage`.
- Do NOT include a "Root Cause" or "Proposed Fix" section. That's `/triage`.

---

## Phase 4: Bug Review

Dispatch the **`story-reviewer`** agent via the Agent tool. Pass:
- The full bug card text
- Item type: "bug"

The story-reviewer has a dedicated "Evaluation: Bugs" section that checks
for reproducibility, environment specificity, expected/actual clarity, and
severity calibration.

**Processing results:**

- **If NOT_READY**: Present missing items to the user as questions. For each:
  - If it's about **missing reproduction steps or evidence**: Ask the user
    for specifics.
  - If it's about **structural issues** (format, missing sections): Fix
    silently without bothering the user.
  - If it's about **severity miscalibration**: Discuss with the user and
    recalibrate.

  After the user answers, update the draft and re-run the reviewer (max 1
  re-run).

- **If READY**: Present the final bug card to the user for approval. Once
  approved, set `**Status**: TODO`.

### Check for NEEDS_REFINEMENT Status

If the bug was loaded from an existing file and has `**Status**: NEEDS_REFINEMENT`,
present the `**Revision-Reason**` before starting:

> "This bug was flagged for revision:
>
> **Reason**: [Revision-Reason content]
>
> Let's address this before proceeding."

Focus the conversation on the revision reason.

---

## Phase 5: Save the Bug

Once the user approves, save the bug:

### Step 1: Ensure Artifact Directory Exists

```bash
mkdir -p ~/.claude/backlog-driven-development/artifacts/{initiatives,epics,architectures,stories,bugs,tasks,plan-summaries}
```

If `index.json` does not exist, create it with the empty scaffold (including
the `bugs` array).

### Step 2: Generate ID

Read `index.json`. Find the highest numeric suffix among existing bug IDs
and increment. Zero-pad to 3 digits. First bug is `bug_001`.

### Step 3: Write the Artifact

Write the bug as JSON to:
`~/.claude/backlog-driven-development/artifacts/bugs/{id}.json`

**Bug JSON schema:**

```json
{
  "id": "bug_001",
  "type": "bug",
  "title": "[Symptom-based title]",
  "status": "TODO",
  "severity": "high",
  "reporter": "[You]",
  "assignee": null,
  "createdAt": "2026-04-11",
  "parentEpic": "epic_001",

  "symptom": "[1-2 sentence description]",

  "environment": {
    "os": "macOS 26.0",
    "build": "v0.1.0",
    "additional": "[other relevant details]"
  },

  "stepsToReproduce": [
    "Step 1...",
    "Step 2...",
    "Step 3..."
  ],

  "expectedBehavior": "[What should happen]",
  "actualBehavior": "[What does happen]",

  "impact": "[Who is affected, how many, workaround status]",

  "evidence": [
    "[Screenshot, log excerpt, stack trace, error message]"
  ],

  "targetRepositories": [
    { "name": "[repo]", "area": "[what area is affected]" }
  ],

  "resolution": null
}
```

### Step 4: Update the Index

Add an entry to the `bugs` array in `index.json`:

```json
{
  "id": "bug_001",
  "title": "...",
  "status": "TODO",
  "severity": "high",
  "epicId": "epic_001",
  "initiativeId": "init_001"
}
```

If the bug has a parent epic, derive `initiativeId` from the epic.

Update `lastModified`. Write `index.json` back.

### Step 5: Report to User

Tell the user the bug ID and: "Next step: `/triage {bug_id}` when you're
ready to investigate and fix this bug."

---

## View Mode

When triggered (Input Handling case 1):

1. Read the bug from `~/.claude/backlog-driven-development/artifacts/bugs/{id}.json`
2. Read `index.json` to resolve relationships
3. Display in this format:

```
## Bug: {title}
**ID:** {id}  |  **Severity:** {severity}  |  **Status:** {status}  |  **Created:** {createdAt}

### Relationships
- **Parent Epic:** {parentEpic} — "{epic title}" (or "None — standalone")

### Symptom
{symptom}

### Environment
{environment details}

### Steps to Reproduce
1. {step 1}
2. {step 2}
...

### Expected Behavior
{expectedBehavior}

### Actual Behavior
{actualBehavior}

### Severity and Impact
{impact}

### Evidence
{evidence list}

### Target Repositories
{targetRepositories}

### Resolution
{resolution or "Pending — run /triage {id} to investigate"}
```

4. **Stop.** Do not enter any other phase or mode.

---

## Delete Mode

When triggered (Input Handling case 2):

### Step 1: Safety Check

1. Read the bug from `~/.claude/backlog-driven-development/artifacts/bugs/{id}.json`
2. Check the bug's `status` field
3. If status is `IN_PROGRESS` or `DONE`:

> "Cannot delete `{bug_id}`: bug is currently {status}.
>
> A bug that is IN_PROGRESS has active investigation work. A DONE bug
> has a fix associated with it. Reset the status to `TODO` first if
> you want to delete it."

**Stop.** Do not proceed with deletion.

### Step 2: Confirmation

If status allows deletion (`TODO`, `BACKLOG`, `NEEDS_REFINEMENT`):

> "You are about to delete bug `{id}`: "{title}"
>
> This will remove:
> - The bug file
>
> Type "confirm" to proceed."

Use AskUserQuestion to get confirmation.

### Step 3: Execute Deletion

On "confirm":

1. Delete the bug file: `bugs/{id}.json`
2. Update `index.json`:
   - Remove the bug entry from the `bugs` array
   - Update `lastModified`
3. Write `index.json`

### Step 4: Confirm

> "Deleted bug `{id}`: "{title}""

---

## Refinement Mode

When an existing bug is loaded (Input Handling case 3):

1. Read the existing bug content
2. Run the **`story-reviewer`** agent on it (item type: "bug")
3. Present the reviewer's findings:
   > "I reviewed the existing bug card and found these areas that could be
   > strengthened: [findings]. Let's work through these together."
4. Enter Phase 2 (The Bug Conversation) but only for the gaps identified
   by the reviewer — do not re-interview for things already well-defined
5. Update the bug card and proceed through Phase 4-5 as normal

---

## Common Anti-Patterns to Catch

When you notice any of these during the conversation, name the anti-pattern
explicitly and help the user fix it:

| Anti-Pattern | Signal | Response |
|---|---|---|
| Diagnosis as title | "Race condition in save handler" | Reframe as observable symptom |
| Vague reproduction | "It just breaks sometimes" | Demand specific steps and conditions |
| Missing environment | No OS/version/build info | Ask which environment they observed it in |
| Expected = "it works" | "Expected: it should work correctly" | Ask what "correctly" looks like specifically |
| Actual = "it's broken" | "Actual: it doesn't work" | Ask what specifically they see/experience |
| Solution in bug card | "Fix: invalidate the cache after save" | Remove — solutions belong in /triage |
| Multiple bugs in one | "Also, there's another issue..." | Split into separate bug cards |
| Inflated severity | Cosmetic issue rated as Critical | Calibrate using the severity table |
| No evidence | No screenshots, logs, or error messages | Ask if they can reproduce and capture evidence |

---

## Conversation Rules

- **One question at a time.** Do not dump a list of 10 questions.
- **Push back on vagueness.** Every vague statement gets restated in specific
  terms: "When you say 'it breaks,' I interpret that as [specific behavior].
  Is that right?"
- **Name the anti-pattern.** When you see a common mistake, name it:
  "That's a diagnosis, not a symptom," or "That reproduction step assumes
  too much — what state is the system in when you start?"
- **Celebrate good input.** When the user provides a clear reproduction
  sequence or exact error message, acknowledge it.
- **Do not write the bug card silently.** The conversation IS the deliverable.

---

## Pipeline

```
Bug symptom observed
    |
/bug  -->  Bug Card (this skill)
    |
story-reviewer gate (READY / NOT_READY — bug evaluation rules)
    |
/triage  -->  Full debugging lifecycle (reproduce → isolate → test → fix → verify → PR)
    |
Complete (bug resolved, PR merged)
```
