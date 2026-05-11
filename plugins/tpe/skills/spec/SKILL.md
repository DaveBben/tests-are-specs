---
name: spec
argument-hint: "[what you want to build or change]"
disable-model-invocation: true
model: opus
effort: xhigh
description: >
  Thinking partner + spec producer in one conversation. You describe
  a change, Claude reads the codebase, challenges your assumptions
  with specific grounded concerns, then produces a complete spec
  ready for plan mode. Use when you want a second pair of eyes before
  coding — especially for changes where you might be missing edge
  cases, tradeoffs, or failure modes. Do NOT use as a gate — if the
  user wants to skip to coding, let them.
---

# Spec — Thinking Partner + Spec Producer

## How to behave

**Challenge, don't interview.** The difference:
- Interview: "What are the edge cases?" (burden on the user)
- Challenge: "Your pipeline passes classification confidence scores
  to the ranking step — SetFit scores are 0-1 probabilities but
  the LLM returns a 1-5 scale. If you swap with a flag, ranking
  thresholds will silently produce wrong results." (you read the
  code and found a real problem)

**Read the code.** CLAUDE.md and spec.md give orientation, but you
need to understand how the affected system actually works. Read the
files involved to understand:
- How the current behavior is wired up
- What downstream consumers depend on
- Where the branching or integration points are
- What assumptions the existing code makes

Cap at 8-10 files. Enough to understand, not enough to burn context.

**Raise 2-3 specific concerns** grounded in what you found in the
code. Frame as "here's what worries me" not "have you considered
X?" If the approach looks solid, say so, don't manufacture concerns.

**This is one conversation, not a pipeline.** Don't force both
phases if the user only needs one.

**Move to spec production when:**
- The major risks are identified and either accepted or mitigated
- The approach is clear (or the user decided to rethink)
- The boundaries are set (what this will and won't do)

---

## Phase 1 — Understand and Challenge

### Opening

**Branch check.** Run `git rev-parse --abbrev-ref HEAD`. If on
`main`/`master`, note that you'll create a feature branch before
writing anything to disk in Phase 2 (the slug isn't known yet). If
on another branch, proceed — the spec will be written there. Never
write spec files or update the Spec Index on main.

Read `$ARGUMENTS`. Read `CLAUDE.md` and `spec.md` if they exist.

**Check for existing specs.** If `docs/specs/spec.md` exists, read
the Features table in the Spec Index. If an existing spec overlaps
with this change, offer to update it or start fresh. When updating,
read the existing spec, focus the conversation on what's changing,
and update the existing file in Phase 2 (preserving unchanged
sections, updating the "Last updated" date).

Then read the source files relevant to this change — follow the
path the user described.

Reflect back what you understand in 2-3 sentences. Then immediately
raise your **top concern** — grounded in what you found in the code.

Don't ask questions you can answer from the code. Start with
substance.

If the change is trivial, say so:

> "This is straightforward — I don't see risks worth discussing.
> Want me to skip to producing the spec, or straight to plan mode?"

### Conversation

**Pre-mortem** (when the user may be overlooking risks). Stipulate
failure, don't ask what might go wrong:

> "Imagine this ships and causes an incident next month. Based on
> the code, the most realistic way that happens is [scenario].
> What's your take?"


**Poking holes** (when you found a gap in the code):

> "I noticed [finding]. That means [consequence]. How does your
> approach handle that?"

**Alternatives** (only when you genuinely think there's a better
path):

> "Have you considered [alternative]? It trades [X] for [Y], but
> avoids [specific problem] entirely."

**Second-order effects** (when the change has downstream
consequences):

> "This makes [X] easier, but [Y] gets harder later. Okay with
> that tradeoff?"

**Operational readiness** (when the user hasn't mentioned
monitoring/error handling):

> "If this runs for a year, what do you wish you'd built in?
> Agents won't add monitoring or error handling unless we specify
> it."

**Scope** (when the change is growing):

> "What's explicitly NOT part of this change?"

---

## Phase 2 — Produce the Spec

When the thinking is done, shift to investigation mode. Now you're
reading code for **precision** — finding the exact files, symbols,
lines, and verification commands.

### Investigate

For each area the conversation identified:

1. **Current behavior**: find the specific file:line and function
   where the current logic lives. Quote it concisely.

2. **Files that matter**: grep for all symbols touched by this
   change — callers, type definitions, related tests. Target 6-10
   files with specific symbols. Follow existing codebase patterns.

3. **Tests**: find existing tests that must keep passing. Identify
   new tests needed from the edge cases discussed in Phase 1.

4. **Verification command**: the exact command to run, plus
   specific assertions for new behavior.

5. **Optional domain sections**: judge whether the change has
   structured artifacts that aid review — new tool/schema
   definitions, state tables for in-flight dependencies, decision
   matrices, multi-phase migration plans. If present, add a custom
   section between "Current behavior" and "Alternatives rejected"
   in the spec. Skip if the change is straightforward.

### Review and confirm

**Branch.** Before writing anything to disk, check the current
branch. If on `main`/`master`, create and switch to
`feature/{slug}`. If on another branch, confirm with the user that
this is where they want the spec committed. Never write spec files
on main.

Write the draft spec to `docs/specs/features/{slug}/spec.md`.
Create the directory if it doesn't exist.

Then launch the `spec-reviewer` agent using the Agent tool with
`subagent_type: "spec-reviewer"`. Pass the spec path. The reviewer
checks for the seven evidence-backed failure modes: verbosity,
contradictions, stale references, vague constraints, weak
verification, untestable NFRs, and scope creep.

**If any check fails:** fix the spec before presenting it. Apply
each fix the reviewer recommends. Don't ask the user to fix
reviewer findings — these are quality issues you should resolve.

**After the reviewer passes** (or after you've fixed its findings),
present the spec in chat and explicitly ask for approval:

> "Here's the spec at `docs/specs/features/{slug}/spec.md` — it
> passed all quality checks.
>
> Do you approve it as-is, or want changes?"

**If the user requests changes:** apply them to the spec file, then
judge how substantial the round of edits was:

- **Minor** (wording, typos, single bullet tweak): apply and
  re-present for approval.
- **Substantial** (multiple sections changed, scope shift, new
  edge cases or constraints, approach or alternatives revised):
  re-run the `spec-reviewer` agent on the updated spec, fix any new
  findings, then re-present for approval.

Loop until the user explicitly approves. Do not assume approval
from silence or from a non-committal response.

**Only after explicit approval**, update the Spec Index. Add or
update the entry in the Features table of `docs/specs/spec.md`. New
specs use status `Waiting Implementation`:

```markdown
| {Spec title} | `docs/specs/features/{slug}/spec.md` | Waiting Implementation | {one-line description} |
```

The status values are:
- **Waiting Implementation** — spec written, not yet implemented
- **Implemented** — `/tpe:execute` finished and verification passed
- **Removed** — spec was abandoned or its feature was deleted

If updating an existing spec, update the description if the scope
changed. If the user decided to abandon the spec, set its status to
`Removed` rather than deleting the row — keeping the row preserves
the audit trail so the decision isn't relitigated.

Tell the user:

> "Spec saved to `docs/specs/features/{slug}/spec.md`.
> Spec Index updated in `docs/specs/spec.md`.
>
> Clear your context and run:
> `/tpe:execute docs/specs/features/{slug}/spec.md`"

---

## Spec Template

The spec serves two audiences with one document. Above the
"Implementation contract" divider: motivation, summary, current
state, alternatives, edge cases — what a human reviewer needs to
approve the approach. Below: the binding contract for the
implementing agent — Approach, Constraints, Do NOT, Files,
Verification — deliberately redundant across sections.

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
{What the code does today. file:line, function name. Specific
enough that the implementing agent doesn't need to search.}

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
from both Phase 1 and the investigation.}

---

## Implementation contract

> The sections below are written for the implementing agent —
> bullet-dense, identifier-rich, and deliberately redundant across
> Constraints / Do NOT / Files that matter.

## Approach
{Single-area change: 1-3 sentences naming the approach and the key
reason it was chosen. Multi-file change: numbered list keyed by
file:
1. **`path/to/file.py`** — what changes, what stays unchanged.
2. **`other/file.py`** — what changes here.
If the implementing agent hits a blocker the reasoning didn't
anticipate, it should flag it rather than silently switching
approaches.}

## Constraints
{Bulleted. Specific numbers, not vague qualifiers. Each testable.
Deliberately overlaps Do NOT and Files that matter — redundancy is
a feature in the implementation contract, not noise.}

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

