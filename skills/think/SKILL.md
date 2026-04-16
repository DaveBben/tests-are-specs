---
name: think
effort: high
model: opus
disable-model-invocation: true
argument-hint: "[change request]"
description: >
  Pre-planning skill for feature and change requests. Scopes intent,
  traces codebase impact, evaluates approaches, and surfaces consequences
  for human decision-making. Output is a focused brainstorm.md (under 200
  lines) that feeds /plan. Do NOT use for bugs (use /cks:bug). Do NOT use
  for trivial one-line changes (just make the change).
---

# Think — Scoping and Impact Analysis

> The purpose of this skill is to make human architectural decisions
> *before* AI starts planning. AI investigates and surfaces consequences.
> The human decides. Everything written to brainstorm.md reflects
> decisions made in this conversation, not AI proposals.

```
User describes change → /cks:think
  Phase 1: Intent (what + why + constraints)
  Phase 2: Impact (codebase tracing, at-risk tests, approaches)
  Phase 3: Decisions (human chooses approach, confirms boundaries)
  Phase 4: Write brainstorm.md
```

Artifacts written to `.claude/features/{slug}/brainstorm.md`.

**Slug generation:** derive a URL-safe slug from the change description
(lowercase, hyphens for spaces, no special characters, max 40 chars).
If a `.claude/features/{slug}/` directory already exists, resume from
the existing brainstorm.md rather than starting over.

---

## Phase 1: Intent

### Step 1 — Clarify What and Why

Evaluate `$ARGUMENTS`:
- **What** is the concrete change?
- **Why** does it need to exist?

If both are clear, state your understanding and ask for confirmation.
If either is unclear, ask for the missing piece. Do not guess at "why."

Then ask in the same message:

> "Is there any context outside this codebase that's relevant — specs,
> other repos, business constraints, URLs, prior decisions?"

Fetch any URLs provided. Record external context — it will appear in
brainstorm.md's Constraints section.

### Step 2 — Three Focused Scope Questions

Generate exactly **3 questions** about things only the user knows that
the code cannot answer. Each must reference this specific change.
Good questions target: what is explicitly out of scope, backwards
compatibility requirements, and the quality/correctness bar.

Do not ask generic questions. Present all 3 at once. Wait for answers
before proceeding.

---

## Phase 2: Impact Analysis

### Step 3 — Codebase Investigation (silent)

Read `CLAUDE.md`, `spec.md`, and any domain `spec.md` files relevant to
this change. Do not summarize these — use them to orient investigation.

Launch **3 parallel Explore agents** (blast radius, existing patterns,
data shapes) using the questions in
[agent-questions.md](references/agent-questions.md). Agents retrieve
raw findings only — they do not reason about approaches or trade-offs.

Once agents return, **synthesize in the main session** (do not delegate):
- Concern groups and dependency chain (from blast radius)
- 2-3 implementation approaches grounded in findings (from patterns)
- Load-bearing types/interfaces and serialization boundaries (from data shapes)
- 2-3 highest-consequence failure modes (across all three)
- **Security flag**: if blast radius includes auth, validation, query
  construction, or external endpoints, call it out as a hard constraint
  in brainstorm.md — not a suggestion.

**Checkpoint**: After synthesis, write a draft brainstorm.md
(`Status: Draft`, `DraftDate: YYYY-MM-DD`) with the findings so far —
impact surface, at-risk test candidates, approaches, failure modes.

On resume (directory exists, Draft brainstorm.md present):
- If `DraftDate` is ≤3 days old: skip to Step 4.
- If `DraftDate` is >3 days old: spot-check 3 file:line references
  from the draft against the current codebase. If any are stale, warn:
  > "Draft brainstorm.md is {N} days old and some references have
  > changed. Re-run investigation or continue with stale findings?"
  If user continues, proceed to Step 4. If re-run, delete draft and
  restart from Step 3.

The draft is overwritten in Phase 4 with the final version.

### Step 4 — Surface Findings to User

Present findings in three batches. Do not dump everything at once.

**Batch 1 — Impact surface:**
List the files that will change, grouped by concern (not flat list).
For each group: one sentence on why it's affected.

Ask: "Does anything here surprise you? Is there a file you expected to
be involved that isn't, or one you didn't expect?"

Wait for response before proceeding.

**Batch 2 — At-risk tests (predict-before-reveal):**
Before presenting any test list, ask:

> "Which tests do you think are at risk from this change?"

Wait for their answer. Then present the AI-identified list for
comparison — highlight where it agrees and where it differs. This
breaks anchoring so the user evaluates the list independently.

> "Here are the tests I found that could regress: [list with reasons].
> Combined with yours, does this look complete?"

**This list requires human confirmation before it goes into
brainstorm.md.** An incorrect at-risk test list is worse than none.

Wait for confirmation.

**Batch 3 — Approaches (predict-before-reveal):**
Ask: "What approach would you take? High level is fine."

Wait for their answer. If they have no instinct, acknowledge and
proceed. Then present the 2-3 approaches as constraint elimination:
lead with what limits the design space, then show how each approach
follows. Where the human's instinct aligns, say so. Where it diverges,
explain the trade-off with specific findings.

Do not recommend one. The human decides.

**Checkpoint**: After the user chooses an approach, update the draft
brainstorm.md with `Phase: AwaitingDecisions` and record the confirmed
impact surface, at-risk tests, and chosen approach. On resume with
`Phase: AwaitingDecisions`, skip to Step 5 — do not re-present
Batches 1-3.

---

## Phase 3: Decisions

### Step 5 — Confirm Boundaries

Based on the chosen approach and scope answers, present explicit
boundaries for human confirmation:

> "Based on what we've discussed, here's what this change will NOT do:
> [list]
>
> And here's what MUST NOT change:
> [list]
>
> Do these match your intent, or should I adjust?"

Wait for confirmation or corrections. These boundaries become the
`doNot` and `constraints` fields in every task the Plan skill produces.
Getting them wrong here is harder to fix downstream.

### Step 6 — Failure Modes and Reversibility

Present the 2-3 highest-consequence failure modes from Step 3. Focus on
**irreversible or silently-broken** scenarios only. For each, get a
human decision on how to handle it.

Additionally, if applicable (skip if not):
- **Data/state migration**: if change touches persisted data or schemas,
  ask about migration/backfill/coexistence
- **Rollback story**: if change involves migrations or breaking
  interface changes, ask about safe revert

Record answers in brainstorm.md. Unresolved items → `[TBD]`.

---

## Phase 4: Write brainstorm.md

Write `.claude/features/{slug}/brainstorm.md` using the
[brainstorm.md template](references/templates.md#brainstormmd).

**Hard rules:** under 200 lines; only confirmed decisions (unresolved
→ `[TBD]`); unconfirmed tests → `[unverified]`; every file:line
verified on disk; no implementation details (code goes in plan.md).

Present to user for review. Apply corrections. On approval, set
Status to `Approved`, update Date, and direct user to run
`/cks:plan .claude/features/{slug}`.
