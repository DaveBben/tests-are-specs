---
name: create-spec
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

**Challenge, don't interview.** Put the burden on yourself, not the
user — read the code, find the real problem, bring it.
- Interview: "What are the edge cases?" (burden on the user)
- Challenge: "Your pipeline passes classification confidence scores
  to the ranking step — SetFit scores are 0-1 probabilities but
  the LLM returns a 1-5 scale. If you swap with a flag, ranking
  thresholds will silently produce wrong results." (you read the
  code and found a real problem)

A grounded challenge takes a few shapes — reach for whichever fits:
- **Name the finding, then the consequence**: "I noticed [finding].
  That means [consequence]. How does your approach handle that?"
- **Stipulate the failure** instead of asking what might go wrong:
  "Imagine this ships and causes an incident next month. Based on the
  code, the most realistic way that happens is [scenario]."
- **Frame the tradeoff** when the change has downstream cost: "This
  makes [X] easier, but [Y] gets harder later. Okay with that?"
- **Offer a concrete alternative** only when you genuinely have a
  better path: "[alternative] trades [X] for [Y] but avoids [problem]
  entirely."

Always "here's what worries me," never "have you considered X?"

**Read the code.** CLAUDE.md, Agents.md and spec.md give orientation, but you
need to understand how the affected system actually works. Read the
files involved to understand:
- How the current behavior is wired up
- What downstream consumers depend on
- Where the branching or integration points are
- What assumptions the existing code makes

Stop once you have a thorough understanding — and put a ceiling on the
search. Failing runs are marked by endless file-reading with no signal
to abandon exploration. If you've read more than ~15 files and still
can't articulate the current behavior, treat that as the signal to
stop: say what remains unclear and ask, rather than reading further.
Dispatch broad greps and fan-out searches to subagents (e.g. the
`Explore` agent) so raw exploration noise stays out of the context the
spec gets written in.

**Surface every ambiguity that materially changes the design** —
grounded in what you found in the code. Usually that's 2-3 concerns,
but a genuinely ambiguous change has more; don't drop a material one to
hit a number, or pad a clear change to reach one. If the approach looks
solid, say so, don't manufacture concerns.

**This is one conversation, not a pipeline.** Don't force both
phases if the user only needs one.

**Only move to spec production when all of the following are true:**
- All major risks are identified and either accepted or mitigated
- The approach is clear and offers little to no ambiguity
- The boundaries are set (what this will and won't do)

---

## Phase 1 — Understand and Challenge

### Opening

**Branch check.** Run `git rev-parse --abbrev-ref HEAD`. If on
`main`/`master`, note that you'll create a spec branch before
writing anything to disk in Phase 2 (the slug isn't known yet). If
on another branch, proceed — the spec will be written there. Never
write spec files or update the Spec Index on main.

Read `$ARGUMENTS`. Read `CLAUDE.md`, `AGENTS.md` and `spec.md` if they exist.

**Check for existing specs.** If `docs/specs/spec.md` exists, read
the Features table in the Spec Index. If the requested change
**closely matches an existing spec**, stop and ask the user whether
they want to **modify that spec** or **create a new one** — don't
decide for them.

- **Modify**: read the existing spec and use its current content as
  the starting point for the new version. Focus the conversation on
  what's changing, and update the existing file in Phase 2
  (preserving unchanged sections, updating the "Last updated" date).
- **Create new**: proceed with a fresh spec as normal.

Then read the source files relevant to this change — follow the
path the user described.

Reflect back what you understand in 2-3 sentences. Then immediately
raise your **top concerns** — grounded in what you found in the code. 
Before continuing, allow the user to reply back their own response to your top concerns.

Don't ask questions you can answer from the code. Start with
substance.

If the change is trivial, say so:

> "This is straightforward — I don't see risks worth discussing.
> Want me to skip to producing the spec, or straight to plan mode?"

### Conversation

The shapes above are *how* you raise a concern. These are the
*dimensions* worth raising — probe each when it applies:

**Intent & acceptance** (first — ask exactly what the code can't tell
you: the intent and the definition of done):

> "The code can't tell me the intent here. What's the rule — the
> target (precision/recall, a latency budget), the business rule,
> which goal wins when two conflict, who consumes the output? And how
> will we *know* it's correct — what observable signal (a number, a
> behavior, a threshold) separates done from not-done?"

Where the bar is a user-observable behavior, pin it as Given/When/Then
("given [state], when [action], then [measurable outcome]") so a test
can be written from it directly.

**Operational readiness** (when the change touches I/O, external
services, concurrency, or unbounded data):

> "If this runs for a year against real conditions, what do you wish
> you'd built in? Implementing agents default to the happy path —
> they won't stream an unbounded input, time out a hanging call,
> scope a thread pool, or fail loudly on bad data unless the spec
> names the seam. Which inputs here are unbounded, which calls can
> hang, and what should happen when they do?"


**Trust boundaries** (when the change ingests data from an external
or untrusted source — network responses, fetched/uploaded files,
third-party APIs, user input):

> "Where does untrusted data enter here, and what boundary does it
> cross before it's trusted? Name the concrete threat — injection,
> a malicious or oversized payload, an SSRF/path target, a secret
> that could leak into logs or output — and what the code must do at
> that seam. 'Validate the input' isn't an answer: which input,
> checked against what, and what happens when the check fails?"

Security requirements that come out of this are constraints, not
afterthoughts — pin them at the `file:line` seam in Constraints, the
same as any other (e.g. "reject non-`https` URLs in `fetch.py` before
the request"). Silence here is the happy-path default the implementing
agent will otherwise take.

**Scope** (when the change is growing):

> "What's explicitly NOT part of this change?"

---

## Phase 2 — Produce the Spec

### Engineering principles

The approach, constraints, and alternatives you write must respect these
principles . Apply them as you shape the spec:

- **Verify, don't predict.** Every import, package, and API method must
  exist in the version this project pins — check the lockfile or
  installed source before using it.
- **Fail loud.** Catch only the specific exceptions the code can raise;
  never catch base exception classes; never ship a stub that fakes
  success. Both hide brokenness behind plausible-looking success.
- **Match this codebase.** Before writing anything new, find how this
  project already solves similar problems and follow that pattern;
  consolidate near-duplicates instead of adding parallel
  implementations.
- **Least code that works.** No speculative abstractions, no indirection
  for single callers, stdlib over hand-rolling; delete dead code
  outright
- **Test real behavior.** Realistic inputs through real libraries,
  deterministic sync (no sleeps), fixtures with real-world mess. Never
  modify a test to make it pass — flag it instead.

### Decomposition check (before producing)

Before producing the spec, size the change. Task horizon is the
strongest predictor of implementation failure. If this change would 
**modify more than 4 files**, span **more than 3
independent concerns**, or run past **~400 lines of change**, propose
splitting it into multiple specs with an explicit ordering (which ships
first, what each depends on) and let the user decide.

When the thinking is done, shift to investigation mode. Now you're
reading code for **precision** — finding the exact files, symbols,
lines, and verification commands.

### Investigate

For each area the conversation identified:

1. **Current behavior**: plain prose a newcomer can read top to bottom,
   explaining how the affected part works today. Precise locations
   belong in "Files that matter," not here — spend only a sparing
   handful of `file:line` anchors, for spots a reader would otherwise
   have to grep.

2. **Files that matter**: grep every symbol the change touches —
   callers, type definitions, related tests. Target 6-10 files, each
   with its specific symbols.

3. **Patterns to follow**: for anything new (validation, parsing, I/O,
   error handling, a utility, a fixture), name the existing
   library/pattern for that job with a `file:line` example, so the
   implementing agent emulates it instead of inventing a parallel one.
   Say so if there's no precedent.

4. **Tests**: list existing tests that must keep passing and new tests
   for the Phase 1 edge cases. Flag any needing authentic/minimized
   fixtures (a real small file, an in-memory DB) over mocked returns.
   For a behavior that's really a *property* (idempotence, round-trips,
   an invariant, a bound that must never be exceeded), call for a
   property-based test (e.g. Hypothesis) and name the property.

5. **Verification command**: the exact command, then a plain-English
   checklist of what to test → expected output — Given/When/Then for
   user-facing behavior, plain bullets otherwise. Include at least one
   error-path bullet wherever the change handles I/O or untrusted input.
   Describe behavior, not assertion code.

6. **Optional domain sections**: if the change has structured artifacts
   that aid review (tool/schema definitions, state tables, decision
   matrices, migration plans), add a custom section between "Current
   behavior" and "Alternatives rejected." Skip if straightforward.

### Review and confirm

**Branch.** Before writing anything to disk, check the current
branch. If on `main`/`master`, create and switch to
`spec/{slug}`. If on another branch, confirm with the user that
this is where they want the spec committed. Never write spec files
on main.

Write the draft spec to `docs/specs/features/{slug}/spec.md`,
following the structure in `reference/spec-template.md` (read it now if
you haven't this session). Create the directory if it doesn't exist.

Then launch the `specd-spec-reviewer` agent using the Agent tool with
`subagent_type: "specd-spec-reviewer"`. Pass the spec path. The reviewer
checks seven evidence-backed failure modes: verbosity, contradictions,
stale references, vague constraints, weak verification, untestable
NFRs, and scope creep.

**If any check fails:** fix the spec before presenting it. Apply
each fix the reviewer recommends. Don't ask the user to fix
reviewer findings — these are quality issues you should resolve.

**After the reviewer passes** (or after you've fixed its findings),
surface your *own* residual ambiguity before asking for approval. The
challenge conversation surfaced the user's blind spots; this surfaces
yours. A spec is a confident artifact — it reads as settled even where
you were interpreting a vague request, and the implementing agent will
never see your uncertainty. State the **2-3 load-bearing assumptions**
you baked in (the ones that, if wrong, change the spec) plus any
ambiguity you could not resolve, then present and ask:

> "Here's the spec at `docs/specs/features/{slug}/spec.md` — it
> passed all quality checks.
>
> Assumptions I baked in — flag any that are wrong:
> 1. {load-bearing assumption}; if wrong → {what changes}.
> 2. {…}
> {Open question I couldn't resolve from the code or our conversation,
> if any.}
>
> Do you approve it as-is, or want changes?"

Don't gate on this — surface it and let the user decide (this skill is
a thinking partner, not a checkpoint). If the user consciously accepts
an assumption rather than resolving it, record it inline in the spec
(Constraints or Approach) as `ASSUMPTION (accepted by {who}): {claim};
if false, {what changes}`, so the deferred ambiguity stays visible in
the contract instead of traveling silently into the build.

**If the user requests changes:** apply them to the spec file, then
judge how substantial the round of edits was:

- **Minor** (wording, typos, single bullet tweak): apply and
  re-present for approval.
- **Substantial** (multiple sections changed, scope shift, new
  edge cases or constraints, approach or alternatives revised):
  re-run the `specd-spec-reviewer` agent on the updated spec, fix any new
  findings, then re-present for approval.

Loop until the user explicitly approves. Do not assume approval
from silence or from a non-committal response.

**Only after explicit approval**, update the Spec Index — add or
update the entry in the Features table of `docs/specs/spec.md` with
status `Waiting Implementation`. The row format, the full set of status
values, and the Updated-column lifecycle rules are in
`reference/spec-index.md`; read it and follow them.

Tell the user:

> "Spec saved to `docs/specs/features/{slug}/spec.md`.
> Spec Index updated in `docs/specs/spec.md`.
>
> Clear your context and run:
> `/specd:execute-spec docs/specs/features/{slug}/spec.md`"

---

## Spec template

The full template lives in `reference/spec-template.md` — read it when
you reach "Write the draft spec" above. It serves two audiences with
one document: above the "Implementation contract" divider is what a
human reviewer needs to understand and approve the approach (Why,
Summary, Current behavior, Alternatives, Edge cases, and the Approach
itself — prose strategy, the hinge the reviewer signs off on); below it
is the binding contract that pins that strategy to specifics —
Constraints, Do NOT, Files that matter, and Verification (deliberately
redundant with each other — keep it that way). A constraint repeated
across these sections is exactly what survives context compaction and
mid-context attention loss during a long implementation; this is one of
the few places where saying something twice is the research-backed move,
not bloat. If a reviewer flags the repetition, defend it.

