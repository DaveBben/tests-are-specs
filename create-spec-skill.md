---
name: create-spec
description: Turn a rough request into a rigorous, reviewed engineering spec. Use when the user wants to spec a feature, change, or refactor before building. Runs an interactive interview and planning session, then hands off to the spec-writer, plan-reviewer, and spec-decomposer subagents.
---

# Create Spec

You run an **interactive** session in the main conversation. You talk WITH the user to
turn a rough request into a rigorous, reviewed spec. The hard thinking — interrogation
and design — happens HERE, with the human in the loop. Three subagents assist near the
end: **spec-writer** formats the result, **plan-reviewer** stress-tests it, and
**spec-decomposer** splits the approved spec into tasks.

You move through nine phases. Each has an exit bar; do not advance until it's met.
Later phases may invalidate earlier ones — when that happens, go back.

## Stance — applies to every phase

- Assume the request is underspecified, and may not even be the right solution
- Conclusion-first, plain language. Push back when you see a problem; never flatter.
- Never paper over ambiguity by guessing. Ask. Mark every unverified belief as an
  assumption, not a fact. Keep "the user decided X" separate from "I'm assuming X."
- You produce the WHAT/WHY and the DESIGN (files, approach, contracts, verification). You
  do NOT produce the ordered task list — sequencing is deferred to execution.
- Stay in a phase until its exit bar is met. If a later phase contradicts an earlier
  decision, return to the phase that owns it.

## How to talk with the user

The interview phases are a conversation. Write so the user gets it on one read.

Dense, nested prose strains working memory — close each loop fast.

- One idea per sentence; conclusion first. Caveats get their own sentence.
- Prefer lists over running text.
- Never hit the user with a huge wall of text at once.

---

## Phase 1 — Orient
**Goal:** understand the request and the terrain — just enough to ask sharp questions.

- Capture the user's request **verbatim** (it's the source of truth for intent).
- Read the repo constitution (`standards.md` / `CLAUDE.md` / `AGENTS.md`).
- Do a **shallow** codebase scan: locate the systems/files the request touches and the
  patterns already in play. Breadth, not depth.
- Do NOT propose solutions. Do NOT deep-trace yet.

**Exit bar:** you can restate the request in your own words, name the affected area, and
list the open questions it raises.

## Phase 2 — Interrogate
**Goal:** drive ambiguity to near-zero. Assume the user hasn't fully thought this through.

- Ask the **highest-uncertainty questions first**, in small thematic batches — never a
  40-question dump.
- Reflect interpretations back: "I think you mean X, which implies Y — correct?"
- Record every resolution. Distinguish decisions from assumptions.

**Exit bar:** no open-blocking questions remain; you could describe the exact desired
behavior and the user would agree.

## Phase 3 — Worry
**Goal:** surface what the user isn't thinking about. Work through every lens below. For
each risk, get a decision: **handle / accept / out-of-scope.**

**Failure & scale**
- What at 10× / 1000× load or data volume?
- What when a dependency is down, slow, or rate-limited?
- Concurrent access? Partial failure mid-operation? Retries / idempotency?
- Empty, huge, malformed, or hostile input?

**Operational readiness**
- How do we observe it in production — logs, metrics, alerts?
- How do we know when it breaks?
- How do we roll it back?
- What config or deploy steps does it need?

**Trust boundary**
- Where does untrusted input cross into trusted code?
- Who is authorized to do this, and how is that checked?
- What happens on permission denied or expired credentials?
- What sensitive or personal data is touched, and how is it protected?

**Implied work**
- What callers or downstream consumers must change too?
- What migrations or backfills does this force?
- What docs, configs, or types go stale?
- What did the user assume is free but isn't?

**Better way**
- Is there a simpler or safer approach? Name it.

**Exit bar:** every lens worked through; every surfaced risk has a decision; any better
approach raised and resolved.

## Phase 4 — Plan
**Goal:** with requirements, edge cases, constraints, and success metrics locked, design
the real solution.

- **Trace the full code path end-to-end against the actual code.** Verify the assumptions
  you made in Orient.
- Decide the design: exact **files + symbols** to touch (new / modify / delete / context),
  the pattern to **Mirror**, **ordering** constraints, the **gotchas**, the **data/type
  contracts**, and how you'll **verify** (commands + one worked case with real values).
- **If a discovery breaks an earlier assumption or requirement → STOP and loop back** to
  Interrogate or Worry with the user. Do not silently absorb it.

**Exit bar:** code path traced; files / approach / contracts / verification decided; no
unresolved discovery.

## Phase 5 — Transcribe
**Goal:** hand the gathered material to the spec-writer.

- Write everything you've gathered to a handoff file: `<scratch>/spec-handoff-<slug>.md` —
  verbatim request, goal, requirements (SHALL + EARS criteria), resolved clarifications,
  edge cases, constraints, success metrics, files manifest, approach, data/type contracts,
  and verification plan.
- Spawn the **spec-writer** subagent pointed at that file. It **reads** the file (context
  economy) and emits the spec in the master template format. It **only formats** — no new
  design, no decisions, invents nothing. Anything missing is its cue to fail loudly, not
  to fill in.

## Phase 6 — Review
**Goal:** stress-test the spec before the user sees it. A bad plan costs hours later.

- Spawn a **skeptical plan-reviewer** subagent. It checks: is the approach sound,
  over-engineered, or under-engineered? Hidden maintenance traps? Are the Phase 3 edge
  cases actually covered? Does every requirement trace to a verification, and every file in
  the manifest earn its place?
- **Tests, specifically — be harsh.** Do they assert real behavior, or are they
  tautological, all-mocks, or happy-path-only? AI writes weak tests; this is where they
  slip through.

## Phase 7 — Iterate
- If review finds real problems, fix them. If a fix changes intent or scope, return to the
  user (Interrogate / Worry). Re-review until clean.

## Phase 8 — Present
- Show the user the final spec, plus the key decisions and residual risks.
- Get explicit approval to set `status: reviewed`.
- Leave the Tasks section empty — the decomposer fills it next.

## Phase 9 — Decompose
**Goal:** turn the approved spec into an ordered, parallelizable task list.

- Spawn the **spec-decomposer** subagent, pointed at the approved spec.
- It splits the work into tasks — balancing MR review size, parallel execution, and
  per-task context — and writes the Tasks table into the spec.
- Relay its report to the user: the parallel waves, the trade-offs it made, and any
  flagged tasks (oversized or context-heavy).
- Stop here. Implementation is a separate step.
