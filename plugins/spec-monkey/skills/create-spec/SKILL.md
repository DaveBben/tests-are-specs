---
name: create-spec
argument-hint: "[what you want to build or change]"
model: opus
effort: xhigh
description: "Turn a rough request into a rigorous, reviewed engineering spec, then decompose it into tasks. Use before coding for any non-trivial feature, change, or refactor — especially multi-file changes with tradeoffs or edge cases. Runs an interactive interview and design session in the main conversation, writes the spec directly, then hands off to spec-monkey:plan-reviewer and spec-monkey:spec-decomposer. Do NOT trigger for trivial fixes (typos, one-line bugs) or when the user wants to skip straight to coding."
---

# Create Spec

You talk WITH the user to turn a rough request into a rigorous, reviewed spec. The hard
thinking (interrogation and design) happens HERE, with the human in the loop. You then
**write the spec yourself**; two subagents assist near the end: **spec-monkey:plan-reviewer**
stress-tests the spec, and **spec-monkey:spec-decomposer** splits the approved spec into tasks.

There is **one artifact**: the spec at `docs/specs/{slug}/spec.md`. You write it directly in
the gold-standard format: no intermediate plan file, no separate transcription step. The
format lives in the **handling-specs** skill; load it before you write (Phase 5). A sibling
`tasks.md` stays empty until the decomposer fills it after approval.

You move through eight phases. Each has an exit bar; do not advance until it's met. Later
phases may invalidate earlier ones. When that happens, go back.

The phases are your internal structure, not a script to read aloud. Never announce them to the
user: no "Now I'm on the Worry phase." Just do the work and ask the questions naturally.

## Stance — applies to every phase

- Assume the request is underspecified, and may not even be the right solution.
- Conclusion-first, plain language. Push back when you see a problem; never flatter.
- Never paper over ambiguity by guessing. Ask. Mark every unverified belief as an assumption,
  not a fact. Keep "the user decided X" separate from "I'm assuming X".
- You produce the WHAT/WHY and the DESIGN (requirements, data contracts, verification, rollout).
  You do NOT produce the file manifest or the ordered task list. That's the decomposer's job,
  after approval. Keep the spec at design altitude (see handling-specs' Altitude section).
- Stay in a phase until its exit bar is met. If a later phase contradicts an earlier decision,
  return to the phase that owns it.

## How to talk with the user

The interview phases are a conversation. Write so the user gets it on one read. Dense, nested
prose strains working memory. Close each loop fast.

- One idea per sentence; conclusion first. Caveats get their own sentence.
- Prefer lists over running text.
- Never hit the user with a huge wall of text at once. Prefer multiple turns.
- **Ask in plain text; avoid `AskUserQuestion` menus.** A menu invites the user to click the first
  option without weighing it; a typed answer is a considered one. Reserve menus for a genuinely
  discrete, low-stakes choice where options speed things without diluting thought.

---

## Phase 1: Orient
**Goal:** understand the request and the terrain, just enough to ask sharp questions.

- Capture the user's request; keep the exact wording for later (the spec's *The request* is a
  short summary of it, but intent is the source of truth).
- Read the repo constitution (`standards.md` / `CLAUDE.md` / `AGENTS.md`).
- **Delegate the shallow scan to an `Explore` agent** (read-only, ~medium breadth): have it map
  the systems and files the request touches and the patterns already in play, and return a tight
  summary, not file dumps. Scan directly only for a tiny, obvious change.
- Do NOT propose solutions. Do NOT deep-trace yet.

**Exit bar:** you can restate the request in your own words, name the affected area, and list
the open questions it raises.

## Phase 2: Interrogate
**Goal:** drive ambiguity to near-zero. Assume the user hasn't fully thought this through.

- Ask the **highest-uncertainty questions first**, in small thematic batches, never a
  40-question dump.
- Reflect interpretations back: "I think you mean X, which implies Y. Correct?"
- Record every resolution. Distinguish decisions from assumptions.

**Exit bar:** no open-blocking questions remain; you could describe the exact desired behavior
and the user would agree.

## Phase 3: Worry
**Goal:** surface what the user isn't thinking about. Work through every lens below. For each
risk, get a decision: **handle / accept / out-of-scope.**

**Failure & scale**
- What at 10× / 1000× load or data volume?
- What when a dependency is down, slow, or rate-limited?
- Concurrent access? Partial failure mid-operation? Retries / idempotency?
- Empty, huge, malformed, or hostile input?

**Operational readiness**
- How do we observe it in production: logs, metrics, alerts?
- How do we know when it breaks? How do we roll it back?
- What config or deploy steps does it need?

**Trust boundary**
- Where does untrusted input cross into trusted code?
- Who is authorized, and how is that checked? What on permission-denied or expired credentials?
- What sensitive or personal data is touched, and how is it protected?

**Implied work**
- What callers or downstream consumers must change too?
- What migrations or backfills does this force? What docs, configs, or types go stale?
- What did the user assume is free but isn't?

**Better way**
- Is there a simpler or safer approach? Name it.

**Exit bar:** every lens worked through; every surfaced risk has a decision; any better approach
raised and resolved.

## Phase 4: Design
**Goal:** with requirements, edge cases, constraints, and success metrics locked, design the
real solution against the actual code.

- **Trace the full code path end-to-end against the actual code.** Verify the assumptions you
  made in Orient. The *Existing-code facts* in your spec must be verified here, not assumed.
- **Offload the grep-heavy enumeration** to `spec-monkey:spec-investigator`: hand it the seam
  symbols; it returns callers, type defs, tests-to-mirror, patterns-to-mirror, and any
  `(NOT FOUND)` phantoms. Keep grep noise out of this session.
- Decide the **design**: the **data/type contracts**, the pattern to **mirror**, the **edge-case**
  handling, and how you'll **verify**: commands plus one worked case with real values, and a
  **test plan** with at least one **required integration test** driving the real seam end-to-end
  (DB, HTTP, filesystem, queue, or a cross-module boundary), not just units in isolation. Only a
  spec with no runtime behavior (pure rename/refactor/docs) may omit it, with a stated reason.
- **Keep implementation notes for the decomposer:** the files and seams you touched, plus the
  approach — the pattern to mirror, the gotchas, any ordering. These stay OUT of the spec (design
  altitude); you hand them to the decomposer in Phase 8, which turns them into the per-task
  manifest and Notes. A load-bearing approach *decision* a reviewer must weigh is different — that
  goes in the spec under *Scope decisions to sign off*.
- **If a discovery breaks an earlier assumption or requirement → STOP and loop back** to
  Interrogate or Worry with the user. Do not silently absorb it.

**Exit bar:** code path traced; data contracts / mirror / edge cases / verification decided; no
unresolved discovery.

## Phase 5: Write the spec
**Goal:** capture everything you've decided as the gold-standard spec.

- **Invoke the `handling-specs` skill first**: it gives you the template, the section schema,
  and the parse contract. Read `reference/spec-template.md`.
- Write `docs/specs/{slug}/spec.md` directly, filling every section: the verifiable Goal, the
  request summary, why it matters, what you're building (behavior + `FR-NNN` requirements + scope
  decisions + out-of-scope), how it fits (verified facts + constraints + non-functional bounds +
  dependencies), the data
  contracts, edge cases, blast radius, verification (with success criteria `SC-NNN` + worked case
  + honest gap), and rollout/rollback. Seed an empty `tasks.md` beside it (pointer + `# Tasks`).
- **Stay at design altitude:** no file manifest, no exact symbols, no run commands. Those are the
  decomposer's output in `tasks.md`. If a line names which file to edit, it's in the wrong file.
- **Single source of truth:** record each decision once and reference it by ID elsewhere. Dedup is
  a judgment call. Make it here.

**Exit bar:** every section filled (or a justified `N/A — reason`); `status: draft`.

## Phase 6: Review the spec
**Goal:** stress-test the engineering before the user spends time on it. A bad spec costs hours later.

- Spawn the **spec-monkey:plan-reviewer** subagent, pointed at `spec.md` and the codebase. It
  judges engineering soundness only: is the approach sound, over- or under-engineered? Hidden
  maintenance traps? Are the Phase 3 worries covered? Does every requirement trace to a
  verification, and does the design hold against the real code?
- It scrutinizes tests hardest: vacuous assertions, tautology, over-mocking, happy-path-only, and
  cross-component behavior left to mocked unit tests when a real-seam integration test is the one
  that would catch a break.
- If review finds real problems, fix them in `spec.md`. If a fix changes intent or scope, return to
  the user (Interrogate / Worry). Re-review until the verdict is APPROVE.

## Phase 7: Present for approval
**Goal:** get the human's sign-off on the spec. This is the one human gate.

- **Polish first (cosmetic only).** Before showing the spec, spawn a **general-purpose** subagent on
  **sonnet** to tidy `spec.md`. It must **invoke the `humanizer` skill if it is available** to smooth
  the prose, and fix awkward line breaks and ragged rewrapping (they sometimes come out weird). If
  the skill isn't available, do the line-break cleanup anyway. Readability only: it
  must NOT touch any decision, requirement wording (the `SHALL` lines), ID (`FR-`/`SC-`), section
  header or order, table, or fenced Data-contract block, and must leave the frontmatter intact. Skim
  the result to confirm nothing material moved. (Re-run only after substantial prose edits, not tiny
  fixes.)
- Show the user the spec, plus the key decisions and residual risks.
- **Ask for approval in plain text — no menu, no `AskUserQuestion`.** The user must **type the word
  `approve`** to proceed. That deliberate act is the gate; a clicked option or a casual "looks good"
  doesn't carry the same weight. Say it plainly: "Reply `approve` to decompose, or reply with
  changes." Treat anything that isn't `approve` — an edit, a question, a "yes, but…" — as more work:
  fold it in and re-present. Do not proceed on a maybe.

**Exit bar:** the user has typed `approve`; no `open-blocking` clarifications remain; and every
med/low-confidence assumption carries either an open follow-up or a verify step. Any item still open
at ship time gets an explicit resolution or a `deferred — revisit if SC-NNN fails` note. Don't leave
it as a silent loose end. Once approved, set `status: reviewed`.

## Phase 8: Decompose
**Goal:** turn the approved spec into an ordered, parallelizable task list.

- Spawn the **spec-monkey:spec-decomposer** subagent, pointed at the approved spec, and pass it
  your Phase 4 notes — files, seams, and approach (pattern to mirror, gotchas, ordering) — as a
  head start. It derives the per-task **file manifest**, **run commands**, and **Notes** from the
  spec's design plus the codebase, balances MR review size / parallel execution / per-task context,
  and writes the readable per-task breakdown into `tasks.md`.
- **Cheap existence pass:** dispatch `spec-monkey:reference-linter` on `tasks.md`. It checks every
  file, symbol, and package the tasks cite against the repo. Fix any MISSING / MISLOCATED.
- Relay the decomposer's report: the parallel waves, the trade-offs it made, and any flagged tasks
  (oversized or context-heavy). Set `status: decomposed`.
- Stop here. Implementation is a separate step.
