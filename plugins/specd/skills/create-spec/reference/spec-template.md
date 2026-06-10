# Spec Template

Read this when producing the spec in Phase 2. The implementing agent
(`/specd:execute-spec`) consumes the result, so fill every section with the
precision described in the placeholders.

The spec serves two audiences with one document. Above the
"Implementation contract" divider: motivation, summary, current state,
alternatives, edge cases, and the Approach — everything a human
reviewer needs to understand and approve *how* the change will be made.
The Approach is the hinge: prose strategy the reviewer signs off on and
the direction the implementer then executes. Below the divider: the
binding contract that pins that strategy to specifics — Constraints, Do
NOT, Files, and Verification, deliberately redundant with each other.

```
{One-line summary of the change}

**Status**: Waiting Implementation
**Last updated**: {YYYY-MM-DD}

## Why
{1-3 sentences on motivation — the problem today, why it's worth
doing now.}

## Summary
{1-3 sentences on the change itself — intent, not procedure. Why +
Summary together is the reviewer's TLDR.}

## Current behavior
{How the affected part of the system works today, in plain prose,
written for someone who has never seen this codebase. Explain the
flow and the pieces this change touches — not the whole module.

Write it as prose a human reads top to bottom, NOT a code-annotated
walkthrough. Default to naming things in words ("the persist step,"
"the write lock," "the classified-record schema") rather than
`symbol()`. Spend a small, deliberate budget of `file:line` anchors —
a handful across the whole section, reserved for the one or two spots
where a reader would otherwise have to grep (the exact function they'll
edit, a non-obvious branch). If a sentence reads fine without the
citation, drop it; the precise locations already live in "Files that
matter." Keep it short — a paragraph or two, not a tour.

Over-cited (avoid): "The worker calls `_persist` (`__main__.py:219`),
which builds a `ClassifiedRecord` (`output.py:12`) and, under
`_write_lock` via `asyncio.to_thread`, calls `append_record`
(`output.py:54`) before appending to `seen.guids`."
Readable (prefer): "When a worker gets a verdict it writes the record,
then marks the article seen — in that order, so a crash can never drop
an article. The write happens under a single lock and off the event
loop. The persist step (`__main__.py:219`) is the function this change
edits."}

{Optional domain sections — add 0+ sections here when a structured
artifact aids review and doesn't fit elsewhere. Examples:
- "Tool definitions" with code blocks for new schemas
- "Two-state implementation" with a markdown state table covering
  an in-flight dependency
- "Migration plan" with a phased table
Skip entirely if the change is straightforward.}

## Alternatives rejected
{Bulleted. Bold the alternative for scan-readability:
- **{alternative}** — rejected because {reason}.
Prevents the agent from relitigating settled decisions.}

## Edge cases
{Bulleted: "condition: expected behavior". Use a markdown table
when the same case has parallel behaviors across multiple
domains/callsites: `| Case | Domain A | Domain B |`. Include cases
from both Phase 1 and the investigation. Probe the categories
happy-path specs leak: dependency failures (timeout, partial or
malformed response), malformed/oversized input, and empty/boundary
values — each as "condition: expected behavior" so it binds both the
code and a test.}

## Approach
{The strategy, not the keystrokes — written so a human reviewer can
approve *how* you'll make the change. Describe *what* needs to happen
and *why* this direction; leave *how* to the implementer, who knows the
best-practice mechanics for their stack. State the shape of the change
and the order of work where order matters. A few sentences for a simple
change; a short list of moves for a larger one.

You MAY name a new component this change introduces — a module, a
class, a setting — so the rest of the spec shares a vocabulary ("add a
`DynamoDBWriter`"). You may NOT specify its mechanics: no method
signatures, no method bodies, no library-call sequences, no "construct
X with config Y, then call Z" recipes. Name the *role* and the
*behavior*, not the implementation. Don't restate exact existing
symbols or line numbers either — those live in Files that matter.

Telling the implementer how to do their job (avoid): "Add
`src/.../dynamo.py` exposing a `DynamoDBWriter` built from `Settings`.
It constructs a boto3 resource with `Config(retries={...})`, holds the
`Table`, and offers `put(record: ClassifiedRecord)` that writes
`record.model_dump(mode='json')` via `put_item`, plus a reachability
check that calls `table.load()`."
Telling the implementer what we want (prefer): "Add a DynamoDB writer
the run builds once and reuses, with two behaviors: a startup
reachability check that fails the run loud — before any LLM call — if
the table, credentials, or region are wrong; and a put that persists a
classified record. Wrap its failures in the existing `OutputError` so
the abort-all path is unchanged."

Close with **Things to consider** — a brief bulleted list of the
non-obvious tradeoffs, gotchas, and decision points the implementer
should weigh: the spots where a reasonable engineer could pick the
wrong path, an interaction that isn't visible from the local code, a
sequencing or compatibility concern. These guide judgment; hard
requirements belong in Constraints.

If the implementer hits a blocker the reasoning didn't anticipate, they
should flag it rather than silently switching approaches.}

---

## Implementation contract

> The sections below are written for the implementing agent. They take
> the Approach above and pin it to specifics: Constraints, Do NOT, and
> Files that matter are bullet-dense, identifier-rich, and deliberately
> redundant with each other.

## Constraints
{Bulleted. Specific numbers, not vague qualifiers. Each testable.
Deliberately overlaps Do NOT and Files that matter — redundancy is
a feature in the implementation contract, not noise. Where the change
touches unbounded data, calls that can hang, concurrency, or untrusted
input, pin the decision as a named seam — "stream the download in
`fetch.py`, never buffer the whole body"; "5s timeout on the X call,
raise on timeout"; "reuse `FooValidator`, don't hand-roll validation"
— never a generic "be robust" (the reviewer will flag that as a vague
constraint). If a constraint rests on an assumption the user
consciously accepted rather than verified, record it as `ASSUMPTION
(accepted by {who}): {claim}; if false, {what changes}` so the deferred
ambiguity is visible, not silent.}

## Do NOT
{Bulleted. Explicit scope boundaries. Name specific files,
functions, or behaviors that must NOT change.}

## Files that matter
{Index — see Approach for what changes in each. Line numbers anchor
the relevant symbols and ranges. 6-10 files. Single anchor:
- `path/file.ext` — `symbolName()` (`:line`), brief role.
Multiple anchors per file:
- `path/file.ext` — `symbolA` (`:N`), `symbolB` (`:M`); module
  docstring (`:start-end`).}

## Verification
{Open with the exact command to run (`uv run pytest`, etc.). Then list
what to test as a plain-English bulleted checklist — one behavior per
bullet, each naming its expected output. Group with bold subheaders
when verification spans multiple surfaces. Two styles, by audience:

- **User-facing behavior** — write as Given/When/Then so a test drops
  straight out of it: "Given [state], when [action], then [observable
  outcome]."
- **Everything else** (internal functions, data shapes, error paths) —
  plain "what we test → expected result" bullets: "store a record with
  no url → it reads back as null"; "put the same id twice → one item,
  latest value wins." Don't name the test function or assertion API;
  state what must be true and let the implementer write the check.

Cover at least one error/failure path wherever the change touches I/O
or untrusted input. Keep every bullet readable — describe the behavior,
not the code that verifies it.

**Manual sanity check (not a test):** {any non-automated check —
deploys, integration runs, dashboards — explicitly called out as
not-a-test.}}

Keep going until all tests pass and the verification criteria are
met. If you hit a problem, investigate and fix it rather than
stopping. If you discover the spec is wrong (a constraint can't be
met as stated, a referenced file doesn't exist, a rejected
alternative now looks correct), surface it before working around it
— don't silently change the approach.
```
