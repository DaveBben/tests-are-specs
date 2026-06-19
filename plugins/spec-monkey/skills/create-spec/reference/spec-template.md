# Spec Template

Read this when producing the spec in Phase 2. The implementing agent (`/spec-monkey:execute-spec`) consumes the result — fill every section with the precision the placeholders describe.

This fills ONE slice file (`{slice}.md`) in `docs/specs/features/{slug}/`, alongside an `_index.md` (see `index-template.md`). Each slice is self-contained; execute-spec runs one per call as one PR, sized to ship on its own (~400 changed lines, one reviewer in a sitting).

The spec serves two audiences in one document:

- **Above the "Implementation contract" divider** — Why, Summary, Current behavior, Alternatives, Edge cases, Assumptions, Approach. Everything a human reviewer needs to approve *how* the change is made. The Approach is the hinge: the strategy the reviewer signs off and the implementer executes.
- **Below the divider** — the binding contract that pins that strategy to specifics. Constraints, Files that matter, and Verification are deliberately redundant with each other; the redundancy survives context compaction during a long implementation. Keep it.

**Writing style.** The prose sections (Why, Summary, Current behavior, Approach, Things to consider, Edge-case descriptions) follow `writing-style.md`: one idea per sentence, actor-first, conclusion first, caveats in their own sentence. The contract sections below the divider are exempt — there, identifier density and redundancy are load-bearing.

**Front-matter.** Every spec opens with a YAML block (`---` fences); a deterministic linter validates it.

- `schema` — always `v2`.
- `name` — the slice slug = filename without `.md` (e.g. `data-model`). Matches this slice's `_index.md` row.
- `summary` — one scannable line; what execute-spec's menu shows. Quote it if it contains a colon.
- `status` — `Waiting Implementation` | `Implemented` | `Superseded` | `Deprecated` | `Needs Revision`. New specs start at `Waiting Implementation`.
- `created` — `YYYY-MM-DD`, set once, never changes.
- `modified` — `YYYY-MM-DD`, refreshed on every edit or status change; equals `created` at creation. The Spec Index "Updated" column mirrors it.
- `drafter` — author; default to `git config user.name`.
- `execution` — run metadata for the execute-spec run, recorded afterward (an agent can't self-measure). Leave blank during curation. When filled: `total_cost`, `total_duration`, `usage_by_models` (one entry per model: `model`, `input`, `output`, `cache_read`, `cache_write`, `cost`).
- `depends_on` — ordered list of **sibling slice slugs** this slice needs first (bare slugs, not paths), e.g. `['data-model']`. Mirrors `_index.md`, which wins on disagreement. Empty list when none.

```
---
schema: v2
name: {slice-slug}
summary: {one-line summary of the change}
status: Waiting Implementation
created: {YYYY-MM-DD}
modified: {YYYY-MM-DD}
drafter: {name}
execution:
  total_cost:
  total_duration:
  usage_by_models:
depends_on: []
---

## Why
{1-3 sentences on motivation — the problem today, why it's worth
doing now.}

## Summary
{1-3 sentences on the change itself — intent, not procedure. Why +
Summary together is the reviewer's TLDR.}

## Current behavior
{How the affected part of the system works today, in plain prose for someone who has never seen this codebase. Explain the flow and the pieces this change touches — not the whole module.

Prose a human reads top to bottom, NOT a code-annotated walkthrough. Name things in words ("the persist step," "the write lock") rather than `symbol()`. Spend a small budget of `file:line` anchors — reserve them for the one or two spots a reader would otherwise grep (the function they'll edit, a non-obvious branch). The precise locations already live in "Files that matter." A paragraph or two, not a tour.

Over-cited (avoid): "The worker calls `_persist` (`__main__.py:219`), which builds a `ClassifiedRecord` (`output.py:12`) and, under `_write_lock` via `asyncio.to_thread`, calls `append_record` (`output.py:54`)."

Readable (prefer): "When a worker gets a verdict it writes the record, then marks the article seen — so a crash can never drop an article. The write happens under a single lock, off the event loop. The persist step (`__main__.py:219`) is the function this change edits."}

{Optional domain sections. Add when a structured artifact aids review and fits nowhere else: a "Contracts" block with the exact wire shape (paste it or link the producer/consumer) when the change produces or consumes data another system reads; a state table for an in-flight dependency; a phased migration table. Skip if the change is straightforward.}

## Alternatives rejected
{Bulleted. Bold the alternative for scan-readability:
- **{alternative}** — rejected because {reason}.

This prevents the agent from relitigating settled decisions.}

## Edge cases
{Bulleted: "condition: expected behavior". Use a markdown table when the same case has parallel behaviors across domains/callsites: `| Case | Domain A | Domain B |`. Include cases from both Phase 1 and the investigation.

Probe the categories happy-path specs leak: dependency failures (timeout, partial or malformed response), malformed/oversized input, empty/boundary values. State each as "condition: expected behavior" so it binds both the code and a test.}

## Assumptions
{State the 2-3 load-bearing assumptions this spec rests on — the ones that, if wrong, change the spec. State them even when the user confirmed them, so the reasoning survives after the authoring conversation is cleared. One bullet each:
- {load-bearing assumption}; if wrong → {what changes}.

Mark any the user accepted rather than verified with "(accepted by {who})". An open question you couldn't resolve belongs here too, flagged UNRESOLVED. A constraint resting on an accepted assumption is *also* pinned inline at its seam in Constraints.}

## Approach
{The strategy, not the keystrokes. Write so a reviewer can approve *how* you'll make the change: what needs to happen and why this direction. Leave *how* to the implementer. State the shape of the change, and the order where order matters. A few sentences for a simple change; a short list of moves for a larger one.

You MAY name a new component (a module, class, setting) for shared vocabulary ("add a `DynamoDBWriter`"). You may NOT specify its mechanics — no signatures, method bodies, or call sequences. Name the *role* and *behavior*, not the implementation. Exact existing symbols and line numbers live in Files that matter.

How (avoid): "Add `dynamo.py` exposing `DynamoDBWriter` built from `Settings`; construct a boto3 resource with `Config(retries={...})`, offer `put(record)` that writes `record.model_dump(mode='json')` via `put_item`."

What (prefer): "Add a DynamoDB writer the run builds once and reuses, with two behaviors: a startup reachability check that fails loud before any LLM call if the table, credentials, or region are wrong; and a put that persists a classified record. Wrap failures in the existing `OutputError` so the abort path is unchanged."

Close with **Things to consider**: a brief bulleted list of the non-obvious tradeoffs, gotchas, and decision points — spots where a reasonable engineer could pick the wrong path, an interaction invisible from local code, a sequencing or compatibility concern. These guide judgment; hard requirements belong in Constraints. Two especially belong here, where one tidy sentence hides expensive work:

- **Implied work.** A constraint assumes a capability the platform or library doesn't provide. A scheduled trigger reads like config, but with no native target it means a new shim component, its permissions, and its tests. Name the shim now so it's planned, not a surprise.
- **Overlaid behavior.** A new behavior, schedule, setting, or flag composes with an existing one, and the combined outcome is rarely the sum a reader assumes. State it, with its boundary and failure case. A weekend-gated alarm over a "treat missing data as breaching" rule is a weekend pager storm unless the spec says otherwise.

If the implementer hits a blocker the reasoning didn't anticipate, they flag it rather than silently switching approaches.}

---

## Implementation contract

> Written for the implementing agent: these take the Approach above and pin
> it to specifics. Constraints and Files that matter are bullet-dense,
> identifier-rich, and deliberately redundant with each other.

## Constraints
{Bulleted, specific numbers not vague qualifiers, each testable. Deliberately overlaps Files that matter — redundancy is a feature in the contract, not noise.

Scope boundaries live here too: state as a constraint anything that must NOT change ("don't touch the existing `parse_row` signature").

Where the change touches unbounded data, calls that can hang, concurrency, or untrusted input, pin the decision as a named seam: "stream the download in `fetch.py`, never buffer the whole body"; "5s timeout on the X call, raise on timeout"; "reuse `FooValidator`, don't hand-roll validation". Each constraint is a specific, testable action at a named location — "be robust" isn't testable, and the reviewer flags it.

If a constraint rests on an accepted-not-verified assumption, record it as `ASSUMPTION (accepted by {who}): {claim}; if false, {what changes}`.}

## Files that matter
{Index — see Approach for what changes in each. The implementer reads by these anchors alone and does not open the whole file, so each is load-bearing: anchor precisely enough that the cited symbol plus the lines around it is all they need. A vague or stale anchor forces a full re-read — the cost this section exists to prevent.

Sum the `estimated lines` across New + Modified + Removed: above ~400, the slice is too big — re-slice. Aim for 6-10 files.

Group every entry by what the change does to the file. The heading is the contract the reference linter enforces: **New** must NOT already exist; **Modified**, **Removed**, and **Context** must. Tag each changed entry with `estimated lines`. For a file you **rewrite, replace, or delete wholesale, the estimate is its real current line count** — look it up, don't guess; that's the number a one-word "rewrite" hides. **Context** is read-only, so no estimate. Deleting symbols from a surviving file is **Modified**; **Removed** is a whole file that ceases to exist.

### New — file this change creates
- `path/file.ext` — `NewThing`, the role it will play. estimated lines: ~N

### Modified — exists, changes (includes deleting symbols from a surviving file)
- `path/file.ext` — `symbolA` (`:N`), `symbolB` (`:M`); module docstring (`:start-end`). estimated lines: ~N

### Removed — entire file deleted
- `path/file.ext` — the role it played, why it goes. estimated lines: ~N (file size)

### Context — exists, read-only; read to orient, do NOT change
- `path/file.ext` — `symbolName()` (`:line`), why it's relevant. (read-only)}

## Verification
{Open with the exact setup-and-run sequence, not just the test command: any dependency install (with the optional groups/extras the tests need — the full install, not the minimal one), a service start, or an env var, then the command. A command that fails on a missing extra burns the implementer's baseline run.

Then a plain-English checklist — one behavior per bullet, each naming its expected output. Bold subheaders when verification spans multiple surfaces. Two styles:

- **User-facing behavior** — Given/When/Then so a test drops straight out: "Given [state], when [action], then [observable outcome]."
- **Everything else** (internal functions, data shapes, error paths) — "what we test → expected result": "store a record with no url → reads back as null"; "put the same id twice → one item, latest wins." State what must be true; let the implementer write the check.

Cover at least one error/failure path wherever the change touches I/O or untrusted input. When the change needs new tests, name the existing test file whose **structure** they should mirror (fixture conventions, real-dependency vs. mocked) — the implementer copies the shape, not the assertion API.

**Seams to make concrete.** Most criteria stay properties. Where a property hides a collision that surfaces only once it becomes code, name the *mechanism*, not just the property:

- **Criterion × test library** — an assertion the obvious test double can't express (a mock that only raises ordinary errors can't inject the cancellation/interrupt signal). Name the limit and how the test produces the behavior instead.
- **New shape × existing helper** — "reuse helper X" where X's design doesn't cover the new behavior (a mock built for sequential calls vs. concurrent ones). Say reuse, extend, or replace.
- **Criterion × criterion** — two criteria that can't both hold once mechanized (a hygiene grep that "returns nothing" vs. a test whose own code contains the token the grep finds). Reconcile them; don't ship the contradiction.

**Manual sanity check (not a test):** {any non-automated check — deploys, integration runs, dashboards — explicitly called out as not-a-test.}}

Keep going until all tests pass and the verification criteria are met. Hit a problem → investigate and fix, don't stop. Discover the spec is wrong (a constraint can't be met as stated, a referenced file is gone, a rejected alternative now looks right) → surface it before working around it; don't silently change the approach.
```
