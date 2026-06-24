<!--
MASTER SPEC TEMPLATE
A synthesis of the strongest elements from 10 spec-driven-development tools
(spec-kit, GSD, OpenSpec, BMAD, ccpm, Backlog.md, potpie, agent-os,
spec-workflow-mcp, Kiro). Design rationale is in the appendix at the bottom.

This is an ENGINEERING spec, not a product brief. It is outcome-first, not
user-story-first — it works for renames, schema changes, and refactors as well
as features. The spec is the WHAT and WHY; deep design (diagrams, full schemas)
lives in a linked design doc — keep it out of here.

Fill the < > placeholders. Delete guidance comments before review.
-->

---
id: SPEC-NNN                      # stable handle; tasks/commits reference this
title: <short imperative title>
status: draft                    # draft → reviewed → applied → archived
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
owners: [<@handle>]
branch: NNN-<kebab-title>
standards: standards.md          # the constitution — ONE of: standards.md | CLAUDE.md | AGENTS.md
ambiguity_score:                 # 0.00–1.00; must be ≤ 0.20 to leave `draft`
depends_on: []                   # other SPEC-NNN this needs first
supersedes: []                   # SPEC-NNN this replaces (delta lineage)
usage:                           # running totals — accumulated across ALL phases (draft, review, build)
  total_cost:                    # e.g. $12.62
  total_duration:                # e.g. 58m 33s
  usage_by_models:               # one entry per model that touched this spec; combine across phases
    - model:                     # e.g. claude-sonnet-4-6
      input:                     # e.g. 9.9k
      output:                    # e.g. 114.8k
      cache_read:                # e.g. 13.9m
      cache_write:               # e.g. 523.7k
      cost:                      # e.g. $8.45
---

# Spec: <title>

> **Original request:** "<paste the user's ask verbatim — never paraphrase>"
> **In one line:** <one-sentence summary; this is the cheap-context version of the spec>

## 1. Goal
<!-- ONE precise, measurable sentence. State a delta: "X moves from A to B."
     Not "improve X". This is the single sentence a reviewer signs off on.
     This sentence also carries WHO benefits / WHY it matters when that's relevant —
     no separate user-story section. For pure infra it's just the change + its effect. -->
<e.g. (feature)  New users can recover a locked account themselves, cutting reset tickets from ~40/wk to 0.>
<e.g. (infra)    Rename the `specd` plugin to `spec-monkey` across all references, with zero broken cross-links.>

## 2. Context & Background
<!-- Current state from the actual codebase/product: what exists, what's broken,
     what triggers this work now. Ground the reader before the requirements. -->
- **Today:** <what exists / what the gap is>
- **Why now:** <trigger / cost of inaction>
- **Alignment:** <which product goal or `standards` invariant this serves>

## 3. Glossary
<!-- Define every load-bearing term and named actor ONCE. Requirements below
     refer to these exact names so there's no ambiguity about "the system".
     Omit if the spec has no ambiguous terms. -->
- **<Actor/Term>:** <definition>

## 4. Clarifications
<!-- The drafting interrogation, preserved — open AND resolved, so decisions stay
     visible instead of being silently baked in. `open-blocking` rows must all clear
     (and ambiguity_score ≤ 0.20) before the spec leaves `draft`. `open` rows are
     non-blocking follow-ups; `resolved` rows record what was decided and by whom. -->
| question | resolution | status |
|----------|------------|--------|
| <what was unclear> | <answer — or "—" if still open> | open-blocking \| open \| resolved |

## 5. Requirements

### Functional
<!-- Each requirement: a stable ID, a normative SHALL/MUST statement (the durable
     rule), then machine-checkable EARS acceptance criteria (the testable triggers).
     The SHALL line is the contract; the AC lines are how you verify it.
     EARS is event-driven (WHEN/IF …), not user-driven — it fits behavior changes
     and infra rules equally, no "user story" needed. -->

#### FR-001: <name>
The system SHALL <required behavior>.

**Acceptance criteria**
<!-- AC:BEGIN -->
- [ ] #1 WHEN <event> THE SYSTEM SHALL <observable response>
- [ ] #2 IF <precondition> THEN THE SYSTEM SHALL <response>
- [ ] #3 WHEN <event> AND <condition> THEN THE SYSTEM SHALL <response>
<!-- AC:END -->

### Non-Functional
#### NFR-001: <name>
- **Category:** Performance | Security | Reliability | Accessibility | …
- The system SHALL <constraint>.
- **Measurement:** <exactly how this is verified — the metric and threshold>

### Edge Cases
- <boundary / failure condition the requirements above must cover>

## 6. Data Model & Contracts *(omit / "N/A" if no data or type surface)*
<!-- The data shapes and type contracts this change introduces or alters. For a
     type-bearing change these ARE the spec's most precise part — pin them here, not
     in a design doc. Entity prose is fine for simple cases; a typed signature block
     (Pydantic / type sketch / SQL DDL) is the source of truth when types matter. -->
- **<Entity>**: <what it represents; key attributes; relationships>

```python
# typed contract block — the source of truth when the change is type-bearing
class <Name>(BaseModel):
    <field>: <type>
```

## 7. Scope
**In scope**
- <concrete deliverable>

**Out of scope**
- <excluded item> — <reason it's excluded>

## 8. Success Criteria
<!-- Measurable, technology-agnostic outcomes. "95% of X within 1s", not
     "uses Redis". These are how you know the GOAL was met, post-ship.
     "N/A — reason" is allowed for pure refactors/renames with no measurable shift. -->
- **SC-001:** <measurable outcome>

## 9. Assumptions, Constraints & Dependencies

**Assumptions** *(parseable — each row states what breaks if the assumption is wrong)*
| claim | if_wrong | confidence |
|-------|----------|------------|
| <thing taken as given> | <impact / what we'd do instead> | high \| med \| low |
<!-- A med/low-confidence row MUST also appear as an `open` row in §4, or carry a verify step. -->

**Constraints**
- <hard limit: budget, deadline, must-reuse, compliance>

**Dependencies**
- <external service / other spec / team>

## 10. Files / Change Manifest
<!-- The edit sites — one row per file. `mode` drives the diff-lint: the commit
     should touch exactly the new/modify/delete rows, no more and no less.
     `symbol` is the durable anchor (line numbers drift; symbols don't).
     `context` rows are files to READ, not change — this replaces a separate Reuse
     section, so list what to leverage here as `context` rows. -->

| id | path | mode | symbol | why |
|----|------|------|--------|-----|
| F1 | <path/to/file> | new \| modify \| delete \| context | <function / class / const> | <what changes here, or why it must be read> |

> **Companion design doc:** <link to design.md, if one exists>

## 11. Approach *(non-obvious path only — delete any line the implementer would do anyway)*
<!-- GSD-style: concrete, never abstract. Name exact symbols/paths; never "align X
     with Y" without stating the target state. Keep it to these few lines. -->
- **Mirror:** <existing pattern/file to copy — e.g. follow `summarizer.py`'s retry shape>
- **Ordering:** <what must happen before what>
- **Don't touch:** <code that looks related but must NOT change>
- **Gotchas:** <the non-obvious trap / failure mode that will bite>

## 12. Tasks *(deferred — the spec-decomposer fills this once the spec is approved)*
<!-- Tasks are the HOW; they stay empty through `draft` and `reviewed` so the spec is
     approved on intent. The spec-decomposer writes the table. `depends_on` is the source
     of truth for ordering; `wave` is derived from it (the parallel batch). `est_diff` is
     an estimated diff-line count (keep the `~`). `id*` marks optional work (e.g. extra
     tests). Each task cites the acceptance criteria (`#N`) it satisfies and the
     Files / Change Manifest rows it touches; the executor flips `done`. -->
| id | task | files | AC | depends_on | wave | est_diff | done |
|----|------|-------|----|------------|------|----------|------|
| T1 | <single-concern summary> | F1, F2 | #1, #2 | — | 1 | ~120 | [ ] |
| T2 | <…> | F3 | #3 | T1 | 2 | ~300 | [ ] |

## 13. Verification
<!-- HOW you prove the spec is met — the runnable procedure, NOT a restatement of
     §5's criteria. Give the exact commands, ONE worked case with real expected
     values, and a self-check that re-walks every acceptance criterion. -->

**Commands** *(exact invocations a reviewer/agent runs)*
```
<e.g. pytest tests/auth/test_session.py -q>
<e.g. ruff check src/auth ; mypy src/auth>
```

**Worked case** *(one concrete end-to-end example — real values, not "the correct result")*
- **Given:** <real input / starting state>
- **When:** <action / command>
- **Then:** <exact expected output, with literal values>

**Self-check** *(complete before flipping to reviewed / done)*
- [ ] Every acceptance criterion in §5 (#1…#N) re-walked and satisfied
- [ ] Every Constraint in §9 met
- [ ] `git diff` touches only the new/modify/delete rows in §10 — no stray edits

## 14. Activity Log *(append-only; spans the spec's whole life — draft, review, build)*
<!-- Lightweight audit trail. Written by whoever (human or agent) touches the spec.
     Never rewrite history here — append. Quantitative usage (cost, duration,
     per-model token usage) lives in the frontmatter `usage:` block; this
     section is the qualitative log. -->
- **Decisions & notes:** <date — what was decided, what changed, blockers hit>
- **Files changed:** <paths>
- **Final summary:** <what shipped, what was deferred, links to PR/commit>

---

# Appendix — Design rationale (element → source → why)

| Element | Borrowed from | Why it earns its place |
|---|---|---|
| Frontmatter IDs + `status` lifecycle | Backlog.md, ccpm | Machine-parsable identity; lets tooling/agents find, sort, and gate specs. |
| `status: draft→reviewed→applied→archived` | OpenSpec, Backlog.md | An explicit lifecycle is the spine of human approval gates. |
| `standards:` constitution pointer | agent-os (Standards), spec-workflow-mcp (steering), OpenSpec (`AGENTS.md`) | Names the repo's commands, code style, and git rules so the implementer/agent doesn't re-derive them; keeps the spec self-contained without duplicating the constitution. |
| `ambiguity_score` ≤ 0.20 gate | GSD | A *quantified* quality bar beats "looks done" — blocks vague specs from proceeding. |
| `depends_on` / `supersedes` | ccpm, OpenSpec | Enables ordering and a delta lineage (the spec-as-diff / constitution model). |
| `usage:` running totals (cost/duration + per-model token & cost breakdown) | your current v3 template | One phase-agnostic block that accumulates resource use across drafting, review, and build — no create-vs-execute split. Queryable for cost/model analysis across the repo. |
| **Original request (verbatim)** | spec-kit | The source of truth for intent; paraphrasing on capture is where drift starts. |
| **In one line** (spec-lite) | agent-os | A cheap-context summary an agent can load without the whole doc — real token savings. |
| §1 Goal as one measurable delta (carries who/why) | GSD; replaces user stories | Forces a single, falsifiable objective; folds in the beneficiary when there is one, and degrades cleanly to "rename X" when there isn't. |
| §2 Context & Background | GSD, potpie | Grounds requirements in the real current state, not a vacuum. |
| §3 Glossary of named actors | Kiro | Kills "the system" ambiguity; requirements reference exact, defined names. |
| §4 Clarifications (open + resolved) | spec-kit (`[NEEDS CLARIFICATION]`) + GSD gate | Open blockers gate promotion; preserving resolved rows keeps decisions visible — stops assumption-laundering. Absorbs the old Open Questions (status `open`). |
| §5 RFC-2119 `SHALL` statements | OpenSpec | Normative keywords make the durable rule unambiguous. |
| §5 EARS acceptance criteria | Kiro, spec-workflow-mcp | `WHEN…THE SYSTEM SHALL…` yields testable, event-driven criteria — no user-story frame needed. |
| `FR-NNN` / `NFR-NNN` / `SC-NNN` IDs | spec-kit | Stable handles that tasks, tests, and design docs can back-reference. |
| Machine-checkable AC (`<!-- AC:BEGIN -->`, `#1` indices) | Backlog.md | Stable indices let an agent/CLI check off criteria programmatically. |
| NFR `Category` + `Measurement` | potpie | A non-functional req without a measurement is untestable; this forces one. |
| §6 Data Model & Contracts (typed blocks allowed) | spec-kit (entities) + potpie (data models) + types-first | For a type-bearing change the typed contract is the spec's *most precise* part; pinning it here (Pydantic/DDL) beats exiling it to a design doc. |
| §7 Scope with reasons for exclusions | GSD, ccpm | "Out of scope" with a *reason* prevents re-litigating later. |
| §8 Measurable Success Criteria (N/A allowed) | spec-kit | Defines done at the outcome level, decoupled from implementation; refactors opt out with a reason. |
| §9 Assumptions as a table (`claim \| if_wrong \| confidence`) | GSD | Parseable risk surface; `if_wrong` forces impact analysis; low-confidence rows must surface as clarifications. |
| §10 Files / Change Manifest (path \| mode \| symbol \| why) | Claude Code plans (organize by file), GSD (`files_modified`) | Engineering specs change *specific code*. Most lintable element (diff must match new/modify/delete rows); `context` rows are the token-saver and absorb the old Reuse section. |
| §11 Approach (Mirror / Ordering / Don't-touch / Gotchas) | GSD (`<action>` blocks) | The non-obvious implementation path — concrete seams, ordering, traps. Lean by construction: delete anything the model would do unprompted. |
| §12 Tasks deferred, filled by spec-decomposer (`depends_on` / `wave` / `est_diff`) | Backlog.md (discipline + `done`), ccpm/GSD (parallel/waves) | Approve on intent before implementation; `depends_on` orders the DAG, `wave` exposes parallel batches, `est_diff` keeps each task reviewable, `done` makes a run resumable. |
| Tasks carry `AC` / `files` columns | BMAD, Kiro, spec-workflow-mcp | Full traceability: every task maps to a criterion and a manifest row. |
| `id*` optional-task marker | Kiro | Distinguishes required work from nice-to-have (e.g. extra tests). |
| §13 Verification (commands + worked case + self-check) | your saved plan files, Kiro | Proves the spec runs: commands are executable, the worked case pins *real* expected values, the self-check re-walks every criterion and the manifest diff. |
| §14 Activity Log (append-only) | BMAD (Dev Agent Record), Backlog.md (notes) | A phase-agnostic audit trail of what actually happened across the spec's life, kept with the spec. |

## Deliberately left out (and why)

- **User stories / "As a… I want… so that…" scenarios** (BMAD, ccpm, spec-kit, agent-os) — product-management ceremony. Most specs here are engineering/infra (renames, schema changes, agent swaps) with no conventional user, so the format would force fake stories. The three real jobs of a user story are already covered elsewhere: the *who-benefits/why* lives in §1 Goal (stated as an outcome), *testability* lives in §5 EARS criteria, and *MVP-slicing/prioritization* lives at the feature-index level (`_index.md`), not inside one spec. User stories belong on the Jira board the spec points to — not in the spec.
- **Mermaid architecture / sequence diagrams** (potpie, Kiro `design.md`) — design-layer detail. Inlining it breaks the *what-before-how* discipline; §10 links to a design doc instead.
- **Full DB schema / API contract files** (agent-os `database-schema.md`, `api-spec.md`) — companion design artifacts. The *contract-level* types live in §6; the exhaustive schema does not.
- **GSD's XML atomic-plan format** — an execution-orchestration syntax. The §12 Tasks table's `depends_on` + `wave` capture ordering and parallel batches without the heavyweight XML.
- **Per-task embedded `_Prompt:_` (Role/Task/Restrictions/Success)** (spec-workflow-mcp) — over-engineered. Task text + AC + Files already give an agent enough to act.
- **ccpm GitHub-sync fields** (`github:`, `conflicts_with`) — tool-specific PM plumbing, not spec content. Kept `depends_on`; dropped the issue-tracker glue.
- **BMAD's six-persona roles + full debug-log scaffolding** — process machinery. Kept the lightweight §14 log, dropped the ceremony.
- **Rollback / Ops section** — rely on dead-code-then-delete + abort-loud; not a standing template section.

## Note on one file vs. three

The field has converged on three *phases* (requirements → design → tasks), not three *files*. This master spec is the **requirements/intent** layer — the durable contract — with Tasks as a *deferred* section and full design *delegated* via §10. If you prefer the split, lift §5–§8 into `requirements.md`, move §6 (data model) + §11 (approach) into `design.md`, and promote §12 (Tasks) + §13 (Verification) into `tasks.md`; the IDs and back-references already make them link cleanly.

## Parse contract (for a future CLI)

The spec is **structured Markdown**: a human-first document with machine-readable islands. A parser reads it WITHOUT understanding prose. The `.md` is the source of truth; the CLI parses it *to* JSON — you never hand-author JSON.

1. **Frontmatter** — YAML between the leading `---` fences. Holds every queryable scalar (`status`, `usage`, `ambiguity_score`, `depends_on`, `supersedes`). Never bury a queryable value in prose.
2. **Sections** — split the body on `^## (\d+)\. <name>`. The canonical section set and order *are* the schema; treat them as frozen. (Sub-structure splits on `^### `.)
3. **Typed islands inside a section:**
   - **Tables** (`| … |` with a header row) → array of row-objects keyed by column name. Used by §4, §9, §10, §12. Escape any literal `|` inside a cell.
   - **Fenced blocks** (` ```lang `) → captured verbatim with the language tag. Used by §6 (typed contracts) and §13 (commands).
   - **Marker regions** `<!-- AC:BEGIN -->` … `<!-- AC:END -->` → the lines between, each `#(\d+) <text>`.
4. **Two prose conventions, nothing else:**
   - `- **Key:** value` → a key/value field. Used by §2, §3, §11, and Given/When/Then in §13. One regex catches all: `^- \*\*(.+?):\*\*\s*(.*)$`.
   - `**Group**` on its own line → introduces the list / table / block that follows. Used by §7 (In/Out scope), §9 (Assumptions/Constraints/Dependencies), §13 (Commands/Worked case/Self-check).
   - Anything else is opaque prose, captured as text keyed by its heading (§1, §14).
5. **IDs are the join keys.** `FR-NNN`, `NFR-NNN`, `SC-NNN`, AC `#N`, file `F#`, task `#` — unique within a spec. The traceability graph (task → AC → FR → file) is built from these alone, so a linter can check manifest↔diff, symbol resolution, and that every AC is covered by a task.
