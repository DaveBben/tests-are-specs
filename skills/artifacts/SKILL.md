---
name: artifacts
description: >
  Defines the storage conventions, JSON schemas, and read/write patterns for all
  backlog artifacts (initiatives, epics, architectures, stories, tasks). Preloaded
  by every skill that reads or writes artifacts. Provides the index.json schema,
  ID generation rules, and brownfield relationship management.
  Do NOT invoke directly — this is a reference consumed by other skills.
user-invocable: false
disable-model-invocation: true
---

# Artifact Storage Standards

All backlog artifacts are stored as flat JSON files in a central directory,
with a lightweight index for discovery and relationship tracking.

---

## Storage Location

```
~/.claude/backlog-driven-development/artifacts/
  index.json
  initiatives/
  epics/
  architectures/
  stories/
  bugs/
  tasks/
  plan-summaries/
```

### Directory Setup

Before reading or writing any artifact, ensure the directory structure
exists. If it does not, create it:

```bash
mkdir -p ~/.claude/backlog-driven-development/artifacts/{initiatives,epics,architectures,stories,bugs,tasks,plan-summaries}
```

If `index.json` does not exist, create it with the empty scaffold:

```json
{
  "version": 1,
  "lastModified": "",
  "initiatives": [],
  "epics": [],
  "architectures": [],
  "stories": [],
  "bugs": [],
  "tasks": []
}
```

---

## index.json

The index is the **single source of truth** for discovering artifacts and
understanding relationships. Every skill reads the index first, then
loads individual artifact files as needed.

### Schema

```json
{
  "version": 1,
  "lastModified": "2026-04-11T14:30:00Z",
  "initiatives": [
    {
      "id": "init_001",
      "title": "Watcher Reliability",
      "status": "proposed",
      "epicIds": ["epic_001", "epic_002"]
    }
  ],
  "epics": [
    {
      "id": "epic_001",
      "title": "Voice Memo Detection",
      "status": "BACKLOG",
      "initiativeId": "init_001",
      "order": 1,
      "storyIds": ["story_001", "story_002"]
    }
  ],
  "architectures": [
    {
      "id": "arch_001",
      "title": "Utterd Architecture",
      "status": "ACTIVE",
      "initiativeId": "init_001",
      "epicIds": ["epic_001", "epic_002", "epic_003", "epic_004"]
    }
  ],
  "stories": [
    {
      "id": "story_001",
      "title": "Detect synced voice memos",
      "status": "BACKLOG",
      "type": "feature",
      "epicId": "epic_001",
      "initiativeId": "init_001",
      "order": 1,
      "taskCount": 3
    }
  ],
  "bugs": [
    {
      "id": "bug_001",
      "title": "Stale transcription after re-recording",
      "status": "TODO",
      "severity": "high",
      "epicId": "epic_001",
      "initiativeId": "init_001"
    }
  ],
  "tasks": [
    {
      "id": "task_001.1",
      "title": "Set up watcher module",
      "status": "PENDING",
      "storyId": "story_001",
      "implementer": "AI"
    }
  ]
}
```

### Field Definitions

**All artifact types:**
- `id` — Unique identifier (see ID Generation below)
- `title` — Human-readable name
- `status` — Current lifecycle state (see Status Lifecycle below)

**initiatives:**
- `epicIds` — Array of epic IDs that belong to this initiative. Empty array if none yet.

**epics:**
- `initiativeId` — Parent initiative ID, or `null` if standalone
- `order` — Sequencing within the initiative (1-based)
- `storyIds` — Array of story IDs that belong to this epic. Empty array if none yet.

**architectures:**
- `initiativeId` — Parent initiative ID (required — architectures cannot be standalone)
- `epicIds` — Array of epic IDs this architecture covers. An initiative-wide architecture covers all epics; an epic-specific architecture covers one or a few.

**stories:**
- `type` — `"feature"`, `"spike"`, or `"bug"`
- `epicId` — Parent epic ID, or `null` if standalone
- `initiativeId` — Parent initiative ID (derived from epic), or `null`
- `order` — Sequencing within the epic (0-based, spikes are typically 0)
- `taskCount` — Number of tasks decomposed from this story

**bugs:**
- `severity` — `"critical"`, `"high"`, `"medium"`, or `"low"`
- `epicId` — Parent epic ID, or `null` if standalone
- `initiativeId` — Parent initiative ID (derived from epic), or `null`

**tasks:**
- `storyId` — Parent story ID
- `implementer` — `"AI"` or `"Human"`
- `symbolDependencies` — Array of symbols (functions, types, constants) this task *calls or imports* that are produced by another task in the same story. Format: `"TaskN.SymbolName"` (e.g., `"Task2.UserService.validateToken"`). Used by `/execute` batch computation alongside file overlap to prevent tasks that share a symbol dependency from running in the same parallel batch even when their file paths don't overlap.

---

## ID Generation

IDs are auto-incremented based on what exists in index.json.

### Algorithm

1. Read index.json
2. Find the highest numeric suffix for the artifact type
3. Increment by 1
4. Zero-pad to 3 digits

### Format

| Type | Pattern | Example |
|------|---------|---------|
| Initiative | `init_NNN` | `init_001`, `init_002` |
| Epic | `epic_NNN` | `epic_001`, `epic_002` |
| Architecture | `arch_NNN` | `arch_001`, `arch_002` |
| Story | `story_NNN` | `story_001`, `story_002` |
| Bug | `bug_NNN` | `bug_001`, `bug_002` |
| Task | `task_NNN.N` | `task_001.1`, `task_001.2` |
| Plan Summary | `plan_NNN` | `plan_001` (keyed to story number) |

**Task ID convention:** `task_{storyNum}.{taskNum}` — the story number
comes from the parent story's numeric suffix. Task numbers are 1-based
and sequential within the story. Example: story `story_003` has tasks
`task_003.1`, `task_003.2`, `task_003.3`.

**Plan Summary convention:** `plan_{storyNum}` — one plan summary per
story, using the parent story's numeric suffix.

### Edge Cases

- If index.json is empty or the array is empty, start at `_001`
- If IDs have gaps (e.g., `init_001`, `init_003`), use the next after
  the highest (`init_004`), not the gap
- Never reuse deleted IDs

---

## Artifact JSON Schemas

Each artifact is stored as a single JSON file in its type directory.
The file name matches the ID: `{id}.json`.

### Initiative (`initiatives/init_NNN.json`)

```json
{
  "id": "init_001",
  "title": "Frictionless Voice-to-Notes Capture for macOS",
  "owner": "[You]",
  "status": "proposed",
  "timeframe": "Q3 2026 (estimated 4-6 weeks)",
  "createdAt": "2026-04-10",
  "problemStatement": "...",
  "strategicAlignment": {
    "goal": "...",
    "whyNow": "..."
  },
  "proposedSolution": "...",
  "alternativesConsidered": [
    { "name": "...", "whyRejected": "..." }
  ],
  "prioritizationRationale": "...",
  "successMetrics": ["...", "..."],
  "guardrailMetrics": ["...", "..."],
  "scope": {
    "inScope": ["...", "..."],
    "outOfScope": ["...", "..."]
  },
  "risks": [
    { "name": "...", "description": "..." }
  ],
  "milestones": [
    { "name": "...", "description": "..." }
  ]
}
```

### Epic (`epics/epic_NNN.json`)

```json
{
  "id": "epic_001",
  "title": "Voice Memo Detection and Transcription",
  "status": "BACKLOG",
  "creator": "[You]",
  "parentInitiative": "init_001",
  "order": 1,
  "createdAt": "2026-04-10",
  "dueDate": null,
  "goal": "...",
  "successMetric": "...",
  "whyThisOrder": "...",
  "roughScope": "...",
  "outOfScope": "...",
  "definitionOfDone": "...",
  "comments": []
}
```

**Standalone epic:** Set `"parentInitiative": null`.

### Architecture (`architectures/arch_NNN.json`)

```json
{
  "id": "arch_001",
  "title": "Utterd Architecture",
  "author": "[Name]",
  "status": "ACTIVE",
  "lastUpdated": "2026-04-10",
  "parentInitiative": "init_001",
  "epicIds": ["epic_001", "epic_002", "epic_003", "epic_004"],
  "systemOverview": {
    "purpose": "...",
    "systemContext": [
      { "name": "...", "relationship": "..." }
    ],
    "components": [
      { "name": "...", "responsibility": "...", "stateful": false }
    ],
    "dataFlow": ["Step 1...", "Step 2..."],
    "dataFlowFailure": "...",
    "keyDecisions": [
      { "title": "...", "rationale": "...", "alternativesRejected": [] }
    ],
    "nonFunctionalRequirements": [
      { "category": "...", "requirement": "..." }
    ]
  },
  "epicDetails": [
    {
      "epicId": "epic_001",
      "title": "...",
      "componentsInvolved": ["...", "..."],
      "componentDetails": [...],
      "unknowns": ["...", "..."],
      "stateModel": {
        "statuses": ["...", "..."],
        "schema": "CREATE TABLE ..."
      },
      "errorHandling": {
        "transient": "...",
        "permanent": "...",
        "daemonRestart": "..."
      },
      "deferredToLaterEpics": [...]
    }
  ]
}
```

**Architectures require a parent.** Every architecture must belong to
an initiative (`parentInitiative` is required) and specify which epics
it covers (`epicIds`). An initiative-wide architecture lists all epics.
An epic-specific architecture lists only the epics it covers. To create
an architecture, you must first have an initiative.

### Story (`stories/story_NNN.json`)

**Feature story:**

```json
{
  "id": "story_001",
  "type": "feature",
  "title": "Detect Fully Synced Voice Memos",
  "parentEpic": "epic_001",
  "order": 1,
  "status": "BACKLOG",
  "creator": "[You]",
  "assignee": null,
  "storyPoints": null,
  "createdAt": "2026-04-10",
  "userStory": {
    "persona": "a user who just recorded a voice memo",
    "want": "Utterd to detect the new audio file once it has fully synced",
    "soThat": "processing begins automatically without me taking any action"
  },
  "context": "...",
  "acceptanceCriteria": [
    {
      "id": "ac_1.1",
      "given": "...",
      "when": "...",
      "then": "..."
    }
  ],
  "outOfScope": "...",
  "dependencies": ["story_000"],
  "comments": []
}
```

**Spike story:**

```json
{
  "id": "story_000",
  "type": "spike",
  "title": "Spike — Validate iCloud Sync Behavior",
  "parentEpic": "epic_001",
  "order": 0,
  "status": "BACKLOG",
  "creator": "[You]",
  "assignee": null,
  "storyPoints": null,
  "createdAt": "2026-04-10",
  "userStory": {
    "persona": "...",
    "want": "...",
    "soThat": "..."
  },
  "questionsToAnswer": ["...", "..."],
  "definitionOfDone": ["...", "..."],
  "timebox": "2 days",
  "note": "The output is knowledge, not production code.",
  "comments": []
}
```

**Standalone story:** Set `"parentEpic": null`.

### Bug (`bugs/bug_NNN.json`)

```json
{
  "id": "bug_001",
  "type": "bug",
  "title": "Stale transcription text displays after re-recording a voice memo",
  "status": "TODO",
  "severity": "high",
  "reporter": "[You]",
  "assignee": null,
  "createdAt": "2026-04-11",
  "parentEpic": "epic_001",

  "symptom": "After re-recording a memo, the old transcription appears.",

  "environment": {
    "os": "macOS 26.0",
    "build": "v0.1.0-alpha",
    "additional": "iCloud sync enabled"
  },

  "stepsToReproduce": [
    "Record a voice memo",
    "Wait for transcription",
    "Delete and re-record with same name",
    "Observe stale transcription"
  ],

  "expectedBehavior": "New transcription displays for the re-recorded memo.",
  "actualBehavior": "Old transcription is served from cache.",

  "impact": "All users who re-record memos see stale text. No workaround.",

  "evidence": [
    "Daemon log: 'File already tracked, skipping'",
    "SQLite shows old content hash"
  ],

  "targetRepositories": [
    { "name": "utterd", "area": "State tracker — duplicate detection" }
  ],

  "resolution": null
}
```

**Standalone bug:** Set `"parentEpic": null`.

**Resolved bug:** The `resolution` field is populated by `/triage`:

```json
{
  "resolution": {
    "rootCause": "State tracker used file path alone for deduplication.",
    "fix": "Added content hash comparison on re-detection.",
    "testsAdded": ["test_bug_001_stale_transcription_after_rerecord"],
    "resolvedAt": "2026-04-12",
    "branch": "bugfix/stale-transcription-after-rerecord",
    "pr": "https://github.com/org/utterd/pull/42"
  }
}
```

### Task (`tasks/task_NNN.N.json`)

```json
{
  "id": "task_001.1",
  "title": "Set up the watcher module with its public interface",
  "parentStory": "story_001",
  "status": "PENDING",
  "assignee": null,
  "size": null,
  "implementer": "AI",
  "repository": "utterd",
  "blockedBy": ["story_000"],
  "covers": ["ac_1.1", "ac_1.2"],
  "createdAt": "2026-04-11",
  "relevantFiles": [
    { "path": "Sources/Utterd/Watcher/FileSystemWatcher.swift", "status": "new" }
  ],
  "contextToReadFirst": [
    { "path": "architecture.md Section 2.2", "reason": "..." }
  ],
  "changes": ["...", "..."],
  "tests": [
    { "name": "test_detectsNewM4AFile", "description": "..." }
  ],
  "doneWhen": "...",
  "verificationCommand": "swift build",
  "doNot": ["...", "..."],
  "symbolDependencies": [],
  "executionNotes": ""
}
```

### Plan Summary (`plan-summaries/plan_NNN.json`)

```json
{
  "id": "plan_001",
  "parentStory": "story_001",
  "createdAt": "2026-04-11",
  "status": "approved",
  "planSize": "medium",
  "author": "AI",
  "repositories": ["utterd"],
  "whatWeAreBuilding": "...",
  "whyThisExists": "...",
  "scope": {
    "in": ["...", "..."],
    "out": [{ "item": "...", "reason": "..." }],
    "constraints": ["...", "..."]
  },
  "downstreamImpact": {
    "internal": ["...", "..."],
    "external": ["...", "..."],
    "implicitContracts": ["...", "..."]
  },
  "risksAndRollback": ["...", "..."],
  "criticalReminders": ["...", "..."],
  "taskIds": ["task_001.1", "task_001.2", "task_001.3"]
}
```

---

## Read/Write Conventions

### Reading Artifacts

1. **Read index.json** — always start here for discovery
2. **Filter** — by type, status, parent ID, etc.
3. **Read individual files** — `~/.claude/backlog-driven-development/artifacts/{type}/{id}.json`

**Example — find all stories for an epic:**
```
1. Read index.json
2. Filter stories where epicId === "epic_001"
3. Read each: stories/story_001.json, stories/story_002.json
```

**Example — traverse upstream from a story:**
```
1. Read stories/story_001.json → parentEpic: "epic_001"
2. Read epics/epic_001.json → parentInitiative: "init_001"
3. Read initiatives/init_001.json
4. Filter architectures in index where initiativeId === "init_001"
   (or filter by epicIds containing the relevant epic)
```

### Writing Artifacts

When creating or updating an artifact, follow this order:

1. **Read index.json** (to generate ID if new, or to verify existence if updating)
2. **Write the individual artifact file** (`{type}/{id}.json`)
3. **Update index.json:**
   - If new: add entry to the appropriate array, update parent's child ID array
   - If updating: update the entry's `status`, `title`, `taskCount`, etc.
   - Always update `lastModified` timestamp
4. **Write index.json** back

### Updating Relationships (Adoption)

When a standalone artifact is adopted into a parent:

1. Update the child's parent field in its individual file
   (e.g., set `parentEpic` from `null` to `"epic_001"`)
2. Update the child's parent field in index.json
   (e.g., set `epicId` from `null` to `"epic_001"`)
3. Add the child's ID to the parent's child array in index.json
   (e.g., add `"story_001"` to the epic's `storyIds`)
4. Update `lastModified`

---

## View Conventions

When a skill receives a **view** request (ID + "view" keyword), it displays the
artifact in a structured, human-readable format and then **stops** — no
refinement, no questions, no reviewer invocation.

### Standard Display Format

```
## {Type}: {title}
**ID:** {id}  |  **Status:** {status}  |  **Created:** {createdAt}

### Relationships
- Parent: {parentType} {parentId} — "{parentTitle}" (or "None — standalone")
- Children: {list of child IDs with titles and statuses}

### Content
[Type-specific sections rendered as markdown — see each skill's View Mode]

### Progress (if applicable)
- Tasks: N PENDING, N IN_PROGRESS, N DONE
```

### Relationship Resolution

1. Read the artifact JSON file
2. Read `index.json` to resolve parent/child names and statuses
3. For stories: count tasks by status
4. For epics: list stories with their task progress summaries
5. For initiatives: list epics with overall progress

### Behavior

- **Read-only.** Do not enter any creation or refinement phase.
- **No side effects.** Do not modify any files.
- **Short-circuit.** After displaying, the skill is done.

---

## Deletion Conventions

When a skill receives a **delete** request (ID + "delete" keyword), it runs
safety checks, shows a cascade preview, asks for confirmation, and then
removes the artifact and its descendants.

### Safety Check Algorithm

Deletion is **blocked** if any descendant task has status `IN_PROGRESS` or
`DONE`. The check traverses the artifact tree downward:

| Deleting | Check |
|----------|-------|
| Story | All tasks where `parentStory` matches |
| Bug | Blocked if status is `IN_PROGRESS` or `DONE` |
| Epic | All stories' tasks where story's `parentEpic` matches; all bugs where `parentEpic` matches |
| Initiative | All epics → stories → tasks and bugs in the tree |
| Architecture | No check (advisory artifact) |

If blocked, display:

```
Cannot delete {id}: {N} task(s) have work in progress or completed.

Blocking tasks:
- {task_id}: "{title}" — status: {status}

Resolve these tasks first (reset to PENDING or delete them individually).
```

### Cascade Order

When deletion is allowed, remove artifacts **bottom-up** to avoid orphan
references:

1. **Compute** the full list of files to delete (traverse children recursively)
2. **Delete child files** first (tasks, then plan-summaries, then stories,
   then epics, then architectures)
3. **Update parent references** — remove the deleted ID from any parent's
   child array in index.json
4. **Remove all deleted entries** from index.json arrays
5. **Delete the target artifact file** itself
6. **Write index.json** once with all changes and updated `lastModified`

This ordering ensures that if the process is interrupted, index.json still
points to existing files (recoverable state).

### Cascade by Type

- **Story:** Delete tasks (`task_{storyNum}.*.json`), plan summary
  (`plan_{storyNum}.json` if exists), then the story file. Remove story ID
  from parent epic's `storyIds`.
- **Epic:** For each child story, run story cascade. Then delete the epic
  file. Remove epic ID from parent initiative's `epicIds` and from any
  architecture's `epicIds`.
- **Initiative:** For each child epic, run epic cascade. Delete any child
  architectures. Then delete the initiative file.
- **Architecture:** Delete the architecture file. Remove from parent
  initiative's architecture references if tracked.

### Confirmation UX

After safety checks pass, present a preview and ask for explicit confirmation
using AskUserQuestion:

```
You are about to delete {type} `{id}`: "{title}"

This will remove:
- {N} task(s)
- {N} plan summary/summaries
- {N} story/stories
- [etc., only show non-zero counts]

Type "confirm" to proceed.
```

### Post-Deletion Output

```
Deleted {type} `{id}`: "{title}"
Also removed: {summary of cascaded deletions}
```

### ID Reuse

Deleted IDs are **never reused**. The next artifact of that type gets the
next number after the current highest in index.json.

---

## Status Lifecycle

### Initiatives

```
proposed → approved → needs-revision → approved
```

### Epics

```
BACKLOG → NEEDS_REFINEMENT → TODO → IN_PROGRESS → BLOCKED → DONE
```

### Architectures

```
DRAFT → ACTIVE → RETIRED
NEEDS_REFINEMENT → DRAFT (backflow)
```

### Stories

```
BACKLOG → NEEDS_REFINEMENT → TODO → IN_PROGRESS → IN_REVIEW → BLOCKED → DONE
```

### Bugs

```
BACKLOG → NEEDS_REFINEMENT → TODO → IN_PROGRESS → BLOCKED → DONE
```

### Tasks

```
PENDING → IN_PROGRESS → BLOCKED → DONE
```

### Status: NEEDS_REFINEMENT

Any artifact with `status: "NEEDS_REFINEMENT"` must also have a
`revisionReason` field explaining what needs to change:

```json
{
  "status": "NEEDS_REFINEMENT",
  "revisionReason": "Epic scope doesn't cover the auth boundary discovered during architecture"
}
```

Skills check for `NEEDS_REFINEMENT` status in upstream artifacts before
proceeding (see individual skill documentation for details).

---

## Relationship Rules

### What can be standalone

- **Standalone story** (`parentEpic: null`): Created via `/story`
  without epic context. Can be adopted into an epic later.
- **Standalone bug** (`parentEpic: null`): Created via `/bug` without
  epic context. Can be adopted into an epic later.
- **Standalone epic** (`parentInitiative: null`): Created via `/epic`
  without initiative context. Can be adopted into an initiative later.

### What requires a parent

- **Architecture** — must belong to an initiative (`parentInitiative`
  required) and specify which epics it covers (`epicIds` required,
  non-empty). Cannot exist standalone.
- **Task** — must belong to a story (`parentStory` required). Cannot
  exist standalone.

### Cardinality

| Child | Parent | Cardinality |
|-------|--------|-------------|
| Epic | Initiative | Many-to-one (or standalone) |
| Architecture | Initiative | Many-to-one (required) |
| Architecture | Epics | Many-to-many (at least one epic) |
| Story | Epic | Many-to-one (or standalone) |
| Bug | Epic | Many-to-one (or standalone) |
| Task | Story | Many-to-one (required) |

### Linking and moving

- **Link an epic to an initiative:** `/epic {epic_id} link to {init_id}`
  — sets `parentInitiative`, adds to initiative's `epicIds`
- **Move an epic between initiatives:** `/epic {epic_id} move to {init_id}`
  — removes from old initiative's `epicIds`, sets new `parentInitiative`,
  adds to new initiative's `epicIds`
- **Link a story to an epic:** Update the story's `parentEpic` and add
  to the epic's `storyIds`

### Brownfield adoption

When a parent is created after its children already exist, the creating
skill should ask the user whether to adopt existing standalone artifacts.
Epics and stories can be adopted upward; architectures and tasks always
have parents from creation.

### UX hints

Skills that create standalone artifacts should proactively suggest
grouping when it would help:

- `/epic` with a plain description: suggest existing initiatives, hint
  to create one if multiple epics are expected
- `/story` with a plain description: infer likely epic from description
  and suggest it, hint to create an epic if multiple stories expected
- `/architecture`: always require initiative + epic linkage, no hints
  needed (it's enforced)
