# Backlog-Driven Development

A pipeline of Claude Code skills and reviewer agents that turns a raw idea into implemented, reviewed code through structured conversation and automated quality gates.

## Pipeline

```
                    PLANNING (each step manual)                                       EXECUTION
 ___________      ________      _______________      _________      ______________      _________
|           |    |        |    |               |    |         |    |              |    |         |
| /initiative|--->| /epic  |--->| /architecture |--->| /refine |--->| /task-decomp |--->| /execute|
|___________|    |________|    |___(optional)__|    |_________|    |______________|    |_________|
     |                |              |                  |              |     |            |
     v                v              v                  v              v     v            v
  init-rev        epic-rev       arch-rev          story-rev      plan-rev  test-rev   /check (per task)
  (READY?)        (READY?)       (READY?)          (READY?)       (APPROVE?) (SOUND?)  /deep-review (per repo)
                                                                                          |
  <------- NEEDS_REFINEMENT (backflow: any downstream skill can flag upstream) ------  code-writer
                                                                                       PR + push

                              BUG TRACK (parallel entry point)
                               ________      _________
                              |        |    |         |
                              |  /bug  |--->| /triage |
                              |________|    |_________|
                                  |              |
                                  v              v
                              story-rev      /check (per commit)
                              (READY?)       /deep-review (per repo)
                                              PR + push
```

Each skill conducts an **investigative conversation**, produces a structured document, then passes it through a **reviewer agent** (quality gate) before the next stage begins. A NOT_READY verdict sends the artifact back for revision.

**Each step runs manually.** The user invokes each skill in a fresh conversation. Skills guide the user to the next command rather than auto-invoking downstream skills.

**Gap-driven questioning.** Skills analyze what context already exists (from upstream documents) and only ask about what's missing. When an initiative provides rich context, `/epic` may need only 2-3 questions. When starting from scratch, the conversation goes deeper.

**Backflow via status.** Every artifact has a `status` field with type-specific lifecycles (e.g., `BACKLOG → TODO → IN_PROGRESS → DONE` for stories/epics/bugs). Downstream skills can mark upstream artifacts as `NEEDS_REFINEMENT` with a `revisionReason` when they discover issues. Upstream skills check for this status when re-invoked and focus on the flagged issue.

## Stages

| # | Skill | Input | Output | Gate |
|---|-------|-------|--------|------|
| 1 | `/initiative` | Raw idea or opportunity description | Initiative document with problem statement, strategic alignment, proposed solution, alternatives, metrics, guardrails, scope, risks, milestones | `initiative-reviewer` |
| 2 | `/epic` | Initiative (batch creates all epics) or standalone description | Epic documents with goal, success metric, ordering rationale, scope, definition of done | `epic-reviewer` |
| 3 | `/architecture` | Initiative + all epics | Architecture document with system overview + per-epic detail (components, unknowns/spikes, schemas, error handling) | `architecture-reviewer` |
| 4 | `/refine` | Epic + architecture + initiative | Stories (including spike stories for unknowns) with GIVEN/WHEN/THEN acceptance criteria | `story-reviewer` |
| 5 | `/task-decomposition` | Story + upstream artifacts | Task files with parallel execution schedule, TDD structure, verification and anti-scope per task | `plan-reviewer` + `test-reviewer` |
| 6 | `/execute` | Story + task files | Implemented code — one branch per repo, `/check` per task, `/deep-review` per repo, PR + push | `/check` per task, `/deep-review` per repo |
| B1 | `/bug` | Bug symptom description | Bug card with reproduction steps, expected/actual behavior, severity, evidence | `story-reviewer` (bug mode) |
| B2 | `/triage` | Bug card | Fix implemented — branch, failing test, fix, `/check` per commit, `/deep-review`, PR + push | `/check`, `/deep-review` |

Stage 3 (`/architecture`) is optional — recommended when the initiative involves new system boundaries, significant technology decisions, or external integrations.

**Any artifact can be set to `NEEDS_REFINEMENT` by a downstream skill.** When re-invoked, the upstream skill reads the `revisionReason` and focuses on addressing it.

## How It Works

### Stage 1: Initiative (`/initiative`)

Takes a raw idea — even a single paragraph — and through focused conversation fills in the gaps needed to produce a complete initiative document. The skill analyzes the input, identifies what's covered and what's missing, and asks targeted questions.

Output is a narrative document: problem statement, strategic alignment, proposed solution, alternatives considered, prioritization rationale, success metrics, guardrail metrics, scope, risks, and milestones. No heavy tables or formal structures — readable prose with specific numbers.

Trusts the user. Solo projects, personal tools, single-user apps — all valid initiatives.

### Stage 2: Epic (`/epic`)

When given an initiative, analyzes the full scope and produces **all epics at once** with ordering rationale, dependency chains, and risk sequencing. When standalone, produces a single epic through focused conversation.

Each epic has: goal (outcome, not feature list), success metric (specific threshold), ordering rationale (why this is first/second/last), rough scope, out of scope, and definition of done.

No story maps at this stage — story decomposition happens in `/refine`.

### Stage 3: Architecture (`/architecture`, optional)

Reads the initiative and auto-discovers all associated epics, then produces a narrative architecture document organized as: **System Overview** (purpose, context, components, data flow, key decisions, NFRs) followed by **per-epic detail sections** (components involved, technical depth, unknowns/spikes, schemas, error handling, deferred scope).

Decisions are prose paragraphs, not formal ADRs. Unknowns are surfaced as spike recommendations. Concrete technical detail (schemas, API shapes) is included when it clarifies decisions.

### Stage 4: Refine (`/refine`)

Takes an approved epic and its architecture, then creates the full story breakdown. Derives stories from the architecture's per-epic component detail:

- **Unknowns → Spike story** (Story 0) — questions to answer, timebox, throwaway code
- **Components → Feature stories** — one per component, independently testable
- **State/data → State story** — schema, state machines
- **Integration → Orchestration story** — wires components together

Drafts all stories itself (doesn't delegate to `/story`) with GIVEN/WHEN/THEN acceptance criteria, out of scope, and dependencies. Runs story-reviewer on each.

### Stage 5: Task Decomposition (`/task-decomposition`)

Takes a story, discovers upstream artifacts, explores all involved codebases, then decomposes into individual task files with parallel-optimized TDD structure. Each task includes:

- Relevant files (strict boundary for the executor)
- Steps (TDD: write failing tests → verify red → implement → verify green)
- Acceptance criteria (GIVEN/WHEN/THEN)
- Verification (prose description of what "done" looks like)
- Do NOT (explicit anti-scope — what the implementer must avoid)
- Blocked By (dependency DAG)
- Implementer (AI or Human)
- Repository (which repo this task belongs to)

Tasks are stored as JSON artifacts alongside the plan summary in the artifact store.

### Stage 6: Execute (`/execute`)

Takes a story, resolves all tasks, groups them by repository, then processes each repo sequentially:

1. **Create branch**: `us-{story-slug}`
2. **Execute tasks in parallel batches** — dispatches code-writer agents using TDD
3. **`/check` after each task** — fast single-agent review, fix findings
4. **`/deep-review` after all tasks** — thorough 4-agent review (security, reliability, maintainability, performance), fix findings
5. **Push + create PR** — using `gh` CLI

Multi-repo stories are handled in one invocation. Each repo gets its own branch and PR. Human-marked tasks pause for the user to complete manually.

### Bug Track: `/bug` → `/triage`

Bugs have their own parallel track, separate from the feature pipeline.

**`/bug`** — Conversational bug report creator. Guides the user through capturing the symptom (not the cause), environment, reproduction steps, expected vs actual behavior, severity, and evidence. Saves as a bug card in the artifact store. Does NOT propose a fix.

**`/triage`** — Systematic debugging skill. Takes a bug card and walks through: reproduce → gather information → form hypothesis → isolate root cause → write failing test → implement minimal fix → verify → edge case testing → deep review → PR. This is the execution path for bugs — the equivalent of `/task-decomposition` + `/execute` combined. The debugging methodology IS the task decomposition.

**Why a separate path?** Bug fixes follow a fundamentally different workflow than feature implementation. Features start with known requirements and decompose into parallel tasks. Bugs start with a symptom and require investigation before you even know what to change.

## Artifact Status Lifecycle

Every planning artifact has a `Status` field:

```
BACKLOG ──── (reviewer gate passes + user approves) ────→ TODO ──→ IN_PROGRESS ──→ DONE
  ↑                                                         |
  |                                                         | (downstream skill
  |                                                         |  discovers issue)
  |                                                         v
  └──── (upstream skill addresses refinement) ──── NEEDS_REFINEMENT
                                                   + revisionReason
```

**Entry points:** Users can enter the pipeline at any point:
- `/epic` without an initiative — creates a standalone epic
- `/story` without an epic — creates a standalone story
- `/bug` without an epic — creates a standalone bug card
- `/task-decomposition` on any story — works with or without upstream artifacts
- `/triage` on any bug card — investigates and fixes the bug

## Artifact Storage

All artifacts are stored as flat JSON files with a central index:

```
~/.claude/backlog-driven-development/artifacts/
  index.json              # IDs, titles, status, relationships (stays small)
  initiatives/
    init_001.json
  epics/
    epic_001.json
  architectures/
    arch_001.json
  stories/
    story_001.json
  bugs/
    bug_001.json
  tasks/
    task_001.1.json       # Dot notation: {story_num}.{task_num}
  plan-summaries/
    plan_001.json
```

**index.json** is the discovery mechanism — skills read it to find artifacts by type, status, or parent relationship. Individual JSON files contain the full artifact content.

**Brownfield-friendly:** Not every artifact needs a parent. Standalone stories (`parentEpic: null`), standalone epics (`parentInitiative: null`), and standalone architectures are all valid. Artifacts can be adopted into parents later.

**IDs are sequential:** `init_001`, `epic_001`, `story_001`, `task_001.1`. Zero-padded to 3 digits. Task IDs use dot notation linking to parent story.

## Multi-Repository Support

Stories can span multiple repositories:

1. **`/task-decomposition`** — discovers repos, explores all codebases in parallel, tags each task with its repository
2. **`/execute`** — groups tasks by repo, processes each repo sequentially (branch → tasks → review → PR)
3. **Cross-repo dependencies** — tasks in different repos cannot share a parallel batch; repos with dependencies are processed in order

## Skills

### Planning Skills

| Skill | Description | Output |
|-------|-------------|--------|
| `/initiative` | Investigative conversation to formalize a raw idea into a structured initiative document | `artifacts/initiatives/init_NNN.json` |
| `/epic` | Analyzes an initiative and produces all epics at once with ordering rationale; or creates a standalone epic | `artifacts/epics/epic_NNN.json` |
| `/architecture` | Reads initiative + epics, produces narrative architecture with system overview and per-epic detail | `artifacts/architectures/arch_NNN.json` |
| `/refine` | Takes an epic + architecture, creates the full story breakdown including spike stories | `artifacts/stories/story_NNN.json` |
| `/story` | Refines a single standalone user story with GIVEN/WHEN/THEN acceptance criteria | `artifacts/stories/story_NNN.json` |
| `/bug` | Conversational bug report creator — captures symptom, reproduction steps, expected/actual behavior, severity, evidence | `artifacts/bugs/bug_NNN.json` |
| `/task-decomposition` | Decomposes story into parallel-optimized TDD task files with per-task verification and anti-scope | `artifacts/tasks/task_NNN.N.json` |

### Utility Skills

| Skill | Description |
|-------|-------------|
| `/repos` | Repository registry — add, list, and remove local repo paths. Used by `/task-decomposition` and `/import` to discover available repos without asking for paths each time. |

### Execution Skills

| Skill | Description |
|-------|-------------|
| `/execute` | Resolves tasks from story, groups by repo, creates branch per repo, dispatches code-writer agents in parallel batches, `/check` per task, `/deep-review` per repo, PR + push |
| `/triage` | Systematic debugging — takes a bug card through reproduce → isolate → failing test → fix → verify → `/check` per commit → `/deep-review` → PR |
| `/ship` | Creates a pull request with structured description from plan context |
| `/check` | Fast single-agent code review — used per-task during `/execute` |
| `/deep-review` | Thorough 4-agent parallel code review (security, reliability, maintainability, performance) — used per-repo after all tasks complete |

### Reference Skill (not user-invocable)

| Skill | Description |
|-------|-------------|
| `implementation-plans` | Standards, templates, and validation rules for implementation plans. Preloaded by `/task-decomposition` and `/execute`. |
| `artifacts` | Storage conventions, JSON schemas, and read/write patterns for all backlog artifacts. Referenced by all planning skills. |

## Reviewer Agents

### Planning Reviewers

| Agent | Role | Dispatched By |
|-------|------|---------------|
| `initiative-reviewer` | Experienced product leader — evidence quality, strategic alignment, metrics rigor, scope discipline | `/initiative` |
| `epic-reviewer` | Quality gate for epics — goal quality, scope discipline, multi-epic coherence | `/epic` |
| `architecture-reviewer` | Principal engineer — decision quality, component clarity, complexity-context fit | `/architecture` |
| `story-reviewer` | The nervous nelly — acceptance criteria rigor, edge cases, spike story evaluation, bug card completeness | `/refine`, `/task-decomposition`, `/bug` |
| `plan-reviewer` | Codebase grounding — file paths exist, symbols real, task ordering feasible | `/task-decomposition` |
| `test-reviewer` | Test quality — AC strength, edge case coverage, mock discipline | `/task-decomposition` |

### Execution Agents

| Agent | Role | Dispatched By |
|-------|------|---------------|
| `code-writer` | TDD implementer (does NOT commit) | `/execute` (one per task) |
| `generic-code-reviewer` | Fast all-dimensions reviewer | `/check` |
| `security-reviewer` | Injection, access control, data exposure | `/deep-review` |
| `reliability-reviewer` | Correctness, race conditions, resource lifecycle | `/deep-review` |
| `maintainability-reviewer` | Readability, compatibility, conventions | `/deep-review` |
| `performance-reviewer` | N+1 queries, blocking I/O, resource leaks | `/deep-review` |

## Artifact Storage Detail

See the [artifacts skill](skills/artifacts/SKILL.md) for full JSON schemas, ID generation rules, and read/write conventions.

## File Structure

```
backlog-driven-development/
  skills/
    initiative/
      SKILL.md
      references/
        initiative-template.md
    epic/
      SKILL.md
      references/
        epic-template.md
    architecture/
      SKILL.md
      references/
        architecture-template.md
        anti-patterns.md
    refine/
      SKILL.md
      references/
        decomposition-techniques.md
    story/
      SKILL.md
    bug/
      SKILL.md
    triage/
      SKILL.md
    task-decomposition/
      SKILL.md
      references/
        parallel-optimization.md
    implementation-plans/
      SKILL.md
      references/
        template.md
        section-guidance.md
        pipeline-overview.md
      examples/
        notification-unsubscribe.md
    execute/
      SKILL.md
    ship/
      SKILL.md
    deep-review/
      SKILL.md
    check/
      SKILL.md
    repos/
      SKILL.md
  agents/
    initiative-reviewer.md
    epic-reviewer.md
    architecture-reviewer.md
    story-reviewer.md
    plan-reviewer.md
    test-reviewer.md
    code-writer.md
    generic-code-reviewer.md
    security-reviewer.md
    reliability-reviewer.md
    maintainability-reviewer.md
    performance-reviewer.md
```

## Key Design Principles

**Gap-driven questioning.** Skills analyze upstream context and only ask about what's missing. Rich inputs need fewer questions.

**Trust the user.** If someone calls `/initiative`, they've decided it's an initiative. Solo projects, personal tools — all valid. No scope gatekeeping.

**Narrative over bureaucracy.** Decisions are prose paragraphs, not formal ADR tables. Templates produce readable documents, not review-board artifacts.

**Architecture drives decomposition.** When architecture exists, story breakdown follows component structure, unknowns become spikes, integration points become orchestration stories.

**Spike stories are first-class.** When the architecture flags unknowns, the first story is a time-boxed spike that resolves them before feature work begins.

**Flat JSON artifacts.** All backlog artifacts stored as JSON files in `~/.claude/backlog-driven-development/artifacts/` with a central `index.json` for discovery and relationship tracking. Brownfield-friendly — standalone artifacts don't require parents.

**Multi-repo in one invocation.** `/execute` groups tasks by repo and processes each sequentially: branch → tasks → review → PR.

**Two-tier review.** `/check` after each task (fast, focused). `/deep-review` after all tasks per repo (thorough, cross-cutting).

**One branch, one PR per repo.** All tasks for a repo commit to a single branch. Deep review covers the full change set. One PR for the reviewer.

**Vertical slicing.** Stories and tasks deliver end-to-end value. Pipeline-stage decompositions (detect → classify → integrate) are valid vertical slices when each produces independently testable output.

**TDD by default.** RED (failing test) then GREEN (implement). Tests and implementation live in the same task.

**Parallel optimization.** Task decomposition builds a dependency DAG. `/execute` computes parallel batches with zero file overlap between concurrent tasks.

**Quality gates block forward progress.** Every stage has a reviewer agent. NOT_READY sends work back.

**Backflow via NEEDS_REFINEMENT.** Downstream skills flag upstream issues. The user decides when to address them.

**Bugs have their own track.** `/bug` creates the card (symptom, not cause). `/triage` handles the full lifecycle from reproduction through fix verification. Unlike features, bugs don't pass through `/task-decomposition` → `/execute` — the debugging methodology IS the task decomposition.
