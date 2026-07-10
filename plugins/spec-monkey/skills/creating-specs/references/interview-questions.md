# Interview questions

This is the discovery instrument for a spec. It is **not** the spec's layout: it follows the order you
interrogate in, working backwards from every field the template needs filled. Discover here; compose the
answers into `spec-template.md` afterward.

## How to use it

- **This is a conversation, not a questionnaire.** These are prompts, not a script to read out in order.
  Skip what isn't relevant to this change, reword a question to fit the user's context, and let each answer
  reshape what you ask next. The goal is shared understanding, not a filled-in form.
- **Ask relentlessly, one question at a time.** Plain language, in the user's own words. Never offer a
  menu of options to pick from unless the choice is genuinely discrete and low-stakes; a considered answer
  beats a grabbed one.
- **Reflect every answer back.** "I think you mean X, which implies Y — right?" Surface the implication,
  not just the words.
- **Recurse.** When an answer opens new questions or a sub-decision, chase those before moving on. A branch
  of the design tree is not done until its leaves are.
- **Separate decisions from assumptions.** Record "the user decided X" apart from "I'm assuming X". Every
  unverified belief is an assumption, not a fact, until confirmed.
- **Don't gold-plate or narrow.** If scope, approach, or intent is unclear, ask. Don't guess.

The areas below run in a natural discovery order. Each notes the template field(s) it fills.

---

## A. The ask, and the one-decision gate
*(fills: Goal · The request · Drivers — and decides whether this is one spec or several)*

- In one or two sentences, what are you actually asking for? (Keep it faithful; this catches drift later.)
- What single observable delta must be true when this is done? State it as "X moves from A to B",
  checkable true or false. If you can't, we don't have a goal yet.
- What is broken or missing today? What does leaving it cost, and to whom? Who benefits when it's fixed?
- **One-decision gate — settle this before going deep.** Is this exactly one independent decision?
  - Do the calls that need sign-off form one conversation, or several unrelated ones?
  - Would approval need different specialists who can't each sign off on the whole?
  - Do the parts have distinct lifecycles (own versioning, rollout, or rollback)?
  - Will the success criteria partition into near-disjoint groups?
  - If any of these is "yes", **stop and split**: a parent for the goal, shared contract, and
    orchestration, plus one child per decision. Interview each child on its own.

## B. Orientation
*(not user questions — your own discovery; grounds "What's true today" and the blast radius)*

- Which systems and files does this touch? What patterns are already in play here?
- Grep wide for the ripple: what else calls into, or depends on, the thing being changed?
- If the sweep turns up scope you hadn't accounted for, loop back to the human before continuing.

## C. Behavior, requirements & proof
*(fills: Requirements & success criteria (by subsystem) · Coverage exceptions)*

- Walk me through what an outside observer sees happen, step by step. Not the code; the visible flow.
- Does this span more than one subsystem or seam? Name them; they become the requirement groups.
- For each rule the change must satisfy, one at a time:
  - Who is the actor and what is the action? Is there a runtime condition (a leading WHEN)?
  - Can a single pass/fail test settle this rule, or is it really several? (If several, split it.)
  - Is any guarantee word in play (every, only, always, never, cannot)? If so, what exactly enforces
    it, and is that check as strong as the word? If not, what's the honest, weaker wording?
- For each requirement: what measurable, technology-agnostic outcome proves it on the running system?
  (An outcome an outside observer can check, not "the unit test passes" or "uses Redis".)
- Is there any requirement with no way to prove it yet? Say so; it's a declared gap, not a blank.

## D. Timing & order
*(fills: Rollout / cutover gate · Blast radius & reversibility (brief) · When it happens)*

- What triggers each behavior: an event, a schedule, on-demand, a state change? What must be true
  before it may run?
- What must exist or land first? Any internal ordering ("the backfill completes before the new read
  path goes live")?
- Under what condition does this turn on? What's the risky moment, and what signal do you watch?
- Until when can this be undone? What becomes permanent once it ships (irreversible migrations,
  emitted events, external side effects)?

## E. Fit & constraints
*(fills: What's true today · Constraints & non-functional bounds · depends_on)*

- What load-bearing facts about how the system works today does this design rest on? For each: do
  you know it, or are you assuming it?
- What hard limits bound the solution: platform, volume, must-reuse, compliance?
- Walk performance, security, reliability, accessibility. Which apply, and at what threshold?
- What external services, APIs, other specs, or teams does this ride on?

## F. Contracts
*(fills: Data & interface contract)*

- Does anything cross a boundary: an API request/response, an event or message, a persisted record
  other code or teams depend on?
- For each: what does it represent, which fields matter and what do they mean, what invariants must
  hold, and who consumes it? (Logical shape only; the concrete type and storage are the implementer's.)

## G. What could go wrong — the five lenses
*(fills: Failure modes; accepted risks surface in Known limitations & honest gaps)*

Work every lens. Each risk gets a decision: HANDLE (→ an FR), ACCEPT (→ Known limitations & honest gaps), or
OUT-OF-SCOPE (where does it live?).

- **Failure & scale:** behavior at 10× / 1000× load or data? A dependency down, slow, or
  rate-limited? Concurrency, partial failure mid-operation, retries / idempotency? Empty, huge,
  malformed, or hostile input?
- **Operational readiness:** how is it observed live? How is a break noticed? What config or
  environment does it need?
- **Trust boundary:** where does untrusted input cross into trusted code? Who is authorized, and
  what happens on denied or expired credentials? What sensitive data is touched, and how protected?
- **Implied work:** what callers or consumers must change too? Migrations or backfills forced? Docs,
  configs, or types that go stale? What was assumed free but isn't?
- **Better way:** is there a simpler or safer approach? Name it, then adopt it or record why this
  approach wins.

## H. Proof mechanics
*(fills: Verification approach & commands, incl. the worked case)*

- What evidence would convince a skeptic the requirements actually hold?
- Does any behavior cross a real boundary (a database, an HTTP call, a queue, a contract between two
  modules)? If so, how is that crossing proven end-to-end, not just in isolation or with mocks?
- What are the exact commands anyone can run to verify success?
- Give me one concrete end-to-end example with real values: given X, when Y, then exactly Z.

## I. Residue & fallbacks
*(fills: Blocking open questions (brief) · Open questions & assumptions · Contingencies)*

- What unresolved questions are left? For each: does it gate the release (blocking), or can it be
  deferred with a revisit trigger?
- What unverified beliefs does the design still lean on? For each: confidence, the impact if wrong,
  and how you'd verify it.
- Is there any what-if fallback that only applies if something breaks? What's its trigger, and who
  acts? (These are contingencies; they stay out of the requirements list.)
