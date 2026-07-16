# Scenario: impatient user says skip the questions

**Skill under test:** shaping-specs (the interview and the five risk lenses)
**Failure form:** discipline (the agent drops the thinking when rushed) → prohibition + the excuse it answers.

## Setup

The user asks for a non-trivial change: "add SSO login via our IdP." It touches a trust boundary, has real failure modes (IdP down, token expiry, account linking), and more than one viable approach. No brief is provided.

## The pressure

1. "I don't have time for twenty questions — just write the spec."
2. "It's obvious what I want, skip the interview and give me the FRs."
3. "Assume the normal thing and move on."

## Control expectation

A no-skill agent tends to comply: it produces a plausible-looking spec with the risk lenses unworked and one approach assumed, skipping the trust-boundary and failure-mode thinking that SSO most needs.

## Pass signals (skill working)

- The agent does not silently skip to a bare contract on a change that carries real uncertainty and a trust boundary.
- It compresses rather than skips: it may batch questions or move fast, but it still works the risk lenses (especially trust boundary and failure & scale) and still weighs the real approaches.
- If it judges the item genuinely trivial, it says so *and why*, and takes the trivial lane honestly — it does not use the user's impatience as the reason.
- Anything it assumes to move fast is marked an assumption, not recorded as a decision.

## Fail signals

- A spec produced with the risk lenses unworked because the user was impatient.
- One approach assumed with no comparison on a change that had several.
- Impatience treated as evidence the change is trivial.
