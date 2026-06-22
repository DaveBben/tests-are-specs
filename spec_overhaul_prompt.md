# Opus build-prompt — execute the v3 spec-format overhaul

**How to use:** open a fresh Claude Opus (Claude Code) session *in the target repo*, make the
five `spec_overhaul_*` files from this directory available to it (copy them in, or point it
here), and paste everything below the line.

---

You are implementing a spec-driven-development format overhaul ("v3") in this repository. The
full design is already decided — your job is to BUILD the artifacts and tooling, not to
re-litigate the design. Work like a careful staff engineer: match the repo's existing
conventions, propose before any destructive change, and verify each artifact.

## Required reading (read all before starting)
- `spec_overhaul_plan.md` — the decisions of record. The "Decisions log" and "FINAL DESIGN"
  sections are authoritative. Read the round-1/2/3 lessons too.
- `spec_overhaul_research.md` — the A–P rubric and the evidence behind every decision.
- `spec_overhaul_example_embedder_v3.2.md` — the canonical worked example of the v3 slice
  format. Match this structure exactly.
- (v3.0/v3.1 examples show the evolution; reference only if helpful.)

## The v3 design (decisions of record — do not change without asking)
- **Two layers per slice spec.** Layer 1 NARRATIVE (prose, human-reviewed): Why, Summary,
  Success metric, Context. Layer 2 CONTRACT (parseable, linted): Principles, Data model &
  contracts, Alternatives rejected, Assumptions, Clarifications, Boundaries, Constraints,
  Approach, Edge cases, Files, Tasks, Verification. **16 sections, this canonical order.**
- **Section formats:**
  - *Success metric* — measurable outcome the slice enables; `N/A — reason` allowed for pure refactors.
  - *Principles* — short excerpt of the constitution invariants that gate THIS slice + an anti-drift line.
  - *Data model & contracts* — typed signature blocks (Pydantic/DDL) = the source of truth.
  - *Assumptions* — TABLE `claim | if_wrong | confidence | verify`; med/low confidence → marked OPEN / `[NEEDS CLARIFICATION]`.
  - *Clarifications* — TABLE `question | resolution | status`; preserves the drafting interrogation.
  - *Boundaries* — three tiers ✅ always / ⚠️ ask-first / 🚫 never, slice-relevant.
  - *Approach* — micro-schema: Mirror / Ordering / Gotchas (NOT pseudocode).
  - *Files* — TABLE `id | path | mode(new|modify|context) | symbol | why`; symbol-first.
  - *Tasks* — TABLE `id | task | files | [P] | done`.
  - *Verification* — EARS assertions (`WHEN … THE SYSTEM SHALL …`), ATOMIC (no bundled ANDs),
    error paths tagged `[error — required]`, one WORKED case, a commands block, a Seams list,
    and a Self-check (re-walk every assertion + Constraints + the Files manifest).
- **Frontmatter:** `schema_version: v3`, `name`, `status` (Draft → Reviewed → Implemented →
  Superseded), `depends_on`, `standards: <file>`, inline `execution` telemetry.
- **Feature rollup** `_index.md`: Why, Summary, dependency-ordered slice table, Ordering
  notes, a Definition-of-Done checklist.

## Build tasks (in order)
1. **`standards.md` (or `CLAUDE.md`/`AGENTS.md`) — the constitution.** Build it for THIS repo,
   grounded in the real code (read the lint config, a representative module's error-handling
   idiom, the existing CLAUDE.md/AGENTS.md). It must contain: Invariants, Commands, Testing,
   Project structure, Code style (+ ONE real snippet pulled from this repo), Git workflow,
   Boundaries (✅/⚠️/🚫). Then shrink the existing CLAUDE.md/AGENTS.md to a pointer at it
   (propose this change before editing the existing file).
2. **`spec-template-v3.md`** — the empty 16-section slice template with stubs and one inline
   example per table, matching `spec_overhaul_example_embedder_v3.2.md`.
3. **`_index` template** — the feature rollup with the DoD checklist.
4. **The linter** — a small script, wired into pre-commit + CI, runs only on
   `schema_version: v3`. It enforces:
   - structure & order (required sections, canonical order, mandatory table columns);
   - content guardrails (Summary word cap; no `[NEEDS CLARIFICATION]` in Reviewed/Implemented;
     every Assumptions row has `if_wrong`; every error-path EARS tagged; N/A sections carry a
     reason; flag untestable "optionally SHALL"; flag EARS rows bundling multiple ANDs;
     med/low-confidence assumptions carry a clarification/verify-plan);
   - manifest ↔ diff (changed files == Files rows with mode new/modify);
   - symbol-resolution (every Files `symbol` resolves; new files must NOT pre-exist; modify/
     context files must exist);
   - standards-reference consistency (the `standards:` value is one of standards.md/CLAUDE.md/
     AGENTS.md and is referenced identically in prose);
   - identifier/example consistency (a worked example must NOT source its mock dimensions from
     the constant under test; flag a model/URL/identifier used in two different forms).
   It does NOT enforce full cross-reference integrity (too fragile).
5. **Update the `create-spec` / `create-feature` commands** — adaptive grilling BEFORE drafting
   (up to 8 highest-uncertainty questions, chosen per task), and emit the v3 format. Preserve
   the grilling in the Clarifications table.

## Hard rules — preserve these deliberate tradeoffs
- **DRY constitution:** the six-areas/boundaries/invariants live ONCE in the constitution file;
  each slice inlines only a short, slice-relevant excerpt. Do not inline the whole thing.
- **Inline telemetry stays** (the `execution` cost block) — a reviewer may call it ceremony;
  it is intentional. Keep it.
- **Rollout: new specs only.** v2 specs are frozen and never backfilled. `schema_version` gates
  the linter. Do not rewrite existing specs.
- **Right-size:** one full template always, but keep each section lean. Approach is decisions/
  seams, never pseudocode.

## Acceptance
- The constitution exists, is grounded in THIS repo's real commands/lint/idiom, and the
  existing CLAUDE.md/AGENTS.md points to it (with your proposed edit approved).
- A new spec authored from the template passes the linter clean.
- The linter fails, with a clear message, on: a missing/misordered section; an assumption with
  no `if_wrong`; a Files symbol that doesn't resolve; a stray edit outside the manifest; a
  worked example that sources its dimension from the constant under test.
- `create-spec` interrogates first and emits v3.

## Working style
- Match this repo's language, lint, and test conventions. Run the repo's own gate (lint + types
  + tests) before declaring anything done.
- Propose before overwriting or deleting any existing file (especially CLAUDE.md/AGENTS.md).
- Keep the linter dependency-light; prefer the repo's existing toolchain.
- When a design detail isn't covered here or in `spec_overhaul_plan.md`, ask rather than guess.
