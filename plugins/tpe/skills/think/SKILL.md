---
name: think
effort: max
model: opus
disable-model-invocation: true
argument-hint: "[change request]"
description: >
  Pre-planning skill for feature and change requests. Scopes intent,
  traces codebase impact, evaluates approaches, and surfaces consequences
  for human decision-making. Output is a focused brainstorm.md (under 200
  lines) that feeds /plan. Do NOT use for bugs (use /tpe:bug). Do NOT use
  for trivial one-line changes (just make the change).
---

# Think — Scoping and Impact Analysis

> The purpose of this skill is to make human architectural decisions
> *before* AI starts planning. AI investigates and surfaces consequences.
> The human decides. Everything written to brainstorm.md reflects
> decisions made in this conversation, not AI proposals.

```
User describes change → /tpe:think
  Phase 1: Intent (what + why + constraints)
  Phase 2: Impact (codebase tracing, at-risk tests, approaches)
  Phase 3: Decisions (human chooses approach, confirms boundaries)
  Phase 4: Write brainstorm.md
```

Artifacts written to `.claude/features/{slug}/brainstorm.md`.

**Slug generation:** derive a URL-safe slug from the change description (lowercase, hyphens for spaces, no special characters, max 40 chars). If a `.claude/features/{slug}/` directory already exists, verify the existing brainstorm.md's "What and Why" section describes the same change before resuming. If it describes a different change, append a numeric suffix to the slug (e.g., `add-user-auth-2`).

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

Use the WebFetch tool to retrieve any URLs provided. Record external context — it will appear in brainstorm.md's Constraints section.

### Step 2 — Three Focused Scope Questions

Generate exactly **3 questions** about things only the user knows that the code cannot answer. Each must reference this specific change and must be answerable in one sentence. Each answer must change what you would investigate in Phase 2 — if it would not, discard the question and generate a replacement.

If the change is narrow enough that fewer than 3 qualifying questions exist, state how many you have and why additional questions would not change the investigation.

Good questions target: what is explicitly out of scope, backwards compatibility requirements, and the quality/correctness bar.

**Quality filter:** A good scope question names a specific fork in the road ("Should X also handle Y, or is Y out of scope?"). A bad one asks for open-ended preferences ("What's your quality bar?" — too vague to act on) or asks something the codebase can answer ("Are there tests for X?" — that's Phase 2's job).

Do not ask generic questions. Present all 3 at once. Wait for answers before proceeding.

---

## Phase 2: Impact Analysis

### Step 3 — Codebase Investigation (silent)

Read `CLAUDE.md` and, if present, `spec.md` and any domain `spec.md` files relevant to this change. Do not summarize these — use them to orient investigation.

Launch **3 parallel Explore agents** using the Agent tool with `subagent_type: "Explore"`. Issue all 3 Agent tool calls in a single message to ensure parallel execution. Each agent investigates one dimension (blast radius, existing patterns, data shapes) using the questions in [agent-questions.md](references/agent-questions.md). Agents retrieve raw findings only — they do not reason about approaches or trade-offs.

Once agents return, **synthesize in the main session** (do not delegate). Synthesis consists of the following steps:

**1. Investigation scope cap:** if the combined agent findings touch more than 12 files, group by concern and limit detailed analysis to the top 4 concern groups (by number of affected files). List remaining groups by name and file count only — the user can request expansion. This prevents rabbit-holing on large surface areas while preserving completeness in the summary.

**2. Step back first**: before producing any outputs, classify the change.
Is it **additive** (new path through existing infra — risk is shadowing
or resource contention), **modificative** (altering shared contracts —
risk is every consumer, failures are silent type mismatches), or
**extractive** (pulling apart coupled code — risk is severing implicit
dependencies)? State the classification in one sentence. This frames
the failure modes and approaches below — an additive change and a
modificative change have fundamentally different risk profiles even
when they touch the same files.

**3. Interrogate inherited constraints**: the failure to guard
against here is **anchoring on the current implementation** — treating
existing data shapes, file layouts, and interfaces as fixed inputs to
the problem when they're design choices someone made upstream.
Experienced engineers get bitten by this specifically because they're
good at solving problems within a frame; the clean downstream solution
offers no pain signal to step back. The habit to enforce is asking
"why am I solving this problem at all?" *before* "what's the best way
to solve it?"

Practical trigger: if any candidate approach below would require
adding concurrency machinery (thread pools, parallel fetches), retry
or caching layers, translation shims, or defensive validation to
bridge a shape mismatch, ask whether the *need* for that machinery can
be removed by changing the upstream shape instead of accommodated. The
answer is often no — but the question is cheap and the alternative
never surfaces unless asked.

Mechanically: list the upstream data shapes, interfaces, and
structural decisions this change inherits. Classify each as
*externally fixed* (third-party API contract, regulatory requirement,
persisted state that can't be cheaply migrated) or *internally
malleable* (a prior design decision on this team). For any
internally-malleable constraint the practical trigger flagged, surface
"redesign the upstream shape" as a candidate approach in Batch 3
alongside the approaches that accept the shape as-is. The skill's job
is to make sure the human sees this choice — not to pick for them.

**4. Produce outputs:**
- Concern groups and dependency chain (from blast radius)
- 2-3 implementation approaches grounded in findings (from patterns).
  Each approach must differ on which constraint it sacrifices or which
  risk it accepts. If two approaches trade the same thing, they are
  variants — pick the stronger one and discard the other.
- Load-bearing types/interfaces and serialization boundaries (from data shapes)
- 2-3 highest-consequence failure modes — identify these twice using
  different frames: first "what breaks silently?" (returns wrong data,
  corrupts state, passes tests while wrong), then "what's irreversible?"
  (data loss, schema migration, published API contract). Take the union.
  Rank by cost-to-fix-after-discovery, not by likelihood of occurrence —
  a rare data-corruption bug outranks a common build break.
  Single-pass failure analysis anchors on the obvious risk and misses
  the subtle one.
- **Security flag**: if blast radius includes auth, validation, query construction, or external endpoints, call it out as a hard constraint in brainstorm.md — not a suggestion.

**5. At-risk test convergence check**: each agent independently identifies
test files that could regress. During synthesis, compare their lists:
- Tests named by **2+ agents** → confirmed at-risk (present in Batch 2
  as the primary list)
- Tests named by **only 1 agent** → uncertain (present separately in
  Batch 2 as "lower-confidence candidates — these appeared in only one
  investigation thread")

This filters out low-confidence items. An incorrect at-risk test is
worse than a missing one.

**Checkpoint**: After synthesis, write a draft brainstorm.md (`Status: Draft`, `DraftDate: YYYY-MM-DD`) with the findings so far — impact surface, at-risk test candidates, approaches, failure modes.

On resume (directory exists, Draft brainstorm.md present):
- If `DraftDate` is ≤3 days old: skip to Step 4.
- If `DraftDate` is >3 days old: spot-check 3 file:line references from the draft against the current codebase. If any are stale, warn:
  > "Draft brainstorm.md is {N} days old and some references have changed. Re-run investigation or continue with stale findings?"
  If user continues, proceed to Step 4. If re-run, delete draft and restart from Step 3.

The draft is overwritten in Phase 4 with the final version.

### Step 4 — Surface Findings to User

Present findings in three batches. Do not dump everything at once.

**Batch 1 — Impact surface:**
List the files that will change, grouped by concern (not flat list). For each group: one sentence on why it's affected.

Ask: "Does anything here surprise you? Is there a file you expected to be involved that isn't, or one you didn't expect?"

Update the draft brainstorm.md with `LastBatch: 1`. Wait for response before proceeding.

**Batch 2 — At-risk tests (predict-before-reveal):**
Before presenting any test list, ask:

> "Which tests do you think are at risk from this change?"

Wait for their answer. Then present the two tiers from the convergence check:

> "**High-confidence** (identified by multiple investigation threads):
> [list with reasons]
>
> **Lower-confidence candidates** (appeared in only one thread):
> [list with reasons]
>
> Combined with yours, does this look complete?"

**This list requires human confirmation before it goes into brainstorm.md.** An incorrect at-risk test list is worse than none.

Update the draft brainstorm.md with `LastBatch: 2`. Wait for confirmation.

**Batch 3 — Approaches (predict-before-reveal):**
Ask: "What approach would you take? High level is fine."

Wait for their answer. If they have no instinct, acknowledge and proceed. Then present the 2-3 approaches as constraint elimination: lead with what limits the design space, then show how each approach follows. If the human's instinct aligns with an approach, note the alignment. If it diverges, state what the human's approach trades off without characterizing it as better or worse.

Present trade-offs factually. Do not add a summary recommendation or rank approaches. The human decides.

**Checkpoint**: After the user chooses an approach, update the draft brainstorm.md with `Phase: AwaitingDecisions` and record the confirmed impact surface, at-risk tests, and chosen approach. Also record `LastBatch: 3` to track presentation progress.

On resume with `Phase: AwaitingDecisions`, skip to Step 5 — do not re-present Batches 1-3. On resume with a Draft brainstorm.md that has `LastBatch: 1` or `LastBatch: 2`, resume from the next undelivered batch rather than re-presenting all batches.

---

## Phase 3: Decisions

### Step 5 — Confirm Boundaries

Based on the chosen approach and scope answers, present explicit boundaries for human confirmation. At minimum, evaluate each of these boundary categories and include any that apply:

- **Data model / schema**: tables, columns, serialization formats that must not change
- **Public API surface**: endpoints, response shapes, CLI flags consumers depend on
- **Performance characteristics**: latency budgets, batch sizes, concurrency limits
- **Backwards compatibility**: old clients, migration coexistence, feature flags

Skip categories that are clearly not applicable — do not pad with irrelevant boundaries.

> "Based on what we've discussed, here's what this change will NOT do:
> [list]
>
> And here's what MUST NOT change:
> [list]
>
> Do these match your intent, or should I adjust?"

Wait for confirmation or corrections. These boundaries become the `doNot` and `constraints` fields in every task the Plan skill produces. Getting them wrong here is harder to fix downstream.

### Step 6 — Failure Modes and Reversibility

Present the 2-3 highest-consequence failure modes from Step 3. Focus on **irreversible or silently-broken** scenarios only. For each, get a human decision on how to handle it.

Additionally, if applicable (skip if not):
- **Data/state migration**: if change touches persisted data or schemas, ask about migration/backfill/coexistence
- **Rollback story**: if change involves migrations or breaking interface changes, ask about safe revert

Record answers in brainstorm.md. Unresolved items → `[TBD]`.

---

## Phase 4: Write brainstorm.md

Write `.claude/features/{slug}/brainstorm.md` using the [brainstorm.md template](references/templates.md#brainstormmd).

**Hard rules:** The brainstorm.md must be under 200 lines. Only include confirmed decisions (unresolved → `[TBD]`). Mark unconfirmed tests as `[unverified]`. Every file:line reference must be verified on disk. Do not include implementation details (code goes in plan.md).

Show the user the full brainstorm.md content inline in chat for review. If the user requests corrections, apply them to the file and show only the changed sections. On approval, set Status to `Approved`, update Date, and say:
> "Clear your context and run `/tpe:plan .claude/features/{slug}`."
