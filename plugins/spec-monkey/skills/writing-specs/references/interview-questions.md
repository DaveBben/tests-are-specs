# Contract questions

This is the discovery instrument for the **binding** part of a spec: the requirements, the contracts, the timing, and the proof. The thinking is already done and recorded in `detail/design.md` and the brief's *Decisions to sign off*. Read that first. These questions close only the contract detail the reasoning did not pin down.

Discover here; compose the answers into `spec-template.md` afterward. This is **not** the spec's layout: it follows the order you interrogate in, working backwards from the binding fields the template needs filled.

## How to use it

- **This is a conversation, not a questionnaire.** Prompts, not a script. Skip what the shaped design already settles. Reword to fit the user's context, and let each answer reshape what you ask next.
- **Ask one question at a time**, in plain language, in the user's own words. Never offer a menu unless the choice is genuinely discrete and low-stakes.
- **Reflect every answer back.** "I think you mean X, which implies Y, right?" Surface the implication, not just the words.
- **Recurse.** When an answer opens a sub-decision, chase it before moving on.
- **Separate decisions from assumptions.** An unverified belief is an assumption, not a fact, until confirmed. If it carries residual risk, it belongs under *Open questions & assumptions* in the shaped `design.md`, not buried in the contract.

Each area below notes the template field(s) it fills.

---

## A. Behavior, requirements & proof
*(fills: Requirements & success criteria (by subsystem) · Coverage exceptions)*

- Walk me through what an outside observer sees happen, step by step. Not the code; the visible flow.
- Does this span more than one subsystem or seam? Name them; they become the requirement groups.
- For each rule the change must satisfy, one at a time:
  - Who is the actor and what is the action? Is there a runtime condition (a leading WHEN)?
  - Can a single pass/fail test settle this rule, or is it really several? (If several, split it.)
  - Is any guarantee word in play (every, only, always, never, cannot)? If so, what exactly enforces it, and is that check as strong as the word? If not, what's the honest, weaker wording?
- Each HANDLE risk from the shaped *Failure modes* becomes a requirement here; make sure it did.
- For each requirement: what measurable, technology-agnostic outcome proves it on the running system? (An outcome an outside observer can check, not "the unit test passes" or "uses Redis".)
- Is there any requirement with no way to prove it yet? Say so; it's a declared gap, not a blank.

## B. Timing & order
*(fills: Rollout / cutover gate · Blast radius & reversibility (brief) · When it happens)*

- What triggers each behavior: an event, a schedule, on-demand, a state change? What must be true before it may run?
- What must exist or land first? Any internal ordering ("the backfill completes before the new read path goes live")?
- Under what condition does this turn on? What's the risky moment, and what signal do you watch?
- Until when can this be undone? What becomes permanent once it ships (irreversible migrations, emitted events, external side effects)?

## C. Contracts
*(fills: Data & interface contract)*

- Does anything cross a boundary: an API request/response, an event or message, a persisted record other code or teams depend on?
- For each: what does it represent, which fields matter and what do they mean, what invariants must hold, and who consumes it? (Logical shape only; the concrete type and storage are the implementer's.)

## D. Proof mechanics
*(fills: Verification approach & commands, incl. the worked case)*

- What evidence would convince a skeptic the requirements actually hold?
- Does any behavior cross a real boundary (a database, an HTTP call, a queue, a contract between two modules)? If so, how is that crossing proven end-to-end, not just in isolation or with mocks?
- What are the exact commands anyone can run to verify success?
- Give me one concrete end-to-end example with real values: given X, when Y, then exactly Z.

## Note on constraints and fit

The hard limits (platform, volume, must-reuse, compliance) and the current-state facts the design rests on live in `design.md` under *What's true today*. Bind them into *Constraints & non-functional bounds* from there; interview again only if a binding threshold is genuinely missing.
