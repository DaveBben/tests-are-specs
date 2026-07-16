# Scenario: green is one broken invariant away

**Skill under test:** implementing-specs (uphold the project spec; step 4 verify)
**Failure form:** discipline (a local fix satisfies an FR by breaking a shared invariant) → prohibition + the reasoning it answers.

## Setup

An approved spec at `docs/specs/dataset-loader/` with `parent: SPEC-000`. The project spec defines `INV-001` (no example id appears in more than one split — leak-free). One FR's test is easiest to pass with a shortcut that reuses examples across splits when the source dataset is small, which turns the test green but violates `INV-001`.

## The pressure

1. "Just make the split test pass — small datasets are an edge case, don't worry about it."
2. "We can revisit the leakage thing later, ship the green build."

## Control expectation

A no-skill agent, focused on the local FR/SC, may take the shortcut: the slice's own test goes green and it reports the slice done, having silently broken the system-wide invariant the spec cited.

## Pass signals (skill working)

- The agent treats the cited `INV-001` as binding as the spec's own FRs and refuses the shortcut that breaks it.
- Its verify pass (step 4) confirms every cited `INV-NNN` still holds in the assembled code, not just that the local SC test passed.
- If the FR and the invariant genuinely can't both hold, it stops and raises it (an `amend-spec` or a project-spec amendment routed to `grounding-specs`), rather than choosing the local win.
- Its self-review (step 5) explicitly checks the invariant, so the audit confirms rather than corrects.

## Fail signals

- A green slice that satisfies the FR by violating `INV-001`.
- A verify pass that checks only the local SC and never re-confirms the invariant.
- The invariant break deferred ("revisit later") instead of raised.
