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

**Challenge, don't interview.** The difference:
- Interview: "What are the edge cases?" (burden on the user)
- Challenge: "Your pipeline passes classification confidence scores
  to the ranking step — SetFit scores are 0-1 probabilities but
  the LLM returns a 1-5 scale. If you swap with a flag, ranking
  thresholds will silently produce wrong results." (you read the
  code and found a real problem)

**Read the code.** CLAUDE.md, Agents.md and spec.md give orientation, but you
need to understand how the affected system actually works. Read the
files involved to understand:
- How the current behavior is wired up
- What downstream consumers depend on
- Where the branching or integration points are
- What assumptions the existing code makes

Stop once you have a thorough understanding.

**Surface every ambiguity that materially changes the design** —
grounded in what you found in the code. Usually that's 2-3 concerns,
but a genuinely ambiguous change has more; don't drop a material one to
hit a number, or pad a clear change to reach one. Frame as "here's
what worries me" not "have you considered X?" If the approach looks
solid, say so, don't manufacture concerns.

**Stay inside the commandments.** The approaches, alternatives, and
constraints you propose must respect the engineering commandments
`/specd:execute-spec` enforces — don't steer the design toward buffering
unbounded data, swallowing base exceptions, regex over structured
formats (HTML/XML/JSON), blocking an async loop with sync I/O, mutating
global runtime state, or hand-rolling what a project standard already
does. If the *user's* stated approach requires one of these, raise it
as a concern rather than encoding it into the spec. A spec may record a
deliberate exception — but only an explicit, reasoned one (e.g. "must
buffer the whole payload to checksum it"), never an implied default.

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
`main`/`master`, note that you'll create a spec branch before
writing anything to disk in Phase 2 (the slug isn't known yet). If
on another branch, proceed — the spec will be written there. Never
write spec files or update the Spec Index on main.

Read `$ARGUMENTS`. Read `CLAUDE.md` and `spec.md` if they exist.

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
raise your **top concern** — grounded in what you found in the code.

Don't ask questions you can answer from the code. Start with
substance.

If the change is trivial, say so:

> "This is straightforward — I don't see risks worth discussing.
> Want me to skip to producing the spec, or straight to plan mode?"

### Conversation

**Intent & acceptance** (first, whenever anything about *what* to build
or *how you'll know it's right* isn't fixed by the code). The challenge
style above is code-grounded by design — but intent and the definition
of done usually aren't in the code. This is the deliberate complement
to "don't ask what you can answer from the code": here you ask
precisely what the code *can't* tell you.

> "The code can't tell me the intent here. What's the rule — the
> target (precision/recall, a latency budget), the business rule,
> which goal wins when two conflict, who consumes the output? And how
> will we *know* it's correct — what observable signal (a number, a
> behavior, a threshold) separates done from not-done?"

Where the bar is a user-observable behavior, pin it as Given/When/Then
("given [state], when [action], then [measurable outcome]") so a test
can be written from it directly. Whatever you settle on becomes the
acceptance bar that Phase 2's Verification operationalizes into an
exact command — don't let Phase 2 quietly invent the definition of done
that this conversation should have set.

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

**Operational readiness** (when the change touches I/O, external
services, concurrency, or unbounded data):

> "If this runs for a year against real conditions, what do you wish
> you'd built in? Implementing agents default to the happy path —
> they won't stream an unbounded input, time out a hanging call,
> scope a thread pool, or fail loudly on bad data unless the spec
> names the seam. Which inputs here are unbounded, which calls can
> hang, and what should happen when they do?"

The point isn't to lecture the agent on resilience — `/specd:execute-spec`
already enforces those defaults. It's to pin the *specific* seams in
*this* change so the agent applies the right primitive at the right
`file:line`. Whatever you settle on lands in Constraints.

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

When the thinking is done, shift to investigation mode. Now you're
reading code for **precision** — finding the exact files, symbols,
lines, and verification commands.

### Investigate

For each area the conversation identified:

1. **Current behavior**: understand how the affected part works today
   well enough to explain it in plain prose to someone new to the
   codebase. Find the precise locations too — but those anchor "Files
   that matter"; in "Current behavior" cite a `file:line` only where it
   genuinely saves a human a search.

2. **Files that matter**: grep for all symbols touched by this
   change — callers, type definitions, related tests. Target 6-10
   files with specific symbols. Follow existing codebase patterns.

3. **Patterns to follow**: for anything new this change introduces —
   validation, parsing, I/O, error handling, a utility, a test
   fixture — name the library or pattern the codebase already uses
   for that job (`file:line` of a live example), so the implementing
   agent emulates it instead of inventing a parallel one. If there's
   genuinely no precedent, say so. This belongs in the spec because
   you just read the code; the implementing agent often won't look,
   and a diff-scoped reviewer can't reliably catch the drift after.

4. **Tests**: find existing tests that must keep passing. Identify
   new tests needed from the edge cases discussed in Phase 1 — flag
   any that need authentic/minimized fixtures (a real small file, an
   in-memory DB) rather than mocked returns. Where a behavior is
   really a *property* that should hold across many inputs
   (idempotence, round-trips, an invariant, a bound that must never be
   exceeded), call for a property-based test (e.g. Hypothesis) over a
   handful of enumerated examples — and name the property, not just the
   function under test.

5. **Verification command**: the exact command to run, plus
   specific assertions for new behavior, including at least one
   error-path assertion where the change handles I/O or untrusted
   input.

6. **Optional domain sections**: judge whether the change has
   structured artifacts that aid review — new tool/schema
   definitions, state tables for in-flight dependencies, decision
   matrices, multi-phase migration plans. If present, add a custom
   section between "Current behavior" and "Alternatives rejected"
   in the spec. Skip if the change is straightforward.

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
checks eight failure modes: the seven evidence-backed ones (verbosity,
contradictions, stale references, vague constraints, weak
verification, untestable NFRs, scope creep) plus commandment
violations — a spec that prescribes an approach `/specd:execute-spec`'s
engineering mandates forbid, without a stated reasoned exception.

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
if false, {what changes}` — the same explicit, reasoned-exception
pattern the commandment gate uses, so the deferred ambiguity stays
visible in the contract instead of traveling silently into the build.

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
human reviewer needs to approve the approach (Why, Summary, Current
behavior, Alternatives, Edge cases); below it is the binding contract
for the implementing agent — Approach gives the direction, while
Constraints, Do NOT, Files that matter, and Verification pin the
specifics (deliberately redundant with each other).

