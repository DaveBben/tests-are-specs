# Spec Template

Read this when producing the spec in Phase 2. The implementing agent (`/spec-monkey:execute-spec`) consumes the result, so fill every section with the precision described in the placeholders.

A feature is **sliced**: this template fills ONE slice file (`{slice}.md`) inside `docs/specs/features/{slug}/`. The folder also holds an `index.md` (see `index-template.md`) with the feature overview and slice ordering. Each slice is a complete, self-contained spec. `/spec-monkey:execute-spec` runs one slice per call, producing one PR. Size each slice to ship on its own without breaking production. One person reviews it in a sitting (~400 changed lines).

The spec serves two audiences with one document.

Above the "Implementation contract" divider: motivation, summary, current state, alternatives, edge cases, the assumptions the change rests on, and the Approach. This is everything a human reviewer needs to understand and approve *how* the change will be made. The Approach is the hinge: the prose strategy the reviewer signs off on and the direction the implementer then executes.

Below the divider: the binding contract that pins that strategy to specifics. Constraints, Files, and Verification are deliberately redundant with each other.

**Writing style.** The prose sections follow the readable style in `writing-style.md` (this directory). These are Why, Summary, Current behavior, Approach, Things to consider, and the Edge-case descriptions. Use one idea per sentence, actor-first voice, caveats split into their own sentence, and conclusion first.

The implementation-contract sections below the divider are exempt. There, identifier density and redundancy are load-bearing, so keep them dense.

**Front-matter.** Every spec opens with a YAML front-matter block (`---` fences). A deterministic linter validates it. Fill the fields as follows:

- `name` — the slice's slug, identical to its filename without `.md` (e.g. `data-model` for `data-model.md`). Matches this slice's row in `index.md`.
- `summary` — a one-line summary of the change this slice makes. This is what `/spec-monkey:execute-spec` shows in its slice-selection menu, so keep it to a single, scannable line. Quote it if it contains a colon.
- `status` — lifecycle state. One of: `Waiting Implementation` | `Implemented` | `Superseded` | `Deprecated` | `Needs Revision`. New specs start at `Waiting Implementation`.
- `created` — `YYYY-MM-DD`, set once when the spec is first written; never changes.
- `modified` — `YYYY-MM-DD`, refreshed on every edit or status change. Equals `created` at creation. The Spec Index "Updated" column mirrors this date.
- `drafter` — who authored the spec; default to the git identity (`git config user.name`).
- `model` — the model that *implemented* the spec. Leave blank during curation; `/spec-monkey:execute-spec` fills it at finalize. Omit, don't guess.
- `tokens`, `cost`, `reasoning_effort` — optional execution metadata, also filled (if at all) at execute time. Leave blank during curation.
- `depends_on` — optional, ordered list of **sibling slice slugs** in the same feature folder this slice needs implemented first (e.g. `['data-model']`). Use bare slugs, not paths. This mirrors this slice's row in `index.md`. `index.md` is authoritative. If they disagree, `index.md` wins. Use an empty list when none exist.

```
---
name: {slice-slug}
summary: {one-line summary of the change}
status: Waiting Implementation
created: {YYYY-MM-DD}
modified: {YYYY-MM-DD}
drafter: {name}
model:
tokens:
cost:
reasoning_effort:
depends_on: []
---

## Why
{1-3 sentences on motivation — the problem today, why it's worth
doing now.}

## Summary
{1-3 sentences on the change itself — intent, not procedure. Why +
Summary together is the reviewer's TLDR.}

## Current behavior
{How the affected part of the system works today, in plain prose, written for someone who has never seen this codebase. Explain the flow and the pieces this change touches. Don't describe the whole module.

Write it as prose a human reads top to bottom, NOT a code-annotated walkthrough. Name things in words ("the persist step," "the write lock," "the classified-record schema") rather than in `symbol()`. Spend a small, deliberate budget of `file:line` anchors. Reserve them for the one or two spots where a reader would otherwise have to grep: the exact function they'll edit, a non-obvious branch. If a sentence reads fine without the citation, drop it. The precise locations already live in "Files that matter." Keep it short: a paragraph or two, not a tour.

Over-cited (avoid): "The worker calls `_persist` (`__main__.py:219`), which builds a `ClassifiedRecord` (`output.py:12`) and, under `_write_lock` via `asyncio.to_thread`, calls `append_record` (`output.py:54`) before appending to `seen.guids`."

Readable (prefer): "When a worker gets a verdict it writes the record, then marks the article seen. This order ensures a crash can never drop an article. The write happens under a single lock and off the event loop. The persist step (`__main__.py:219`) is the function this change edits."}

{Optional domain sections. Add 0+ sections here when a structured artifact aids review and doesn't fit elsewhere.

Examples:
- "Tool definitions" with code blocks for new schemas
- "Two-state implementation" with a markdown state table covering an in-flight dependency
- "Migration plan" with a phased table
- "Contracts" with the exact wire shape (message, event, or request/response schema) when the change produces or consumes data another system reads. Paste the shape or link the authoritative producer/consumer. Don't name the pattern and leave the shape to guesswork. If another repo owns it, say so and pin the source.

Skip entirely if the change is straightforward.}

## Alternatives rejected
{Bulleted. Bold the alternative for scan-readability:
- **{alternative}** — rejected because {reason}.

This prevents the agent from relitigating settled decisions.}

## Edge cases
{Bulleted: "condition: expected behavior". Use a markdown table when the same case has parallel behaviors across multiple domains/callsites: `| Case | Domain A | Domain B |`. Include cases from both Phase 1 and the investigation.

Probe the categories that happy-path specs leak: dependency failures (timeout, partial or malformed response), malformed/oversized input, and empty/boundary values. State each as "condition: expected behavior" so it binds both the code and a test.}

## Assumptions
{State the 2-3 load-bearing assumptions this spec rests on. These are the ones that, if wrong, change the spec. Required: state them even when the user confirmed them. This ensures the reasoning survives after the authoring conversation is cleared. Use one bullet each:
- {load-bearing assumption}; if wrong → {what changes}.

Mark any the user consciously accepted rather than verified with "(accepted by {who})". An open question you could not resolve from the code or the conversation belongs here too, flagged UNRESOLVED.

This is the spec-level list. A constraint that rests on an accepted assumption is *also* pinned inline at its seam in Constraints below.}

## Approach
{The strategy, not the keystrokes. Write so a human reviewer can approve *how* you'll make the change. Describe *what* needs to happen and *why* this direction. Leave *how* to the implementer, who knows the best-practice mechanics for their stack. State the shape of the change and the order of work where order matters. A few sentences for a simple change; a short list of moves for a larger one.

You MAY name a new component this change introduces: a module, a class, a setting. This gives the rest of the spec a shared vocabulary ("add a `DynamoDBWriter`"). You may NOT specify its mechanics: no method signatures, no method bodies, no library-call sequences, no "construct X with config Y, then call Z" recipes. Name the *role* and the *behavior*, not the implementation. Don't restate exact existing symbols or line numbers; those live in Files that matter.

Telling the implementer how to do their job (avoid): "Add `src/.../dynamo.py` exposing a `DynamoDBWriter` built from `Settings`. It constructs a boto3 resource with `Config(retries={...})`, holds the `Table`, and offers `put(record: ClassifiedRecord)` that writes `record.model_dump(mode='json')` via `put_item`, plus a reachability check that calls `table.load()`."

Telling the implementer what we want (prefer): "Add a DynamoDB writer the run builds once and reuses. It has two behaviors: a startup reachability check that fails the run loud before any LLM call if the table, credentials, or region are wrong; and a put that persists a classified record. Wrap its failures in the existing `OutputError` so the abort-all path is unchanged."

Close with **Things to consider**: a brief bulleted list of the non-obvious tradeoffs, gotchas, and decision points the implementer should weigh. These are the spots where a reasonable engineer could pick the wrong path, an interaction that isn't visible from the local code, or a sequencing or compatibility concern. These guide judgment; hard requirements belong in Constraints.

Two cases especially belong here, where one tidy sentence hides expensive work:

- **Implied work.** A constraint assumes a capability the platform or library doesn't actually provide. A scheduled trigger that toggles a resource reads like config. But with no native target it means a new shim component, its permissions, and its tests. Name the shim now (its role may go in the Approach) so it's a planned decision, not a surprise.

- **Overlaid behavior.** A new behavior, schedule, setting, or flag composes with an existing one. Examples: a schedule meeting a missing-data rule, a flag meeting a wrapper. The *combined* outcome ships, and it's rarely the sum a reader assumes. State it, with its boundary and failure case. A weekend-gated alarm over a "treat missing data as breaching" rule is a weekend pager storm unless the spec says otherwise.

If the implementer hits a blocker the reasoning didn't anticipate, they should flag it rather than silently switching approaches.}

---

## Implementation contract

> The sections below are written for the implementing agent. They take
> the Approach above and pin it to specifics: Constraints and Files that
> matter are bullet-dense, identifier-rich, and deliberately redundant
> with each other.

## Constraints
{Bulleted. Use specific numbers, not vague qualifiers. Each must be testable. This deliberately overlaps Files that matter — redundancy is a feature in the implementation contract, not noise.

Scope boundaries live here too. State as a constraint any file, function, or behavior that must NOT change ("don't touch the existing `parse_row` signature").

Where the change touches unbounded data, calls that can hang, concurrency, or untrusted input, pin the decision as a named seam: "stream the download in `fetch.py`, never buffer the whole body"; "5s timeout on the X call, raise on timeout"; "reuse `FooValidator`, don't hand-roll validation". State each constraint as a specific, testable action at a named location. Generic language like "be robust" is not testable — the reviewer flags it as a vague constraint.

If a constraint rests on an assumption the user consciously accepted rather than verified, record it as `ASSUMPTION (accepted by {who}): {claim}; if false, {what changes}`. This keeps the deferred ambiguity visible, not silent.}

## Files that matter
{Index — see Approach for what changes in each. Line numbers anchor the relevant symbols and ranges.

This is one slice. Keep it to a shippable, production-safe PR a single reviewer can hold in their head (~400 changed lines, a handful of files). If the file list outgrows that, the slice is too big: re-slice the feature. Aim for 6-10 files.

Tag every entry: `[modify]` (exists, changes), `[context]` (exists, read only), or `[new]` (this change creates it). The tag does two jobs: it forces you to confirm that something you plan to "add to" exists (or admit it's `[new]`), and it tells the reference linter what to enforce. `[modify]`/`[context]` must exist; `[new]` is exempt.

Single anchor:
- `[modify]` `path/file.ext` — `symbolName()` (`:line`), brief role.
- `[new]` `path/file.ext` — `NewThing`, the role it will play.

Multiple anchors per file:
- `[modify]` `path/file.ext` — `symbolA` (`:N`), `symbolB` (`:M`); module docstring (`:start-end`).}

## Verification
{Open with the exact setup-and-run sequence, not just the test command. State any step needed to run the suite from a clean checkout: a dependency install (including the optional groups/extras the tests need — the full install, not the minimal one), a service start, an env var, then the command itself. A command that fails on a missing extra burns the implementer's baseline run.

Then list what to test as a plain-English bulleted checklist. One behavior per bullet, each naming its expected output. Group with bold subheaders when verification spans multiple surfaces.

Two styles, by audience:

- **User-facing behavior** — write as Given/When/Then so a test drops straight out of it: "Given [state], when [action], then [observable outcome]."
- **Everything else** (internal functions, data shapes, error paths) — plain "what we test → expected result" bullets: "store a record with no url → it reads back as null"; "put the same id twice → one item, latest value wins." Don't name the test function or assertion API. State what must be true and let the implementer write the check, *except at a seam* (see below), where naming the mechanism is the whole point.

Cover at least one error/failure path wherever the change touches I/O or untrusted input. Keep every bullet readable. Describe the behavior, not the code that verifies it.

When the change needs new tests, name the existing test file whose **structure** they should mirror. This is the project's established style: fixture conventions, real-dependency vs. mocked. The implementer copies the shape instead of grepping for it. That's structure, not the assertion API. Still state what must be true, not how to assert it.

**Seams to make concrete.** Most criteria stay properties. A few don't: where the property hides a collision that surfaces only once it becomes code, name the *mechanism*, not just the property. An aspirational test criterion inherits none of the production contract's reliability.

- **Criterion × test library** — an assertion the obvious test double can't express. A mock that only raises ordinary errors can't inject the cancellation/interrupt signal you need to assert. Name the limit and how the test produces the behavior instead.
- **New shape × existing helper** — "reuse helper X" where X's design doesn't cover the new behavior. A mock built for sequential calls vs. concurrent ones. Say reuse, extend, or replace; "reuse" alone is direction, not specification.
- **Criterion × criterion** — two criteria that can't both hold once mechanized. A hygiene grep for a token "returns nothing" vs. a test that asserts the token's absence, whose own code contains it for the grep to find. Reconcile them; don't ship the contradiction.

**Manual sanity check (not a test):** {any non-automated check — deploys, integration runs, dashboards — explicitly called out as not-a-test.}}

Keep going until all tests pass and the verification criteria are met. If you hit a problem, investigate and fix it rather than stopping. If you discover the spec is wrong (a constraint can't be met as stated, a referenced file doesn't exist, a rejected alternative now looks correct), surface it before working around it. Don't silently change the approach.
```
