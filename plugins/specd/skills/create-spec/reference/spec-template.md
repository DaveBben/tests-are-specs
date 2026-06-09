# Spec Template

Read this when producing the spec in Phase 2. The implementing agent
(`/specd:execute-spec`) consumes the result, so fill every section with the
precision described in the placeholders.

The spec serves two audiences with one document. Above the
"Implementation contract" divider: motivation, summary, current
state, alternatives, edge cases — what a human reviewer needs to
approve the approach. Below: the binding contract for the
implementing agent — Approach gives the direction; Constraints, Do
NOT, Files, and Verification pin the specifics, deliberately redundant
with each other.

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
flow and the pieces this change touches — not the whole module. Cite a
`symbol()` or `file:line` only where it genuinely saves a human a
search (the one function they'll edit, a non-obvious branch); don't
annotate prose that reads fine without it. Keep it short — a paragraph
or two, not a tour.}

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

---

## Implementation contract

> The sections below are written for the implementing agent. Approach
> gives the direction in prose and leaves the mechanics to the
> implementer; Constraints, Do NOT, and Files that matter are
> bullet-dense, identifier-rich, and deliberately redundant with each
> other.

## Approach
{The strategy, not the keystrokes. Describe *what* needs to happen and
*why* this direction — enough for a capable implementer to act on, but
leave *how* to them; they know the best-practice mechanics for their
stack. State the shape of the change and the order of work where order
matters. Don't prescribe exact symbols, signatures, or line numbers —
those live in Files that matter; naming them here just creates two
places to keep in sync. A few sentences for a simple change; a short
list of moves for a larger one.

Close with **Things to consider** — a brief bulleted list of the
non-obvious tradeoffs, gotchas, and decision points the implementer
should weigh: the spots where a reasonable engineer could pick the
wrong path, an interaction that isn't visible from the local code, a
sequencing or compatibility concern. These guide judgment; hard
requirements belong in Constraints.

If the implementer hits a blocker the reasoning didn't anticipate, they
should flag it rather than silently switching approaches.}

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
{Exact command to run, then specific assertions. Group with bold
subheaders when verification covers multiple surfaces:

**{Surface — symbol or feature name}**
- {assertion: expected input → expected output}
- {assertion}

**{Other surface}**
- {assertion}

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
