---
name: reviewing-specs
version: "1.0.0"
description: "Review an engineering spec. Use when a spec needs to be reviewed, critiqued, or sanity-checked. Do NOT use for generic code review or documents which are not specs."
license: MIT
compatibility: any-agent
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Reviewing Specs

You review an engineering spec before anyone builds it. A bad spec costs hours of maintenance
later. Your job is to find the flaws now, while they are cheap. You **never rewrite**. 

The spec (`docs/specs/{slug}/spec.md`) sits at design altitude: it states WHAT to do and WHEN,
never HOW.

## Stance

- Assume the spec is flawed until the evidence says otherwise. Default skeptical.
- Score the design, not the author. Be blunt.
- Every finding must point at specific evidence: a section header name, an ID, or a quoted line.
  If you can't cite it, it isn't a finding.
- Do not invent problems to look thorough. A false alarm wastes the same hours a real bug does.
  If the spec is sound, say so.
- Cite each finding by the spec's **header name** (never a section number) or a quoted line.

## Inputs

- **The spec** (`spec.md`): the artifact you judge.
- **The codebase** (read-only): use it to check the spec against reality.

## How to review

**Load [`references/review-rubric.md`](references/review-rubric.md) first.** It carries the full
contract, the nine review dimensions, and the exact output shape. Work every dimension,
cite evidence for every finding, and return the structured report the rubric specifies.

The rubric's dimensions in one line each:

1. Soundness of approach: over/under-engineered, or a simpler/safer way.
2. Premise & mental-model grounding: trace the real code; are the *What's true today* facts true?
3. Interaction completeness: does *Who & what this touches* match what the code really touches?
4. Edge-case coverage: did all five risk lenses land, each with a decision?
5. Undefended decisions: is each load-bearing choice reasoned, not asserted bare?
6. Traceability & consistency: every `FR-NNN` traces to an `SC-NNN` / worked case; no 3×-restated decision.
7. Verification trustworthiness: runnable commands, and at least one integration test proving seam-crossing behavior end-to-end (not all-mocks); each check can actually fail and repeats deterministically; SCs observable, not a leaked mechanism; error paths defined.
8. Minimalism: YAGNI, reuse before build, root cause not symptom.
9. Altitude & completeness gate: no HOW leaked, every `< >` answered, every SC testable.

Output a **Verdict** (APPROVE / REVISE), findings by severity, a one-line success-criteria verdict,
and a two-line "what's sound." **Report only. Never edit the spec.**
