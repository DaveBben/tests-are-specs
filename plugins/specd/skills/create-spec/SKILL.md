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

- One idea per sentence (~15–20 words); conclusion first.
- Actor then action: "PHP drops the fields," not "truncation occurs." Verbs over nouns.
- One condition per sentence; caveats get their own sentence.
- Keep subject next to verb; repeat the noun rather than "it."
- Plain words; define load-bearing terms once. Lists over walls of text.

Precision stays (names, numbers) — unpack across sentences, don't drop detail.

## How to behave

**Challenge, don't interview.** Read the code, find the real problem, present it.
- Interview: "What are the edge cases?" Challenge: "Your pipeline mixes SetFit's 0–1 scores with the LLM's 1–5 scale. Ranking thresholds will silently break."
- **Name the finding, then the consequence**: "I noticed [X]. That means [Y]. How does your approach handle that?"
- **Stipulate the failure**: "Imagine this ships and causes an incident. The most realistic way that happens is [scenario]."
- **Frame the tradeoff**: "This makes [X] easier, but [Y] gets harder. Okay with that?"
- **Offer a concrete alternative** only when you have a better path: "[alt] trades [X] for [Y] but avoids [problem]."

**Read the code.** CLAUDE.md, Agents.md, and spec.md give orientation; read the relevant files to understand current behavior, downstream consumers, branching points, and existing assumptions. Agressively dispatch broad sweeps to `Explore` subagents.

**Surface every ambiguity that materially changes the design**, grounded in what you found. If the approach looks solid, say so; don't manufacture concerns.

**This is one conversation, not a pipeline.** Don't force both phases if the user only needs one. Move to spec production only when risks are identified and accepted or mitigated, the approach is unambiguous, and the boundaries are set.

---

## Phase 1 — Understand and Challenge

### Opening

**Branch check.** Run `git rev-parse --abbrev-ref HEAD`. If on `main`/`master`, note that you'll create a spec branch before writing anything to disk in Phase 2 (the slug isn't known yet). If on another branch, proceed — the spec will be written there. Never write spec files or update the Spec Index on main.

Read `$ARGUMENTS`. Read `CLAUDE.md`, `AGENTS.md` and `spec.md` if they exist.

**Check for existing specs.** If `docs/specs/spec.md` exists, read the Features table in the Spec Index. If the requested change **closely matches an existing spec**, stop and ask the user whether they want to **modify that spec** or **create a new one** — don't decide for them.

- **Modify**: read the existing spec and use its current content as the starting point for the new version. Focus the conversation on what's changing, and update the existing file in Phase 2 (preserving unchanged sections, updating the "Last updated" date).
- **Create new**: proceed with a fresh spec as normal.

Read along the path the user described. Then reflect back what you found in 2-3 sentences and raise your **top concerns**, grounded in the code. Let the user respond before continuing.

Don't ask what the code can answer. Start with substance.

If the change is trivial, say so:

> "This is straightforward — I don't see risks worth discussing. Want me to skip to producing the spec, or straight to plan mode?"

### Conversation

Probe each dimension when it applies.

**Intent & acceptance** (first; ask what the code can't tell you):

> "What's the intent? The target (precision/recall, a latency budget), the business rule, which goal wins on conflict, who consumes the output? And how will we *know* it's correct: what number, behavior, or threshold separates done from not-done?"

Pin user-observable behavior as Given/When/Then ("given [state], when [action], then [outcome]") so a test can be written from it directly.

**Operational readiness** (when the change touches I/O, external services, concurrency, or unbounded data):

> "If this runs for a year against real conditions, what do you wish you'd built in? Implementing agents default to the happy path: unbounded inputs, hanging calls, unscoped thread pools, silent bad data. Which inputs here are unbounded, which calls can hang, and what should happen when they do?"

**Trust boundaries** (when the change ingests untrusted data: network responses, fetched/uploaded files, third-party APIs, user input):

> "Where does untrusted data enter, and what boundary does it cross before it's trusted? Name the threat (injection, oversized payload, SSRF/path target, a secret leaking into logs) and what the code must do at that seam. 'Validate the input' isn't an answer: which input, checked against what, and what happens on failure?"

Pin the resulting security requirements at the `file:line` seam in Constraints, like any other (e.g. "reject non-`https` URLs in `fetch.py` before the request").

**Scope** (when the change is growing):

> "What's explicitly NOT part of this change?"

### Decomposition check

Before moving to Phase 2, size the change. If it would **modify more than 4 files**, span **more than 3 independent concerns**, or run past **~400 lines**, propose splitting it into multiple specs with an explicit ordering (which ships first, what each depends on) and let the user decide.

---

## Phase 2 — Produce the Spec

### Engineering principles

The approach, constraints, and alternatives you write must respect these principles. Apply them as you shape the spec:

- **Verify, don't predict.** Every import, package, and API method must exist in the version this project pins — check the lockfile or installed source before using it.
- **Fail loud.** Catch only the specific exceptions the code can raise; never catch base exception classes; never ship a stub that fakes success. Both hide brokenness behind plausible-looking success.
- **Match this codebase.** Before writing anything new, find how this project already solves similar problems and follow that pattern; consolidate near-duplicates instead of adding parallel implementations.
- **Least code that works.** No speculative abstractions, no indirection for single callers, stdlib over hand-rolling; delete dead code outright
- **Test real behavior.** Realistic inputs through real libraries, deterministic sync (no sleeps), fixtures with real-world mess. Never modify a test to make it pass — flag it instead.

### Draft the sections

Dispatch steps 2–4 to `specd-spec-investigator` (`subagent_type: "specd-spec-investigator"`) with the change description and relevant symbols. Write steps 1 and 5 yourself — they require your full mental model.

1. **Current behavior**: plain prose a newcomer can follow. Use `file:line` sparingly.
2. **Files that matter**: every symbol the change touches — callers, type definitions, related tests. Target 6–10 files.
3. **Patterns to follow**: for anything new, name the existing pattern with a `file:line` example. Note if there's no precedent.
4. **Tests**: existing tests that must keep passing, plus new tests for Phase 1 edge cases. Use real fixtures over mocks. Call for property-based tests (e.g. Hypothesis) for invariants or bounds.
5. **Verification command**: the exact command, then a checklist — Given/When/Then for user-facing behavior, plain bullets otherwise. Include at least one error-path bullet for I/O or untrusted input.
6. **Optional domain sections**: add structured artifacts (schema definitions, state tables, migration plans) between "Current behavior" and "Alternatives rejected" if they aid review.

### Review and confirm

Check the branch. If on `main`/`master`, create and switch to `spec/{slug}`. If on another branch, confirm with the user. Never write spec files on main.

Write the draft to `docs/specs/features/{slug}/spec.md` following `reference/spec-template.md` and `reference/writing-style.md` (read both if you haven't this session).

Run `specd-reference-linter` (`subagent_type: "specd-reference-linter"`) on the spec. Fix every MISSING/MISLOCATED reference before proceeding.

Run `specd-spec-reviewer` (`subagent_type: "specd-spec-reviewer"`) with the spec path only. Fix any failing checks; don't hand them to the user. Re-run on the fixed spec. Loop up to 3 rounds; if still failing, present the remaining findings with what you tried.

Record the **2–3 load-bearing assumptions** in the spec's `## Assumptions` section. Then present them:

> "Here's the spec at `docs/specs/features/{slug}/spec.md` — it passed all quality checks.
>
> Assumptions I baked in — flag any that are wrong:
> 1. {assumption}; if wrong → {what changes}.
> 2. {…}
>
> Do you approve it as-is, or want changes?"

When the user resolves an assumption, update the section. When they accept one, mark it `(accepted by {who})` in Assumptions and inline at the relevant seam in Constraints or Approach.

For changes: minor edits (wording, typos, one bullet) — apply and re-present. Substantial edits (scope shift, new constraints, approach change) — re-run the reviewer, fix findings, re-present. Loop until the user explicitly approves.

Update the Spec Index in `docs/specs/spec.md` with status `Waiting Implementation`. Follow `reference/spec-index.md` for row format.

Tell the user:

> "Spec saved to `docs/specs/features/{slug}/spec.md`.
> Spec Index updated in `docs/specs/spec.md`.
>
> Clear your context and run:
> `/specd:execute-spec docs/specs/features/{slug}/spec.md`"

---

## Spec template

The full template lives in `reference/spec-template.md`. Below the "Implementation contract" divider, Constraints, Do NOT, Files that matter, and Verification are deliberately redundant: a constraint repeated across them survives context compaction during a long implementation. Keep that redundancy; defend it if a reviewer flags it as bloat.
