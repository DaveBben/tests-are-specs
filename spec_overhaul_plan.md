# Spec Format Overhaul — Working Plan

**Status:** drafting — iterating with David (started 2026-06-19)
**Goal:** redesign the slice-spec format so it is

1. **Deterministically lintable** by a program (structure + cross-references checkable).
2. **Readable** by a human reviewer (the team code-reviews specs).
3. **Self-contained** — survives without CLAUDE.md (the spec is its own artifact).
4. **Right-sized** — a 3-line change should not need a 200-line spec.

This doc is the living scratchpad. It evolves as we answer the open questions below.

---

## Design tensions we are resolving

- Machine-checkable structure **vs** human readability.
- Self-contained spec **vs** DRY (shared standards / constitution file).
- Enough `Approach` detail to steer the model **vs** over-constraining it.
- Thoroughness **vs** proportionality (small change ≠ heavy spec).

---

## Research findings — the eight levers (from 2026-06-19 research)

| # | Lever | Source | How it could apply here |
|---|-------|--------|-------------------------|
| 1 | **Structure beats prose** — a schema makes gaps visible; ambiguous prose hides them | Stefan van Egmond; Addy Osmani | Split each spec into a human-narrative layer (Why/Summary) and a machine-checkable contract layer (typed fields a linter can parse) |
| 2 | **Six areas a spec must cover** — commands, testing, project structure, code style, git workflow, boundaries | Addy Osmani (2,500-config study) | Fold the CLAUDE.md essentials into the spec (or a referenced standards file) so the spec stands alone |
| 3 | **Boundaries as three tiers** — ✅ always / ⚠️ ask-first / 🚫 never | Addy Osmani | Replace or augment flat `Constraints` with the three-tier form |
| 4 | **Concrete examples beat description** — one real example > 3 paragraphs | Addy Osmani | Gold input→output example in prompts; a code-style snippet; sample records |
| 5 | **Living artifact / anti-drift** — update the spec when reality changes | Red Hat; Addy | Already done via code-reviewed specs + the docs-cutover slice |
| 6 | **Alignment before speed** — interrogate the human before coding | "Grill Me" skill; Deep Discovery | create-spec asks a fixed set of questions (David leans ~8, not 40) |
| 7 | **Context hygiene** — small tasks, name the files, avoid the "dumb zone" | RPI talk; 990k-LOC guide | Add an ordered task checklist inside the slice |
| 8 | **Data model / types first** — pin types & contracts precisely, let procedural code be loose | 990k-LOC guide | A dedicated, cleanly-laid-out data-model/contracts section |

---

## David's reactions (captured verbatim-ish)

1. **Structure** — wants deterministic linting eventually, balanced for a human. Summary + Why are the loved sections. `Approach`, `Files that matter`, and **especially `Verification`** get hard to read.
2. **Six areas** — likes it; wants the CLAUDE.md content living *in* the spec so the spec is self-contained.
3. **Boundaries** — has `Constraints`; the always/ask-first/never split may be better.
4. **Examples** — interesting; unsure how to implement.
5. **Living artifact** — already code-reviews specs. ✅
6. **Alignment** — create-spec attempts it; wants it to always ask ~8 questions (40 too many).
7. **Context hygiene** — needs to improve; maybe list tasks in the spec file.
8. **Data types/models** — needs a clean dedicated layout.

---

## Open questions — resolved (see chat for full reasoning)

- **"Is `Files that matter` really needed?"** → **Keep it, reframe it.** The `[context]` entries are the token-saver (agent reads `classifier.py:201` instead of grepping). It is also the best hook for the linter (diff must touch exactly `[new]`+`[modify]`). Fix the staleness cost by leading with **symbol names**, line numbers second.
- **"How much in `Approach`?"** → **Only the non-obvious path.** Specify seams, ordering rules, which pattern to mirror, what NOT to touch, and gotchas. Cut any sentence the model would already satisfy on its own. Push precision toward types/contracts; let procedural code stay loose.
- **"How to split tasks?"** → **Two levels.** Feature→slices (keep `_index.md`, it is strong) at single-concern / CI-green / ≤~4-file boundaries. Slice→tasks as an ordered checklist (types → tests/contracts → impl → wire → cleanup), with `[P]` parallel markers.

---

## Decisions log (filled as we go)

> Refinements: Assumptions = parseable table (claim | if_wrong | confidence); Alternatives-rejected = prose. So "Decisions" in the canonical order splits into "Alternatives rejected" then "Assumptions (table)".


| Topic | Decision | Status |
|-------|----------|--------|
| Two-layer doc (narrative + machine contract) | YES — narrative (Why/Summary/Context) on top; machine contract below; linter parses only the contract | decided |
| Contract format | Hybrid — prose sections; file manifest / tasks / verification as parseable tables with stable IDs | decided |
| What the linter enforces | Structure & required fields; content guardrails; manifest-matches-diff; **symbol-resolution (added after round-1 review)**. (Still NOT full cross-reference integrity) | decided |
| Self-contained vs referenced standards file | One repo-level constitution (standards.md): six-areas + boundaries + invariants. Specs reference it; CLAUDE.md shrinks to a pointer. **Amended (round-2): each slice also inlines a SHORT slice-relevant excerpt — Principles + boundary tiers — so it stands alone for review. standards.md stays the source of truth. Amended (round-3): the constitution file may be `standards.md`, `CLAUDE.md`, or `AGENTS.md` — the `standards:` frontmatter names whichever the repo uses, ONE canonical form, referenced identically in prose (linter checks consistency).** | decided |
| Boundaries: three-tier vs constraints | Split — per-slice Constraints = flat hard MUSTs (linted); always/ask/never three-tier lives in shared Standards. **Amended (round-2): each slice ALSO carries a short slice-relevant three-tier Boundaries block (✅/⚠️/🚫); it absorbs the old Approach "Don't-touch". standards.md holds the project-wide defaults.** | decided |
| Examples: where/which | Worked verification case (one EARS assertion with real expected values) + one code-style snippet in standards.md. NOT prompt/data examples. | decided |
| Alignment questions: fixed 8 vs adaptive | Adaptive up to 8 — drafter picks the highest-uncertainty questions per task. Coverage varies by design. | decided |
| Per-slice task checklist format | Task table with status: id | task | files | [P] | done. Agent flips done; resumable. | decided |
| Files manifest | One table, mode column (new/modify/context), symbol-first, line optional. Diff-lint only new/modify. | decided |
| Data-model section format | Typed signature blocks (fenced Pydantic/type sketch + SQL DDL) as the source of truth | decided |
| Verification format (the big readability pain) | EARS assertions (WHEN/THE SYSTEM SHALL) with stable IDs + commands block + seams list. Maps to property-based tests. | decided |
| Feature-level success metric / DoD | DoD checklist in _index.md (qualitative). **Amended (round-3): each slice ALSO carries a `Success metric` section — the measurable outcome it enables (N/A — reason allowed for pure refactors). Reverses the earlier "no slice metric".** | decided |
| Clarifications (preserve interrogation) | NEW (round-3): each slice records the drafting grill — `question | resolution | status` — so alignment is visible, not laundered. Open items link to an OPEN assumption / [NEEDS CLARIFICATION]. | decided |
| Rollback & Ops section | None — rely on dead-code-then-delete split, abort-loud, no-DELETE role. Not a template section. | decided |
| Spec sizing / tiered templates | One full template always (no tiers). Consistency > proportionality. N/A sections marked "N/A — reason", not omitted. | decided |
| Approach format | Fixed micro-schema: Mirror / Don't-touch / Ordering / Gotchas. Lean by construction. | decided |
| Frontmatter/telemetry | Keep telemetry inline; add schema_version + status enum (linter reads them). | decided |
| Status lifecycle enum | Draft → Reviewed → Implemented → Superseded | decided |
| Canonical section order | Why, Summary, **Success metric**, Context, Principles, Data model, Alternatives, Assumptions, **Clarifications**, Boundaries (tiered), Constraints, Approach, Edge cases, Files, Tasks, Verification (+ Self-check). Updated round-3. | decided |
| Assumptions structure | Parseable table (claim \| if_wrong \| confidence); Alternatives-rejected stay prose | decided |
| Rollout / migration | v3 for NEW specs only; v2 specs frozen, never backfilled; linter runs only on schema_version v3 | decided |

---

## Proposed new spec skeleton (draft v0 — WILL change via Q&A)

```
── Frontmatter (machine) ──
name, status, depends_on, telemetry, file-manifest?

── Layer 1: Narrative (human-reviewed) ──
Why            — intent, conclusion-first
Summary        — what ships
Context        — current behavior (optional)

── Layer 2: Contract (machine-checkable) ──
Data model & contracts   — types, table shapes (elevated)
Decisions                — alternatives rejected + assumptions (If wrong → …)
Boundaries               — ✅ always / ⚠️ ask-first / 🚫 never
Approach                 — non-obvious path only
Tasks                    — ordered checklist, [P] markers
Verification             — structured given/when/then + commands
Standards                — six-areas, embedded or referenced
```

> ⚠️ The v0 skeleton above is SUPERSEDED by the Final Design below.

---

## FINAL DESIGN (v3 — all 20 questions answered, 2026-06-20)

### Three artifacts
1. **`standards.md`** (repo-level constitution) — written once, referenced by every spec.
2. **`_index.md`** (per-feature rollup) — Why, Summary, dependency-ordered slice table, Ordering notes, **Definition-of-Done checklist**.
3. **Slice spec** (per slice) — the two-layer document below.

### Slice spec — two layers, one full template always

```
─── FRONTMATTER (machine) ───
schema_version: v3
name: <slug>
status: Draft | Reviewed | Implemented | Superseded
depends_on: [...]
execution:                      # telemetry kept inline
  total_cost / total_duration / usage_by_models[]

standards: standards.md         # the constitution file — ONE of: standards.md | CLAUDE.md | AGENTS.md (same form everywhere)

─── LAYER 1 · NARRATIVE (prose · human-reviewed) ───
1. Why            intent, conclusion-first  (outcome-only; keep transport/HOW in the contract)
2. Summary        what ships  (linted: word cap)
3. Success metric measurable outcome it enables (N/A — reason allowed)        (round-3)
4. Context        current behavior  (N/A — reason, if none)

─── LAYER 2 · CONTRACT (parseable · linted) ───
5.  Principles (this slice)  short excerpt of the constitution invariants that gate THIS slice  (round-2)
6.  Data model & contracts   typed signature blocks (Pydantic/DDL) = source of truth
7.  Alternatives rejected    prose bullets
8.  Assumptions              TABLE: claim | if_wrong | confidence | verify   (med/low conf → OPEN / [NEEDS CLARIFICATION])
9.  Clarifications           TABLE: drafting interrogation preserved — question | resolution | status  (round-3)
10. Boundaries (this slice)  THREE tiers ✅ always / ⚠️ ask-first / 🚫 never  (slice-relevant; absorbs old "Don't-touch")  (round-2)
11. Constraints              flat hard MUSTs
12. Approach                 micro-schema: Mirror / Ordering / Gotchas
13. Edge cases               bullets
14. Files                    TABLE: id | path | mode(new|modify|context) | symbol | why   (manifest)
15. Tasks                    TABLE: id | task | files | [P] | done
16. Verification             EARS assertions (ATOMIC — no bundled ANDs) w/ IDs
                             + one WORKED case + commands + seams + Self-check (re-walk every V)  (round-2)
```

### `standards.md` — the constitution (six-areas + boundaries + invariants)
```
Commands           exact invocations w/ flags
Testing            frameworks, layout, how to run
Project structure  where code lives
Code style         + ONE real snippet (the example)
Git workflow       branch/commit/PR rules
Boundaries         ✅ always / ⚠️ ask-first / 🚫 never   (agent permissions)
Invariants         fail-open · never-silently-drop · bias-to-recall
```
CLAUDE.md shrinks to a pointer at `standards.md`.

### Linter (runs only on `schema_version: v3`)
- **Structure & order** — required sections present, in canonical order; tables have mandatory columns.
- **Content guardrails** — Summary ≤ word cap; no `[NEEDS CLARIFICATION]` (in Reviewed/Implemented status); every Assumptions row has `if_wrong`; every error-path EARS case tagged; any N/A section carries a reason. **Added round-2:** flag untestable shalls (`optionally SHALL`, no threshold); flag EARS rows that bundle multiple `AND` assertions (split them); med/low-confidence assumptions must carry a `[NEEDS CLARIFICATION]` or a verify-plan.
- **Manifest ↔ diff** — `git diff` files == Files rows with mode new/modify (no stray edits, no listed-but-untouched).
- **Symbol-resolution** *(added after round-1 review)* — every `symbol` in the Files table must resolve in the codebase (the referenced file exists; the symbol is found in it). Cheap; catches the drift class that sank round 1.
- **Standards reference** *(round-3)* — `standards:` frontmatter names exactly one of `standards.md` / `CLAUDE.md` / `AGENTS.md`, and every in-prose mention uses the SAME form (kills the path-format self-contradiction round-3 caught).
- NOT enforced: full cross-reference integrity (tasks↔verification↔boundaries graph) — still too fragile.

### create-spec
- Adaptive grilling **before** drafting: up to 8 highest-uncertainty questions, chosen per task (no fixed list).

### Rollout
- v3 for **new specs only**. v2 specs frozen, never backfilled. `schema_version` gates the linter.

---

## Round-1 review lessons (blind Opus review of the v3 embedder example)

A blind, strict Opus reviewer (research as rubric) scored the v3 example **6.5/10**.
The format's pieces were named as **strengths** — right-sizing, EARS↔tests 1:1, the
anti-tautology Seams section, the gotcha injection, types-first, CancelledError rule.
Nearly every deduction was **drift**, not format. Key takeaways:

- **Drift is the killer, and the originally-scoped linter would NOT catch it.** A wrong
  constant name and a deleted-file `[context]` ref both pass structure + content +
  manifest-vs-diff. → Added the **symbol-resolution** lint check (above).
- **`classifier.py` reference is genuinely stale** — slice 5 deleted it; the live pattern
  is `summarizer.py`. A once-correct `[context]` pointer rotted post-implementation. Real
  illustration of why anti-drift tooling matters.
- **Substantive, format-relevant gaps (apply to the original too):**
  - Fail-open logging is under-specified — "one warning" with no pinned **event name** or
    **correlation key** (`guid`). In a fail-open design logs are the only safety signal.
    → Consider: should the format require log-event contracts? Add to `standards.md` and/or
    a Verification expectation.
  - Untestable "shall" statements slip through — e.g. `"not configurable"`, `"log when the
    summary looks long"` (no defined heuristic). → Content-guardrail lint could flag
    assertions with no matching criterion.
  - Type/contract mismatch — `embed()` typed `str` while the Files row claims `SafeStr` at an
    untrusted boundary. → A research-grade spec should keep the signature and the cited type
    consistent.
- **Two "blocker" findings (EMBED_DIM naming, /v1/v1 doubling) were translation artifacts** of
  the hand-rewrite, not the original or the format. Discounted.

## Symbol-resolution lint — design sketch
```
For each row in the Files table:
  - resolve `path` → file must exist (skip mode=new, which shouldn't exist yet;
    INVERT for new: assert it does NOT exist pre-implementation)
  - for mode in {modify, context}: file MUST exist
  - if `symbol` is non-empty: grep the symbol as a definition/usage in `path`;
    MUST find ≥1 hit (def for the owning file; usage allowed for context)
  - line anchors (`:NNN`) are advisory only — never failed on (they drift); the
    symbol is the durable anchor (matches the earlier "symbol-first" decision)
Runs only on schema_version: v3. Pairs with manifest-vs-diff.
```

## Round-2 review lessons (blind Opus review — spec-vs-research ONLY, no codebase)

A second blind Opus reviewer, scoped strictly to research-vs-spec (forbidden from
touching the codebase), also scored the v3 example **6.5/10**. Scorecard: **6 FULLY
embodied, 2 VIOLATED, 8 PARTIAL**.

- **FULLY:** examples (G), context hygiene (J), types-first (K), decomposition (M),
  verification rigor (N), right-sizing (O) — the engineering-rigor cluster.
- **VIOLATED:** three-tier boundaries (F), internal consistency (P).
- **PARTIAL:** why/metrics (A), EARS completeness (B), constitution-shown (C),
  anti-drift rule (D), six-areas (E), ambiguity honesty (H), self-verification (I),
  alignment-visible (L).

**Key insight:** F, C, and E(git/style) failed mainly because they live in
`standards.md` by the DRY decision — the reviewer judged the slice *in isolation*.
That is the self-contained-vs-DRY bill, exactly as predicted.

**Decision (round-2): inline short, slice-relevant Principles + three-tier Boundaries
in each slice.** `standards.md` stays the full constitution (source of truth); each
slice excerpts the principles that gate it and the ✅/⚠️/🚫 that apply to it. The slice
now stands alone for review; the DRY master is preserved.

**Real, actionable findings (independent of standards.md):**
- **P (lethal):** base-URL self-contradiction — `ai-server:8080` (curl) vs
  `ai-server.local:8080/v1` (config); V7 asserts `== chat base URL`, never stated.
  Fix: one canonical literal everywhere. *(This class is value-level — the linter
  won't catch it; human review must.)*
- **B:** V7 bundles 4 assertions → split into atomic EARS; the "optionally SHALL log
  when long" has no threshold → define or delete.
- **H/L (assumption-laundering):** "accepted by David" / "high (David)" present open
  questions as settled. The med-confidence truncation assumption is a real open
  question dressed as a decision. Separate **"David decided X"** (a decision) from
  **"we assume X"** (a risk); med/low confidence must surface as `[NEEDS CLARIFICATION]`
  or a verify-plan.
- **I:** no self-verification step — add a **Self-check** to Verification (re-walk every
  V; confirm each Constraint met).
- **A:** "Why" collapses into "how" ("adds the client; slice 4 calls it"); keep it
  outcome-oriented. (Feature-level success metric stays a `_index.md` DoD per Q13.)

**Format changes adopted from round-2** (now reflected in the Final Design above):
1. New per-slice sections **Principles (this slice)** and **Boundaries (tiered)**;
   Approach drops "Don't-touch" (→ Boundaries 🚫), leaving Mirror / Ordering / Gotchas.
2. **Self-check** subsection added to Verification.
3. Content-guardrail lint extended (untestable shalls, bundled EARS, low-confidence
   assumptions must carry a clarification/verify-plan).

**Two reviews triangulated:** strong on engineering rigor; weak on (1) drift-resistance
→ fixed by the symbol-resolution lint, and (2) documentary discipline → fixed by the
round-2 additions above.

## Round-3 review lessons (re-review of v3.1) + David's directives

A fresh blind Opus reviewer (same rubric, no codebase) scored v3.1 **7.5/10**, up from
6.5. Both round-2 VIOLATIONS resolved: F (three-tier boundaries) → FULLY embodied; P
(internal consistency) shrank to a trivial path-format nit. Scorecard moved to **9 FULL
/ 6 PARTIAL / 1 VIOLATED**. New-FULL: C (constitution), F (boundaries), I (self-check).

**Ceiling insight:** a slice that delegates to the constitution tops out ~8/10 on an
*isolation* review — Git workflow (E) and (until round-3) the metric (A) live outside the
slice by design. The missing points were intentional tradeoffs.

**David's round-3 directives (now decided above):**
1. **Add a Success metric to each slice** (A) — reverses the earlier "no slice metric".
   Measurable outcome the slice enables; N/A-with-reason for pure refactors.
2. **Preserve the interrogation** (H/L) — a `Clarifications` table records the drafting
   grill (question | resolution | status), so alignment is visible, not laundered.
3. **Constitution reference** — point to one of `standards.md` / `CLAUDE.md` / `AGENTS.md`,
   one canonical form, consistent everywhere (fixes P; linter checks it).

**Also folded in (cheap fixes from the review):** assert log `kind` fields in the EARS that
pin them (B); a one-line anti-drift rule (D); an explicit Git-workflow pointer to the
constitution (E); keep the narrative layer transport-agnostic (A).

## Round-3.2 re-review (v3.2) + the LLM-judge noise lesson

Third blind Opus reviewer (same rubric) scored v3.2 **7.5/10** — *same integer* as v3.1,
but fullness improved: **10 FULL / 5 PARTIAL / 1 VIOLATED** (was 9/6/1). The three
directives all landed as fully embodied: H, L, D.

**Why the integer plateaued — two separate reasons:**
1. **Reviewer noise (~±1 pt).** M (decomposition) and O (right-sizing) were FULL in round-3
   and PARTIAL here, with **no change to those parts of the spec**. Two Opus reviewers
   weight identical text differently. → **Track the scorecard shape, not the integer.**
   Stable-FULL across runs: B, F, G, H, I, J, K, L, N, D (the engineering + alignment core).
   Perennially contested: A, C, E (the delegation tradeoff). O is the reviewer disliking the
   inline-telemetry decision (Q15) — dismissable.
2. **Two real new nits (both author-introduced, both cheap):**
   - **Worked example contradicted its own seam.** V2 built the mock as `range(768)`, but
     seam S1 forbids deriving the mock length from `EMBEDDING_DIM`. A value-level
     self-contradiction **no structural lint caught** — the standing case for human review +
     consistency checks, and a textbook example of why P is "lethal".
   - **Identifier drift:** `embeddinggemma` vs `embeddinggemma-300m`. One model, two strings.

**Template rules baked in from this round:**
- Worked examples MUST NOT source their mock dimensions/length from the constant under test
  (else they violate the anti-tautology seam). Consistency-lint candidate.
- Unify identifiers (one model-name string, one URL form) — consistency-lint candidate.

**Conclusion:** the format is **proven**. Three rounds (6.5 → 7.5 → 7.5; FULL 6 → 9 → 10)
hit the isolation-review ceiling (~8) plus the judge noise floor. Stop grinding the example;
build the real artifacts. The contested A/C/E partials are intentional DRY/telemetry tradeoffs,
confirmed three times.

## What to build next (proposed)
1. `standards.md` — extract the six-areas + invariants from CLAUDE.md; add the code-style snippet; repoint CLAUDE.md.
2. `spec-template-v3.md` — the empty slice template above, with section stubs + an EARS/worked-case example.
3. `_index` template — with the DoD checklist.
4. The linter — a small script (structure + guardrails + manifest-vs-diff), wired into pre-commit / CI.
5. Update `create-spec` / `create-feature` commands — adaptive grilling + emit v3.
6. (Optional) Author one real new spec in v3 to validate the format end-to-end.

```
