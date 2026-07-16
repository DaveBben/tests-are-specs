# Scenario: a confident PRD with unstated assumptions

**Skill under test:** shaping-specs + `references/ingesting-briefs.md`
**Failure form:** shaping (the fast path launders inferences into facts, or skips the lenses) → positive recipe.

## Setup

The user pastes a polished one-page PRD for "export to CSV." It reads decisively but leaves gaps: it never says what happens on a 2GB export, never mentions who may export (a trust-boundary question), and asserts "stream it to the browser" as *the* approach with no alternative. It also quietly assumes the data fits in memory.

## The prompt

"Here's the PRD, let's get this shaped."

## Control expectation

A no-skill agent tends to either re-interview from scratch (ignoring the doc, high friction) or accept the doc wholesale (recording its assumptions as decisions and skipping the lenses it didn't cover).

## Pass signals (skill working)

- The agent ingests the doc: it reads it, maps what it settles, and reflects the extraction back **once** — "here's what I read you as deciding / assuming / leaving open" — instead of a fresh one-question-at-a-time interrogation.
- The unstated "fits in memory" and "stream to browser" are surfaced as **assumptions to confirm**, not recorded as facts.
- It interviews only the residual gaps (large-export behavior, who may export), not what the doc already answers.
- It still works the risk lenses the PRD skipped (trust boundary: authorization; failure & scale: the 2GB case) and still weighs the asserted approach against a real alternative before ratifying it.

## Fail signals

- Re-running the full interview and ignoring the document (the friction the fast path exists to remove).
- The doc's unstated assumptions written into the spec as decisions/facts.
- The trust-boundary and scale lenses skipped because "the PRD covers it."
- The asserted approach adopted with no comparison.
