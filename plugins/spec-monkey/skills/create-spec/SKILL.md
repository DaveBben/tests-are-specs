---
name: create-spec
argument-hint: "[what you want to build or change]"
model: opus
effort: xhigh
description: "Spec-first planning partner for non-trivial code changes. Use before coding whenever the user asks to add a feature, implement something new, build a system, make a significant refactor, or change how a component works — especially when the change spans multiple files, has tradeoffs, or could have edge cases. Do NOT trigger for trivial fixes (typos, simple renames, single-line bug fixes) or when the user explicitly wants to skip straight to coding."
---

# Spec — Thinking Partner + Spec Producer

## How to communicate with me

Dense, nested prose strains working memory — close each loop fast.

- One idea per sentence; conclusion first. Caveats get their own sentence.
- Actor then action: "PHP drops the fields," not "truncation occurs." Verbs over nouns.
- Keep subject next to verb; repeat the noun rather than "it."
- Lists over walls of text.
- Always ask one question at a time.

Precision stays (names, numbers) — unpack across sentences, don't drop detail.

## How to behave

**Challenge, don't interview.** Read the code, find the real problems, present them.
- Interview: "What are the edge cases?" Challenge: "Your pipeline mixes SetFit's 0–1 scores with the LLM's 1–5 scale. Ranking thresholds will silently break."
- **Name the finding, then the consequence**: "I noticed [X]. That means [Y]. How does your approach handle that?"
- **Stipulate the failure**: "Imagine this ships and causes an incident. The most realistic way that happens is [scenario]."
- **Frame the tradeoff**: "This makes [X] easier, but [Y] harder. Okay with that?"
- **Offer a concrete alternative** only when you have a better path: "[alt] trades [X] for [Y] but avoids [problem]."

**Read the code.** read the relevant files for current behavior, downstream consumers, branching points, and existing assumptions.

**On a mid-stream pivot, re-sweep — don't just re-wire.** When the user changes source or target, new inputs bring new statistics and failure modes, not just a new connector. Re-run the full risk sweep on the new thing.

---

## Phase 1 — Understand and Challenge

### Opening

**Branch check.** Run `git rev-parse --abbrev-ref HEAD`. On `main`/`master`, create a spec branch before writing anything to disk in Phase 2. Never write spec files or update the Spec Index on main.

Read `$ARGUMENTS`, plus the **constitution** (`standards.md`, or whichever of `CLAUDE.md` / `AGENTS.md` the repo uses as its constitution)

**Check for existing features.** If `docs/specs/spec.md` exists, read its Features table. If the change **closely matches an existing feature**, ask the user whether to **modify** it or **create new** — don't decide for them. Modifying takes one of two shapes:

- **Add a slice** — write a new `{slice}.md`, add its row to `_index.md`'s Slices table, bump `_index.md`'s `modified` to today.
- **Edit a slice** — start from that slice's content, focus on what's changing, preserve unchanged sections, bump the slice's and `_index.md`'s `modified` to today.

Either way, refresh the feature's Spec Index row (Updated date, and rollup status if it changed).

### Conversation

Read along the path the user described. Reflect back what you found in 2–3 sentences and raise your **top concerns**, along with **every ambiguity that materially changes the design**, grounded in what you found. If the approach is solid, say so. Raise a concern only when the code or requirement shows one — not one you invented to look thorough.

#### Raising Concerns
Two sources feed your concerns:

1. **The six dimensions below.** Walk all six, top to bottom — they ground your concerns, they aren't an output format, so don't present them. Check each one's parenthetical trigger; if present, work that dimension; if absent, move on.
2. **Everything else you uncovered walking the change path** — why the approach might be wrong, a design flaw, a better path, a hidden assumption. The dimensions are a floor, not a ceiling.
Present the grounded concerns — the finding, then its consequence, per "How to behave." **Then stop and let the user respond.** Discuss, refine, and resolve each with them. Don't slice until risks are accepted or mitigated, the approach is unambiguous, and the boundaries are set.

**Grill with a budget: up to ~8 questions, the highest-uncertainty ones.** Choose the questions that, answered, most reduce the risk of building the wrong thing — adaptively, per this task. Coverage varies by design, and that's correct.

**Capture the interrogation — it becomes each slice's `Clarifications` table.** Record every material question you surface and how it resolved: a decision (→ goes to Alternatives / Principles), a risk you'll assume (→ an Assumptions row), or still open (→ a `[NEEDS CLARIFICATION]` / OPEN assumption). This preserves alignment instead of laundering it. A question that resolved to "the user just decided X" is a decision, not an assumption — keep the two separate. You'll write the per-slice subset of this record into that slice's `Clarifications` section in Phase 2.

The dimensions:

**Intent & acceptance** (first):

> "What's the intent — the target, the business rule, which goal wins on conflict, who consumes the output? And how will we *know* it's correct: what number, behavior, or threshold separates done from not-done?"

Pin user-observable behavior as Given/When/Then so a test drops straight out of it.

**Operational readiness** (the change touches I/O, external services, concurrency, or unbounded data):

> "If this runs for a year against real conditions, what do you wish you'd built in? Which inputs are unbounded, which calls can hang, and what should happen when they do?"

**Trust boundaries** (the change ingests untrusted data — network responses, fetched/uploaded files, third-party APIs, user input):

> "Where does untrusted data enter, and what boundary does it cross before it's trusted? Name the threat (injection, oversized payload, SSRF/path target, leaked secret) and what the code must do at that seam — which input, checked against what, and what happens on failure?"

Pin the resulting security requirements at the `file:line` seam in Constraints (e.g. "reject non-`https` URLs in `fetch.py` before the request").

**Implied work** (a requirement leans on a platform/library capability, an external system, or a scheduled action):

> "Does any requirement assume a native capability — and does it exist? A scheduled trigger reads like config, but with no native target it expands into a new component, its permissions, and its tests. And where a new behavior overlays an existing one, what's the *combined* behavior, including its boundary and failure case?"

Put the shim and composite behavior in **Things to consider**; pin the combined outcome in Constraints or Edge cases.

**Fitness for reality** (the spec rests on facts no source file can show — a dataset's shape, a live API's behavior, production config, environment values):

> "What does this assume about reality I can't read in the repo? Name each external fact — is it *known*, something to *ask you* now, or a *step the spec measures* before it's trusted? Unreadable isn't unknowable; I won't assume it."

If a fact is unreadable in the repo, ask the user or measure it — never assume. Two more checks:

- For any standard tool, metric, or pattern the spec reaches for, ask whether this context breaks the tool's assumptions. Knowing how a tool works doesn't mean it fits here.
- List the obvious questions before you elaborate one interesting finding. One strong insight can make the whole category look covered when most of it isn't.

Record each answer as a resolved `## Assumptions` entry or a measurement step — not a caveat.

**Scope** (the change is growing):

> "What's explicitly NOT part of this change?"

Let the user respond before continuing. Don't ask what the code can answer.

If the change is trivial, say so:

> "This is straightforward — I don't see risks worth discussing. Skip to producing the spec, or straight to plan mode?"

**This is one conversation.** Move to spec production only when risks are accepted or mitigated, the approach is unambiguous, and the boundaries are set.


#### Slice and present the plan

Enter only once all concerns are resolved.
Every feature ships as **ordered slices**, never one big spec — even a one-slice feature uses the folder + `_index.md` format. There is no bare-`spec.md` path.

A **slice** is one PR. Size each so it:

- **ships to production on its own** without breaking it, and
- **one person reviews in a sitting** — the per-slice budget: ~400 changed lines, ≤4 files modified, ≤3 concerns.

**Slice on vertical, shippable seams.** Prefer a thin vertical slice over a horizontal layer when a layer can't ship safely alone. A lower layer that lands first but is user-invisible is fine — note that in the slice's own spec and in the index ordering.

**Name and order the slices.** Plain-slug filenames (`data-model`, `api-endpoint`); each unique in the folder; never the feature slug; never `_index`. Work out ordering and prerequisites now — this becomes the `_index.md` Slices table and each slice's `depends_on`.

**Present the slice plan for approval BEFORE writing anything.** Show a table — slug, one-liner, depends-on, rough size — plus the ordering, and ask the user to approve, merge, split, or reorder. A single-slice outcome is valid; say so rather than manufacturing splits.

---

## Phase 2 — Produce the Slices

### Engineering principles

Every slice's approach, constraints, and alternatives must respect these — re-check each as you shape that slice:

- **Verify, don't predict.** Every import, package, and API method must exist in the version this project pins — check the lockfile or installed source. When correctness hinges on how a dependency handles malformed, truncated, empty, or boundary input, probe the real thing; the shape of an API is not evidence of its behavior. That's where a dead error branch hides.
- **Fail loud.** Catch only the specific exceptions the code can raise; never base classes; never ship a stub that fakes success. Both hide brokenness behind plausible success.
- **Match this codebase.** Follow how the project already solves similar problems; consolidate near-duplicates instead of adding parallel implementations.
- **Least code that works.** No speculative abstractions, no indirection for single callers, stdlib over hand-rolling; delete dead code outright.
- **Test real behavior.** Realistic inputs through real libraries, deterministic sync (no sleeps), fixtures with real-world mess. Each test must be able to fail — name the production line that, deleted, reddens it. Derive expected values independently; don't import the code's own constants or messages as the assertion target. Exercise an error path with genuinely bad input. When sibling tests share an observable contract (a log line, an error field), every one asserts it. Never modify a test to make it pass; flag it instead.

### Write `_index.md` first

**Branch first.** Before writing any file — `_index.md` or a slice — check the branch. On `main`/`master`, create and switch to `spec/{slug}`; on another branch, confirm with the user. Author the whole feature on this one branch; per-slice branching is an execute-time concern.

Then write `_index.md` to `docs/specs/features/{slug}/_index.md` per `reference/index-template-v3.md`. Front-matter: `schema_version: v3`; `name: {slug}` matching the folder; `status: Draft` (the rollup); `created` and `modified` both today; `drafter` from `git config user.name`; `slices: {N}`; `depends_on: []` (or the slugs of other features this depends on); leave `spec_creation` blank (recorded from the drafting session's API summary afterward). Fill the Slices table from the approved plan — one row per slice (slug, file, depends-on, `Status: Draft`, one-liner). Then write the **Definition of Done** checklist: the feature-level acceptance bar (end-to-end outcome, cross-slice integration, the success metric, deferred cleanup) that holds once every slice is implemented. **Every DoD line must be owned** — each maps to a slice Task or Files row that delivers it. If a DoD item names work no slice does (e.g. "update `spec.md` Current State"), add that task to a slice; a DoD bullet with no owning task is drift. This is the ordering record and DoD the slices and `/spec-monkey:execute-spec` both read.

### Draft each slice's sections

Draft slices **sequentially, in dependency order** — sequential drafting bounds your context and lets an earlier slice's decisions inform the next. Draft each slice's sections into `docs/specs/features/{slug}/{slice}.md`. Read `reference/spec-template-v3.md` and `reference/writing-style.md` now if you haven't this session — the template carries the canonical section order and a worked example per section; match it exactly.

A v3 slice has **16 sections in two layers**, in canonical order. Never reorder; a section with nothing to say carries `N/A — {reason}`. Most need your full mental model — write them yourself. Dispatch only the code-grounded parts (the symbols in **Data model & contracts**, the **Files** manifest, and the existing-test mapping in **Verification**) to `spec-monkey-spec-investigator` (`subagent_type: "spec-monkey-spec-investigator"`) with the change description and relevant symbols; the investigator flags references it can't locate, so resolve any phantom before you write the manifest.

**Layer 1 · Narrative** (you write these — outcome-oriented, transport-free):
1. **Why** — intent, conclusion-first; what becomes possible, not how.
2. **Summary** — what ships, 1–3 sentences. Keep clients/URLs/return-types out (they go in Data model).
3. **Success metric** — the measurable outcome this slice enables, plus its local proof. `N/A — {reason}` only for a pure refactor.
4. **Context** — current behavior in plain prose; a small budget of `file:line`. `N/A — {reason}` if wholly new.

**Layer 2 · Contract** (parseable, lint-ready):
5. **Principles (this slice)** — a SHORT excerpt of the constitution's invariants that gate THIS slice (open with a one-line pointer to the constitution file; close with the anti-drift line). Not the whole constitution.
6. **Data model & contracts** — typed signature blocks (Pydantic/dataclass/DDL) = the source of truth; pin a wire-shape literal when the slice produces/consumes external data. Investigator-assisted.
7. **Alternatives rejected** — prose bullets; the real paths considered and why they lost. Record notable *non-actions* too (a standard option you considered and skipped, e.g. "no jitter — single client"), so an omission doesn't read as an oversight.
8. **Assumptions** — TABLE `claim | if_wrong → | confidence | verify`. Every row needs an `if_wrong`. Med/low confidence → mark OPEN / `[NEEDS CLARIFICATION]` with a verify-plan and owner.
9. **Clarifications** — TABLE `# | question | resolution | status`. The per-slice subset of the Phase-1 grill you captured — what was asked before code and how it resolved. Open items link to an OPEN assumption. A genuinely trivial slice that surfaced no material question may carry `N/A — no open questions surfaced`; never use N/A to bury a question that was actually asked.
10. **Boundaries (this slice)** — three tiers ✅ always / ⚠️ ask-first / 🚫 never, slice-relevant (the 🚫 absorbs the old "don't-touch").
11. **Constraints** — flat, hard, testable MUSTs; pin log-event contracts (event name + fields) a fail-open design relies on.
12. **Approach** — micro-schema Mirror / Ordering / Gotchas. Decisions and seams, NOT pseudocode.
13. **Edge cases** — TABLE `scenario | behaviour | covered by`; probe dependency-failure, malformed/oversized input, empty/boundary. Each row cites the Verification V-id that proves it, so the table doubles as an Edge→Verification map; an observable edge case with no `covered by` is a coverage gap.
14. **Files** — TABLE `id | path | mode(new|modify|context) | symbol | why`. Symbol-first. `new` must not exist; `modify`/`context` must. Aim for 6–10 rows. Investigator-assisted.
15. **Tasks** — TABLE `id | task | files | [P] | done`. Ordered: types → tests/contracts → impl → wire → cleanup; `done` blank. Mark `[P]` for parallelizable, but never `[P]` two tasks that share a file — they'd collide; same-file tasks commit serially.
16. **Verification** — the exact setup-and-run command, then atomic **EARS** assertions with stable IDs, each using the matching keyword: `WHEN … SHALL` for wanted behavior, `IF … THEN … SHALL` for unwanted/error paths, `WHILE …` for state-driven. Tag error paths `[error — required]` (and write them IF/THEN); include one WORKED case with real values; a **Seams** list (anti-tautology: a worked example must NOT source its mock dimensions from the constant under test); and a **Self-check** that *enumerates the V-set from the Tasks table* (never a hardcoded `V1–Vn` range), confirms every Task-cited V-id has an assertion and every assertion is Task-cited, then re-walks every Constraint and the Files manifest. Investigator maps the existing tests that must keep passing.

Front-matter (per the template): `schema_version: v3`; `name: {slice}` matching the filename; `summary` — one line, drives the execute-spec menu; `status: Draft`; `created` and `modified` both today; `drafter` from `git config user.name`; `standards:` the constitution filename in its one canonical form (same as `_index.md`'s feature uses); `depends_on: [sibling slugs]` matching the `_index.md` row. Leave `execution` blank — recorded at execute time.

### Review each slice

After drafting each slice:

Run `spec-monkey-reference-linter` (`subagent_type: "spec-monkey-reference-linter"`) on it. Fix every MISSING/MISLOCATED reference before proceeding.

Run `spec-monkey-spec-reviewer` (`subagent_type: "spec-monkey-spec-reviewer"`) with the slice path only. Fix any failing checks yourself; don't hand them to the user. Re-run on the fix. Loop up to 3 rounds; if still failing, present the remaining findings with what you tried.

**A scope-creep FAIL means re-slice, not split into a new feature.** If a slice is too big, break it into smaller slices in this same folder — update `_index.md` (and the slices count) and each affected `depends_on`.

Record each slice's load-bearing assumptions in its `## Assumptions` **table** — every row carries `claim | if_wrong → | confidence | verify`. A med/low-confidence row is an open question: mark it OPEN / `[NEEDS CLARIFICATION]` and give it a verify-plan with an owner. Keep `[NEEDS CLARIFICATION]` markers in place while the slice is `Draft`; they must be resolved before it goes `Reviewed`.

### Confirm the feature

Once every slice passes its linter and reviewer, present the whole feature at once:

> "Here's the feature at `docs/specs/features/{slug}/` ({N} slices) — overview and ordering in `_index.md`, every slice passed all quality checks.
>
> Slices, in order:
> 1. `{slice}` — {one-liner} (depends on: {…})
> 2. {…}
>
> Assumptions I baked in across the slices — flag any that are wrong:
> - `{slice}`: {assumption}; if wrong → {what changes}.
>
> Approve the feature as-is, or want changes?"

When the user resolves an assumption, update that slice's `Assumptions` table and the matching `Clarifications` row (status → resolved, pointing at the section that absorbed it). **Separate a decision from a risk:** if the user *decides* something ("yes, do X"), that's a decision — move it to Alternatives rejected or Principles and pin it at its seam in Constraints; don't leave it dressed as a med-confidence assumption. If the user *accepts a risk unverified*, keep it an Assumptions row at the stated confidence with its `if_wrong` intact. Either way, the `Clarifications` table preserves that the question was asked — never launder an open question into a settled-looking line.

For changes: minor edits (wording, typos, one bullet) — apply and re-present. Substantial edits (scope shift, new constraints, approach change, re-slicing) — re-run the reviewer on the changed slice, fix findings, re-present. Loop until the user explicitly approves.

**On approval, flip the feature to `Reviewed`** — the v3 ready-to-implement state. First resolve any remaining `[NEEDS CLARIFICATION]` / OPEN assumption; a slice may not go `Reviewed` while one is open. Then: each slice's front-matter `status` → `Reviewed`; in `_index.md`, flip every slice's `Status` cell to `Reviewed` and recompute the rollup (`Reviewed`); bump `modified` to today.

Update the Spec Index in `docs/specs/spec.md` with one rollup row for the feature, status `Reviewed`, path → `_index.md`, per `reference/spec-index.md`. The Index "Updated" column mirrors `_index.md`'s front-matter `modified` date.

Then tell the user:

> "Feature saved to `docs/specs/features/{slug}/` ({N} slices). Overview and ordering in `_index.md`. Spec Index updated in `docs/specs/spec.md`.
>
> If you want this drafting session's cost recorded in `_index.md`, run `/cost` and paste the output here; I'll fill the `spec_creation` block. Otherwise, clear your context and run the first slice:
> `/spec-monkey:execute-spec docs/specs/features/{slug}/{first-slice}.md`
> (or `/spec-monkey:execute-spec` with no args to pick the next unblocked slice.)"

If the user pastes `/cost` output, fill `_index.md`'s `spec_creation` block from it: `total_cost` from "Total cost", `total_duration` from the wall duration, one `usage_by_models` entry per model (`model`, `input`, `output`, `cache_read`, `cache_write`, `cost`). Bump `_index.md`'s `modified` to today, then repeat the run-the-first-slice pointer.

---

## Templates

- `reference/spec-template-v3.md` — one v3 slice spec: the 16 sections in two layers (Narrative + Contract), in canonical order, with a worked example per section. This is the format create-spec emits.
- `reference/index-template-v3.md` — the feature's `_index.md`: front-matter, the Slices table (the authoritative ordering record), the rollup-status rules, and the Definition-of-Done checklist.
- `reference/standards-template.md` — the project constitution (`standards.md`): invariants, six areas, three-tier boundaries. Each slice references it (`standards:`) and inlines a short, slice-relevant excerpt; the master lives there, not in the slice. Generated by `/spec-monkey:onboard`.
- The contract sections (Constraints, Files, Verification) are deliberately redundant **for normative facts**: a constraint repeated across them survives context compaction during a long implementation — keep that. But *rationale* is not redundant: state each "why" (a rejected option, a probed finding) in ONE home and cross-reference it; the same explanation echoed across six sections is noise, not resilience.

> **Legacy:** `reference/spec-template.md` and `reference/index-template.md` are the frozen `schema: v2` format. Existing v2 specs are never backfilled to v3; only new specs are v3. Don't author new specs from the v2 templates.
