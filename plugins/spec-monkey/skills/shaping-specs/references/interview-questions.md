# Shaping questions

This is the thinking instrument for a spec. You use it to work out what to build, why, and which approach wins, before anyone writes a binding requirement. It is **not** the spec's layout. Discover here; `writing-specs` composes the contract afterward.

The output of this instrument is the reasoning: `detail/evidence.md` (*What's true today*, *Failure modes*, *Who & what this touches*, *Open questions & assumptions*) plus the brief's *Drivers* and *Decisions to sign off*, and a drafted *Goal* and *The request*. It uses the shared format in `writing-specs/references/spec-template.md`.

## How to use it

- **This is a conversation, not a questionnaire.** These are prompts, not a script to read out in order. Skip what isn't relevant to this change, reword a question to fit the user's context, and let each answer reshape what you ask next. The goal is shared understanding, not a filled-in form.
- **Ask relentlessly, one question at a time.** Plain language, in the user's own words. Never offer a menu of options to pick from unless the choice is genuinely discrete and low-stakes; a considered answer beats a grabbed one. This holds even when you present approaches: lead with your recommendation and its reason, then put the choice to the user in their own words.
- **Reflect every answer back.** "I think you mean X, which implies Y, right?" Surface the implication, not just the words.
- **Recurse.** When an answer opens new questions or a sub-decision, chase those before moving on. A branch of the design tree is not done until its leaves are.
- **Separate decisions from assumptions.** Record "the user decided X" apart from "I'm assuming X". Every unverified belief is an assumption, not a fact, until confirmed.
- **Don't gold-plate or narrow.** If scope, approach, or intent is unclear, ask. Don't guess.
- **Write for one read.** One idea per sentence; caveats get their own sentence. Lists over running prose; never a wall of text, prefer multiple turns.

The areas below run in a natural discovery order. Each notes the artifact field(s) it feeds.

---

## A. The ask, and the one-decision gate
*(feeds: Goal · The request · Drivers, and decides whether this is one spec or several)*

- In one or two sentences, what are you actually asking for? (Keep it faithful; this catches drift later.)
- What single observable delta must be true when this is done? State it as "X moves from A to B", checkable true or false. If you can't, we don't have a goal yet.
- What is broken or missing today? What does leaving it cost, and to whom? Who benefits when it's fixed?
- **One-decision gate: settle this before going deep.** Is this exactly one independent decision?
  - Do the calls that need sign-off form one conversation, or several unrelated ones?
  - Would approval need different specialists who can't each sign off on the whole?
  - Do the parts have distinct lifecycles (own versioning, rollout, or rollback)?
  - Will the success criteria partition into near-disjoint groups?
  - If any of these is "yes", **stop and split**: a parent for the goal, shared contract, and orchestration, plus one child per decision. Shape each child on its own.

## B. Orientation
*(not user questions: your own discovery; grounds "What's true today" and the blast radius)*

- Which systems and files does this touch? What patterns are already in play here?
- Grep wide for the ripple: what else calls into, or depends on, the thing being changed?
- If the sweep turns up scope you hadn't accounted for, loop back to the human before continuing.

## C. Fit & constraints
*(feeds: What's true today · the constraint facts writing-specs binds into Constraints & non-functional bounds · depends_on)*

- What load-bearing facts about how the system works today does this design rest on? For each: do you know it, or are you assuming it?
- What hard limits bound the solution: platform, volume, must-reuse, compliance?
- Walk performance, security, reliability, accessibility. Which apply, and at what threshold?
- What external services, APIs, other specs, or teams does this ride on?

Record the current-state facts under *What's true today*. The hard limits and thresholds are reasoning too: note them so `writing-specs` can bind them into *Constraints & non-functional bounds* without re-interviewing.

## D. What could go wrong: the five lenses
*(feeds: Failure modes; accepted risks are flagged for Known limitations & honest gaps)*

Work every lens. Each risk gets a decision: HANDLE (a requirement `writing-specs` will write), ACCEPT (an admitted gap), or OUT-OF-SCOPE (say where it lives).

- **Failure & scale:** behavior at 10x / 1000x load or data? A dependency down, slow, or rate-limited? Concurrency, partial failure mid-operation, retries / idempotency? Empty, huge, malformed, or hostile input?
- **Operational readiness:** how is it observed live? How is a break noticed? What config or environment does it need?
- **Trust boundary:** where does untrusted input cross into trusted code? Who is authorized, and what happens on denied or expired credentials? What sensitive data is touched, and how protected?
- **Implied work:** what callers or consumers must change too? Migrations or backfills forced? Docs, configs, or types that go stale? What was assumed free but isn't?
- **Better way:** is there a simpler or safer approach? This lens feeds section E below.

Record each risk and its decision under *Failure modes*, one line per lens, citing where a HANDLE lands. The touch-list from the *Implied work* lens plus orientation composes *Who & what this touches*.

## E. Approaches: generate, compare, recommend
*(feeds: Decisions to sign off, and resolves the Better way lens)*

This is the core of shaping. Do not settle on the first approach that works.

- Name 2-3 genuinely different ways to reach the goal. Real alternatives, not one plan and two strawmen. If the change is trivial and only one sane approach exists, say so and move on; do not manufacture options.
- For each approach, lay out the tradeoff in plain terms: what it costs, what it risks, what it forecloses, what it makes easy later. Tie each to the failure modes above: which lens does it handle well, which does it expose?
- State your recommendation and why. Lead with the one you'd pick and the reason, then the alternatives you rejected and why they lose.
- Put the choice to the human in their own words, not as a multiple-choice list. The recommendation is yours to defend; the decision is theirs to make.

Each approach decision becomes an entry under *Decisions to sign off*: the tradeoff, why this way, the alternative rejected, and the question for the reviewer. A choice that turns out to need a **new shared fact** (a system-wide invariant, a shared entity, a contract change) is not yours to make locally: that is a project-spec amendment. Route it up to `grounding-specs`, get it approved, then resume. Never invent a shared fact here.

## F. Residue & assumptions
*(feeds: Open questions & assumptions · the blocking ones writing-specs promotes to the brief · Contingencies)*

- What unresolved questions are left? For each: does it gate the release (blocking), or can it be deferred with a revisit trigger?
- What unverified beliefs does the design still lean on? For each: confidence, the impact if wrong, and how you'd verify it.
- Is there any what-if fallback that only applies if something breaks? What's its trigger, and who acts? (These are contingencies; they stay out of the requirements list.)

Record these under *Open questions & assumptions* (and the fallbacks in the *Contingencies* block of *Failure modes*). Flag the release-gating questions so `writing-specs` can promote them to the brief's *Blocking open questions*.
