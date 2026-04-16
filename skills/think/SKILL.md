---
name: think
effort: medium
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

Launch **3 parallel Explore agents** to retrieve raw findings only.
Agents search and read — they do not reason about approaches or trade-offs.

**Agent 1 — Blast radius:**
1. Which files contain the entry point and immediate consumers of this
   change? Follow imports one level deep from the entry point.
2. Which test files import, mock, or call into any of those files?
   Return: file path, test symbol (describe/it/test block name).
3. What is the import chain from the app entry point to the target
   symbol? Return the ordered list of file paths (3-5 hops max).

**Agent 2 — Existing patterns:**
1. Does anything structurally similar already exist in the codebase
   that this change could extend rather than duplicate?
   Return: file:line and one sentence on what it does.
2. Are there any TODOs, FIXMEs, or comments in the target area that
   mention relevant constraints or known issues?
   Return: file:line and the comment text verbatim.
3. What is the closest analogous change already made in this codebase?
   Return: file:line of the reference implementation.

**Agent 3 — Data shapes and contracts:**
1. What type definitions, interfaces, or schemas describe data flowing
   through the target area? Return: file:line for each type/interface.
2. What external callers consume the output of the target — routes, API
   handlers, queue consumers, other services? These are what break
   silently when a shape changes. Return: file:line for each caller.
3. Are there serialization boundaries near the target — places where
   data is written to a database, cache, queue, or sent over the wire
   in a format that encodes the current shape?
   Return: file:line and the storage mechanism (e.g. "postgres column",
   "redis key", "JSON response body").

Cap each agent's return to **3 lines per question**. Format:
```
Q: [question]
A: file:line — [finding]
Note: [one sentence max]
```

If any question lacks a `file:line` answer, note it as "not found" —
do not invent answers. Unverified context is worse than no context.

Once agents return, **synthesize in the main session** (do not delegate):
- From blast radius: identify concern groups affected and their dependency chain
- From patterns: identify 2-3 distinct implementation approaches, each
  grounded in what the agents found — what each touches, risks, and avoids
- From data shapes: identify which types/interfaces are load-bearing
  (changing them breaks external callers or serialized data), and which
  serialization boundaries constrain what the change can safely do
- Across all three: identify the 2-3 highest-consequence failure modes —
  things that would break silently or be hard to reverse
- **Security flag** (only if the blast radius includes any of the following):
  auth middleware, permission guards, input validation, query construction,
  or external-facing endpoints. If present, call it out explicitly:
  > "This change touches a security-relevant surface: [file:line].
  > The chosen approach must preserve [the auth check / validation / etc]."
  This becomes a hard constraint in brainstorm.md — not a suggestion.

### Step 4 — Surface Findings to User

Present findings in three batches. Do not dump everything at once.

**Batch 1 — Impact surface:**
List the files that will change, grouped by concern (not flat list).
For each group: one sentence on why it's affected.

Ask: "Does anything here surprise you? Is there a file you expected to
be involved that isn't, or one you didn't expect?"

Wait for response before proceeding.

**Batch 2 — At-risk tests:**
List every test that could regress, with the reason for each.
Ask the user to confirm or correct the list:

> "These are the tests I believe are at risk. Do any of these seem
> wrong, or are there tests I've missed?"

**This list requires human confirmation before it goes into
brainstorm.md.** An incorrect at-risk test list is worse than none.

Wait for confirmation.

**Batch 3 — Ask first, then compare:**
Before presenting any approaches, ask:

> "Given what you've seen — the impact surface, the at-risk tests, the
> data constraints — what approach would you take? High level is fine."

Wait for their answer. If they have no instinct ("I don't know", "you
tell me"), acknowledge it and proceed directly to presenting the
approaches — do not push for a prediction they don't have. Then present
the 2-3 approaches synthesized from the findings. For each, show what it touches and what it risks. Where
the human's instinct aligns with an approach, say so. Where it diverges,
explain the trade-off — not "you're wrong" but "that direction risks X
because of [specific finding]."

Do not recommend one. The human decides. If they ask for a
recommendation, surface the constraint that most limits the options and
ask again — the finding should point toward the answer, not you.

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

Present the 2-3 highest-consequence failure modes synthesized in Step 3.
For each, ask how it should be handled if it goes wrong.

The goal is not to enumerate every edge case — it is to surface
**irreversible or silently-broken** scenarios and get a human decision
before planning begins. If a failure mode has an obvious answer, state
it and confirm. Only ask explicitly when the right answer is unclear.

Then ask two additional questions if the investigation found either
condition — skip if neither applies:

**Data/state migration** (ask only if the change touches persisted data,
a schema, a stored format, or a shared cache):
> "This change touches [X]. What happens to existing data — does it need
> migrating, backfilling, or can old and new formats coexist?"

**Rollback story** (ask only if the change involves a migration, a
breaking interface change, or removes something callers depend on):
> "If this needs to be reverted after deploying — is that clean, or does
> it leave the system in a broken state? Is there anything we should
> design now to make rollback safe?"

Record the answers in brainstorm.md's Failure Modes Decided section.
If no decision is reached, mark `[TBD]` — do not choose for the user.

---

## Phase 4: Write brainstorm.md

Write `.claude/features/{slug}/brainstorm.md` using the
[brainstorm.md template](references/templates.md#brainstormmd).

**Hard rules for this file:**
- **Under 200 lines.** If you're approaching 200, cut — omit empty
  sections, compress prose, remove anything derivable from the code.
- **Only confirmed decisions.** Do not write speculative content.
  If the human hasn't decided something, mark it `[TBD]` — do not
  choose for them.
- **Every at-risk test was confirmed by the human.** If a test is on
  the list without human confirmation, mark it `[unverified]`.
- **Every file:line reference must exist on disk.** Do not include
  references that weren't verified during investigation.
- **No implementation details.** brainstorm.md contains decisions and
  constraints, not code. Code goes in plan.md (Phase 2 of /plan).

Present to user:

> "brainstorm.md is at `.claude/features/{slug}/brainstorm.md`.
> Review it and either:
> 1. **Correct anything** — tell me what's wrong
> 2. **Approve** — say 'approve' to proceed to /cks:plan"

Apply any corrections. Once approved, set the Status field in
brainstorm.md to `Approved` and update the Date to today. Then say:

> "Run `/cks:plan .claude/features/{slug}` to generate the
> implementation plan from this brainstorm."
