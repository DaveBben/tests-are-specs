<!--
SPEC TEMPLATE — the canonical engineering-spec format.
This is the shape every spec takes. It is outcome-first — it works
for renames, schema changes, and refactors as well as features. The spec is the WHAT and
WHY; deep design (diagrams, full schemas) lives in a linked design doc — keep it out.
Fill the < > placeholders. Delete guidance comments before review.

SINGLE SOURCE OF TRUTH: each decision lives in ONE section; everywhere else REFERENCES it by ID
(FR-001, SC-001, F3, a config name), never restates it — restating is the top cause of bloat and
drift. So: Edge Cases and Verification cite the FR they exercise; the Glossary doesn't redefine a
type Data Model & Contracts already signs; a rationale is stated once (Assumptions) and referenced.
Two sections saying the same thing → one is a copy; cut it to a reference.
-->

---
schema_version: 2                # spec format version; tooling branches on this
id: SPEC-NNN                      # stable handle; tasks/commits reference this
title: <short imperative title>
status: draft                    # draft → reviewed → applied → archived
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
owners: [<@handle>]
branch: NNN-<kebab-title>
standards: standards.md          # the constitution — ONE of: standards.md | CLAUDE.md | AGENTS.md
depends_on: []                   # other SPEC-NNN this needs first
supersedes: []                   # SPEC-NNN this replaces (delta lineage)
---

# Spec: <title>

> **Original request:** "<paste the user's ask verbatim — never paraphrase>"
> **In one line:** <one-sentence summary; this is the cheap-context version of the spec>
> **Reviewing the design?** Read *Goal* → *Assumptions*. **Building it?** *Files / Change Manifest* onward.

## 1. Goal
<!-- ONE precise, measurable sentence. State a delta: "X moves from A to B."
     Not "improve X". This is the single sentence a reviewer signs off on.
     This sentence also carries WHO benefits / WHY it matters when that's relevant —
     no separate user-story section. For pure infra it's just the change + its effect.
     The measurable DELTA — not a third paraphrase of Original request / In one line. If it just
     re-says the one-liner, sharpen it to a metric. -->
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
     Omit if the spec has no ambiguous terms.
     AMBIGUOUS DOMAIN terms only. Don't redefine types that Data Model & Contracts signs
     (TargetSlot, …) — define those once there and reference them; defining in both violates SSOT. -->
- **<Actor/Term>:** <definition>

## 4. Clarifications
<!-- The drafting interrogation, preserved. `open-blocking` rows clear before `draft` ends;
     `open` are non-blocking follow-ups — both carry the full question. A `resolved` row is a
     POINTER: its resolution cell names WHERE the decision lives (an FR/config/Data Model contract),
     not a re-prose of the answer. Re-stating the FR's behavior here violates SSOT — collapse it
     to the reference. -->
| question | resolution | status |
|----------|------------|--------|
| <what was unclear> | → FR-008 (or: → `DISPLAY_FULLSCREEN` config / → Data Model contract) | resolved |
| <still-open question> | <partial answer — or "—"> | open-blocking \| open |

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
<!-- State each rationale ONCE. If a constraint exists because of an assumption (e.g. SDL needs
     the main thread), the Assumptions table owns the "why" — reference it. Measurement is HOW you
     verify, not why. -->
#### NFR-001: <name>
- **Category:** Performance | Security | Reliability | Accessibility | …
- The system SHALL <constraint>.
- **Measurement:** <exactly how this is verified — the metric and threshold>

### Edge Cases
<!-- ONLY cases an AC doesn't already state — a non-obvious branch (corrupt-vs-missing, alpha-
     flatten, boot race). If a case just re-describes an FR, cite it in one line —
     `<condition> → <result>. (FR-006)` — don't re-prose it or mirror the AC table. -->
- <non-obvious boundary / failure the ACs don't already pin> → <behavior>. (FR-0xx)

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
<!-- A med/low-confidence row MUST also appear as an `open` row in Clarifications, or carry a verify step. -->

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
     the Requirements criteria. Give the exact commands, ONE worked case with real
     expected values, and a self-check that re-walks every acceptance criterion.
     The Worked case shows the WORKING an AC asserts but doesn't derive — the arithmetic, the
     real expected values, the integration sequence. It must not re-type an AC. If your worked
     case reads identically to an AC line, it's a copy: delete it and keep the derivation. -->

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
- [ ] Every acceptance criterion in Requirements (#1…#N) re-walked and satisfied
- [ ] Every NFR's Measurement met (or flagged as needing a benchmark)
- [ ] Every Constraint met
- [ ] `git diff` touches only the new/modify/delete rows in Files / Change Manifest — no stray edits

## 14. Activity Log *(append-only; spans the spec's whole life — draft, review, build)*
<!-- Lightweight audit trail. Written by whoever (human or agent) touches the spec.
     Never rewrite history here — append. This is the qualitative log of what happened.
     A "spec gap / proposed amendment" noted here MUST also be recorded as an `open` row in
     Clarifications — that's where open decisions surface for the next reader; don't leave one
     buried in a log paragraph. -->
- **Decisions & notes:** <date — what was decided, what changed, blockers hit>
- **Files changed:** <paths>
- **Final summary:** <what shipped, what was deferred, links to PR/commit>

---

# Parse contract (for a future CLI)

The spec is **structured Markdown**: a human-first document with machine-readable islands. A
parser reads it WITHOUT understanding prose. The `.md` is the source of truth; the CLI parses
it *to* JSON — you never hand-author JSON.

1. **Frontmatter** — YAML between the leading `---` fences. Holds every queryable scalar
   (`schema_version`, `status`, `depends_on`, `supersedes`). Never bury a
   queryable value in prose.
2. **Sections** — split the body on `^## (\d+)\. <name>`. The canonical section set and order
   *are* the schema; treat them as frozen. (Sub-structure splits on `^### `.)
3. **Typed islands inside a section:**
   - **Tables** (`| … |` with a header row) → array of row-objects keyed by column name. Used
     by Clarifications, Assumptions, Files / Change Manifest, and Tasks. Escape any literal
     `|` inside a cell.
   - **Fenced blocks** (` ```lang `) → captured verbatim with the language tag. Used by Data
     Model & Contracts and Verification commands.
   - **Marker regions** `<!-- AC:BEGIN -->` … `<!-- AC:END -->` → the lines between, each
     `#(\d+) <text>`.
4. **Two prose conventions, nothing else:**
   - `- **Key:** value` → a key/value field. One regex catches all: `^- \*\*(.+?):\*\*\s*(.*)$`.
   - `**Group**` on its own line → introduces the list / table / block that follows.
   - Anything else is opaque prose, captured as text keyed by its heading.
5. **IDs are the join keys.** `FR-NNN`, `NFR-NNN`, `SC-NNN`, AC `#N`, file `F#`, task `T#` —
   unique within a spec. The traceability graph (task → AC → FR → file) is built from these
   alone, so a linter can check manifest↔diff, symbol resolution, and that every AC is
   covered by a task.
