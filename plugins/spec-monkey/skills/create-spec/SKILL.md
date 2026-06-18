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

- One idea per sentence; conclusion first
- caveats get their own sentence.
- Actor then action: "PHP drops the fields," not "truncation occurs." Verbs over nouns.
- Keep subject next to verb; repeat the noun rather than "it."
- Plain words; define load-bearing terms once. Lists over walls of text.

Precision stays (names, numbers) — unpack across sentences, don't drop detail.

## How to behave

**Challenge, don't interview.** Read the code, find the real problems, present it.
- Interview: "What are the edge cases?" Challenge: "Your pipeline mixes SetFit's 0–1 scores with the LLM's 1–5 scale. Ranking thresholds will silently break."
- **Name the finding, then the consequence**: "I noticed [X]. That means [Y]. How does your approach handle that?"
- **Stipulate the failure**: "Imagine this ships and causes an incident. The most realistic way that happens is [scenario]."
- **Frame the tradeoff**: "This makes [X] easier, but [Y] gets harder. Okay with that?"
- **Offer a concrete alternative** only when you have a better path: "[alt] trades [X] for [Y] but avoids [problem]."

**Read the code.** CLAUDE.md, Agents.md, and spec.md give orientation; read the relevant files to understand current behavior, downstream consumers, branching points, and existing assumptions.

**Surface every ambiguity that materially changes the design**, grounded in what you found. If the approach looks solid, say so. Raise a concern only when the code or the requirement shows one — a real ambiguity, not one you invented to look thorough.

**This is one conversation** Move to spec production only when risks are identified and accepted or mitigated, the approach is unambiguous, and the boundaries are set.

**On a mid-stream pivot, re-sweep — don't just re-wire.** When the user changes the source or target, new inputs bring new statistics and failure modes, not just a new connector. Re-run the full risk sweep on the new thing, not only the code path.

---

## Phase 1 — Understand and Challenge

### Opening

**Branch check.** Run `git rev-parse --abbrev-ref HEAD`. On `main`/`master`, create a spec branch before writing anything to disk in Phase 2. Never write spec files or update the Spec Index on main.

Read `$ARGUMENTS`, plus `CLAUDE.md`, `AGENTS.md`, and `spec.md` if they exist.

**Check for existing features.** If `docs/specs/spec.md` exists, read its Features table — each row is a feature pointing at its `_index.md`. If the change **closely matches an existing feature**, ask the user whether to **modify** it or **create new** — don't decide for them. Modifying a feature takes one of two shapes:

- **Add a new slice** — write a new `{slice}.md` in the feature folder, add its row to `_index.md`'s Slices table, bump `_index.md`'s `modified` to today.
- **Edit an existing slice** — start from that slice's content, focus on what's changing, preserve unchanged sections, bump the slice's `modified` and `_index.md`'s `modified` to today.

In both cases also refresh the feature's row in the Spec Index (Updated date, and the rollup status if it changed).

Read along the path the user described. Reflect back what you found in 2-3 sentences and raise your **top concerns**, grounded in the code. Let the user respond before continuing. Don't ask what the code can answer.

If the change is trivial, say so:

> "This is straightforward — I don't see risks worth discussing. Want me to skip to producing the spec, or straight to plan mode?"

### Conversation

This phase has **two gates**, and they are separate turns. Do the concern sweep and present concerns (Gate 1). **Stop. Let the user discuss and reply.** Only after concerns are resolved do you slice and present the plan (Gate 2). Never dump concerns and the slice plan in the same message — that wall of text is the failure this structure prevents.

#### Gate 1 — Surface and discuss concerns

Sweep silently, then present. Two sources feed your concerns:

1. **The six dimensions below.** Walk all six, top to bottom. Do not present them to the user — they ground your concerns, they aren't an output format. For each, check the trigger in its parentheses. If the trigger is present, work that dimension. If it's absent, note that to yourself and move on.
2. **Everything else you uncovered walking the change path.** Why the approach might be wrong, design flaws, a better path, a hidden assumption — surface these alongside the dimension findings. The dimensions are a floor, not a ceiling.

Present the grounded concerns to the user — the finding, then its consequence, per "How to behave." **Then stop and let the user respond.** Discuss, refine, and resolve each concern with them. Do not move to slicing until the risks are identified and accepted or mitigated, the approach is unambiguous, and the boundaries are set.

The dimensions:

**Intent & acceptance** (first):

> "What's the intent — the target, the business rule, which goal wins on conflict, who consumes the output? And how will we *know* it's correct: what number, behavior, or threshold separates done from not-done?"

Pin user-observable behavior as Given/When/Then so a test can be written from it directly.

**Operational readiness** (when the change touches I/O, external services, concurrency, or unbounded data):

> "If this runs for a year against real conditions, what do you wish you'd built in? Which inputs are unbounded, which calls can hang, and what should happen when they do?"

**Trust boundaries** (when the change ingests untrusted data — network responses, fetched/uploaded files, third-party APIs, user input):

> "Where does untrusted data enter, and what boundary does it cross before it's trusted? Name the threat (injection, oversized payload, SSRF/path target, leaked secret) and what the code must do at that seam — which input, checked against what, and what happens on failure?"

Pin the resulting security requirements at the `file:line` seam in Constraints (e.g. "reject non-`https` URLs in `fetch.py` before the request").

**Implied work** (when a requirement leans on a platform/library capability, an external system, or a scheduled action):

> "Does any requirement assume a native capability — and does it exist? A scheduled trigger reads like config, but with no native target it expands into a new component, its permissions, and its tests. And where a new behavior overlays an existing one, what's the *combined* behavior, including its boundary and failure case?"

Put the shim and composite behavior in **Things to consider**; pin the combined outcome in Constraints or Edge cases.

**Fitness for reality** (when the spec rests on facts no source file can show — a dataset's shape, a live API's behavior, production config, environment values):

> "What does this assume about reality I can't read in the repo? Name each external fact — and is it *known*, something to *ask you* now, or a *step the spec measures* before it's trusted? Unreadable isn't unknowable; I won't assume it."

If a fact is unreadable in the repo, ask the user or measure it — never assume it. Two more checks for this dimension:

- For any standard tool, metric, or pattern the spec reaches for, ask whether this specific context breaks the tool's assumptions. Knowing how a tool works does not mean it fits here.
- List the obvious questions in this dimension before you elaborate one interesting finding. One strong insight can make the whole category look covered when most of it isn't.

Record each answer as a resolved `## Assumptions` entry or a measurement step. Do not leave it as a caveat.

**Scope** (when the change is growing):

> "What's explicitly NOT part of this change?"

#### Gate 2 — Slice and present the plan

Only enter this gate once Gate 1's concerns are resolved. This is a **separate turn** from the concern discussion.

Every feature ships as **ordered slices**, not one big spec. Slicing is the default, always — even a one-slice feature uses the folder + `_index.md` format. There is no bare-`spec.md` path.

A **slice** is one PR. Size each slice so it:

- **ships to production on its own** without breaking it, and
- **one person reviews in a sitting** — the old thresholds become the *per-slice* budget: ~400 changed lines, ≤4 files modified, ≤3 concerns.

**Slice on vertical, shippable seams.** Prefer a thin vertical slice (a small end-to-end increment) over a horizontal layer when a layer can't ship safely alone. A lower layer that lands first but is user-invisible is fine — note that in the slice's own spec and in the index ordering.

**Name and order the slices.** Plain-slug filenames (`data-model`, `api-endpoint`); each unique in the folder; never equal to the feature slug; never `_index`. Work out the ordering and each slice's prerequisites now — this becomes the `_index.md` Slices table and each slice's front-matter `depends_on`.

**Present the slice plan for approval BEFORE writing anything.** Show a table — slug, one-liner, depends-on, rough size — plus the ordering, and ask the user to approve, merge, split, or reorder. A single-slice outcome is valid; say so rather than manufacturing splits.

---

## Phase 2 — Produce the Slices

### Engineering principles

The approach, constraints, and alternatives you write must respect these principles. Apply them to every slice you produce, not just the first — re-check each one as you shape that slice's spec:

- **Verify, don't predict.** Every import, package, and API method must exist in the version this project pins; check the lockfile or installed source before using it. Behavior counts too: when correctness depends on how a library or external system acts on malformed, truncated, empty, or boundary input (does it raise, return a sentinel, or silently truncate?), confirm it with a quick probe through the real dependency before relying on it. The shape of an API is not evidence of its behavior. This is where a dead error branch hides: the code assumes a raise that never fires.
- **Fail loud.** Catch only the specific exceptions the code can raise; never catch base exception classes; never ship a stub that fakes success. Both hide brokenness behind plausible-looking success.
- **Match this codebase.** Before writing anything new, find how this project already solves similar problems and follow that pattern; consolidate near-duplicates instead of adding parallel implementations.
- **Least code that works.** No speculative abstractions, no indirection for single callers, stdlib over hand-rolling; delete dead code outright
- **Test real behavior.** Realistic inputs through real libraries, deterministic sync (no sleeps), fixtures with real-world mess. Each test must be able to fail: name the production line that, broken or deleted, turns it red. Derive expected values independently; don't import the code's own constants or messages as the assertion target. Exercise an error path with genuinely bad input, not a payload built to match the handler. When sibling tests share an observable contract (a log line, an error field), every one of them asserts it. Never modify a test to make it pass; flag it instead.

### Write `_index.md` first

**Branch first.** Before writing any file to disk — `_index.md` or a slice — check the branch. If on `main`/`master`, create and switch to `spec/{slug}`. If on another branch, confirm with the user. Author the whole feature (`_index.md` + every slice) on this one branch; per-slice branching is an execute-time concern.

Then, before any slice spec, write the feature's `_index.md` to `docs/specs/features/{slug}/_index.md`, following `reference/index-template.md`. Populate the front-matter: `schema: v2`; `name: {slug}` matching the folder; `status: Waiting Implementation`; `created` and `modified` both today; `drafter` from `git config user.name`; `slices: {N}`; `depends_on: []` (or the slugs of other features this one depends on); leave the `spec_creation` block blank (you can't self-measure the run; it's recorded from the drafting session's API summary afterward). Fill the Slices table from the approved slice plan — one row per slice (slug, file, depends-on, `Status: Waiting Implementation`, one-liner). This is the ordering record the slice specs and `/spec-monkey:execute-spec` both read.

### Draft each slice's sections

Draft the slices **sequentially**, in dependency order — not in parallel. Sequential drafting bounds your context and lets an earlier slice's decisions inform the next. For each slice, draft the spec sections below into `docs/specs/features/{slug}/{slice}.md`.

Dispatch steps 2–4 to `spec-monkey-spec-investigator` (`subagent_type: "spec-monkey-spec-investigator"`) with the slice's change description and relevant symbols. Write steps 1 and 5 yourself — they require your full mental model.

1. **Current behavior**: plain prose a newcomer can follow. Use `file:line` sparingly.
2. **Files that matter**: every symbol the change touches — callers, type definitions, related tests. Target 6–10 files. Tag each `[modify]`/`[context]`/`[new]` (see the template); a thing you "add to" must exist or it's `[new]`. The investigator flags references it can't locate — resolve any phantom before tagging.
3. **Patterns to follow**: for anything new, name the existing pattern with a `file:line` example, or note there's no precedent. When the "pattern" is really a data contract (a message, event, or request/response shape), pin the actual shape — paste it or link the producer/consumer — not just its name. If another repo owns it, say so and cite the source.
4. **Tests**: existing tests that must keep passing, plus new tests for Phase 1 edge cases. Name the test file whose structure new tests should mirror, so the implementer copies it instead of guessing. Use real fixtures over mocks. Call for property-based tests for invariants or bounds.
5. **Verification command**: the exact setup-and-run sequence — any dependency install with the extras the tests need, service start, or env step, then the command — then a checklist: Given/When/Then for user-facing behavior, plain bullets otherwise. Include at least one error-path bullet for I/O or untrusted input. A verification *seam* is a criterion that depends on a test mechanism whose limits the criterion alone hides. At each seam, name the mechanism, not just the property. The template names the three seam types and gives an example of each — see its "Seams to make concrete" list.
6. **Optional domain sections**: add structured artifacts (schema definitions, state tables, migration plans) between "Current behavior" and "Alternatives rejected" if they aid review.

Write each slice to `docs/specs/features/{slug}/{slice}.md` following `reference/spec-template.md` and `reference/writing-style.md` (read both if you haven't this session). Populate the YAML front-matter: `schema: v2`; `name: {slice}` matching the filename; `summary` — a one-line summary of the slice's change (this drives the execute-spec menu); `status: Waiting Implementation`; `created` and `modified` both today; `drafter` from `git config user.name`; `depends_on: [sibling slugs]` matching this slice's row in `_index.md`. Leave the `execution` block blank — it's recorded from the `/spec-monkey:execute-spec` run's API summary at execute time.

### Review each slice

For each slice, after drafting it:

Run `spec-monkey-reference-linter` (`subagent_type: "spec-monkey-reference-linter"`) on the slice. Fix every MISSING/MISLOCATED reference before proceeding.

Run `spec-monkey-spec-reviewer` (`subagent_type: "spec-monkey-spec-reviewer"`) with the slice path only. Fix any failing checks; don't hand them to the user. Re-run on the fixed slice. Loop up to 3 rounds; if still failing, present the remaining findings with what you tried.

**A scope-creep FAIL means re-slice, not split into a new feature.** The reviewer now judges the slice boundary. If a slice is too big, break it into more, smaller slices in this same folder — update `_index.md` (and the slices count) and each affected `depends_on` to match.

Record each slice's **2–3 load-bearing assumptions** in its `## Assumptions` section.

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
> Do you approve the feature as-is, or want changes?"

When the user resolves an assumption, update that slice's section. When they accept one, mark it `(accepted by {who})` in Assumptions and inline at the relevant seam in the slice's Constraints or Approach.

For changes: minor edits (wording, typos, one bullet) — apply and re-present. Substantial edits (scope shift, new constraints, approach change, re-slicing) — re-run the reviewer on whichever slice changed, fix findings, re-present. Loop until the user explicitly approves.

Update the Spec Index in `docs/specs/spec.md` with one rollup row for the feature, status `Waiting Implementation`, path → `_index.md`. Follow `reference/spec-index.md` for row format. The Index "Updated" column mirrors `_index.md`'s front-matter `modified` date.

Tell the user:

> "Feature saved to `docs/specs/features/{slug}/` ({N} slices). Overview and ordering in `_index.md`. Spec Index updated in `docs/specs/spec.md`.
>
> If you want this drafting session's cost recorded in `_index.md`, run `/cost` and paste the output here; I'll fill the `spec_creation` block. Otherwise, clear your context and run the first slice:
> `/spec-monkey:execute-spec docs/specs/features/{slug}/{first-slice}.md`
> (or `/spec-monkey:execute-spec` with no args to pick the next unblocked slice.)"

If the user pastes `/cost` output, fill `_index.md`'s front-matter `spec_creation` block from it: `total_cost` from "Total cost", `total_duration` from the wall duration, and one `usage_by_models` entry per model (`model`, `input`, `output`, `cache_read`, `cache_write`, `cost`). Bump `_index.md`'s `modified` to today, then repeat the run-the-first-slice pointer.

---

## Templates

Two templates back this skill:

- `reference/index-template.md` — the feature's `_index.md`: front-matter, the Slices table (the authoritative ordering record), and the rollup-status rules.
- `reference/spec-template.md` — one slice spec. Below its "Implementation contract" divider, Constraints, Files that matter, and Verification are deliberately redundant: a constraint repeated across them survives context compaction during a long implementation. Keep that redundancy; defend it if a reviewer flags it as bloat.
