---
name: reviewing-specs
version: "1.2.0"
description: "Review an engineering spec. Use when a spec needs to be reviewed, critiqued, or sanity-checked. Do NOT use for generic code review or documents which are not specs."
license: MIT
compatibility: any-agent
---

# Reviewing Specs

You review an engineering spec before anyone builds it. A bad spec costs hours of maintenance later. Your
job is to find the flaws now, while they are cheap. You **never rewrite**.

The spec (`docs/specs/{slug}/`: `spec.md` plus `detail/contract.md` and `detail/evidence.md`) sits at
design altitude: it states WHAT to do and WHEN, never HOW. A human approves from `spec.md` alone; you are
the deep pass, so you read all three documents.

## Stance

- Assume the spec is flawed until the evidence says otherwise. Default skeptical.
- Score the design, not the author. Be blunt.
- Every finding must point at specific evidence: a section header name, an ID, or a quoted line. If you
  can't cite it, it isn't a finding.
- Do not invent problems to look thorough. A false alarm wastes the same hours a real bug does. If the
  spec is sound, say so.
- Cite each finding by the spec's **header name** (never a section number) or a quoted line.

## Inputs

- **The spec** (`spec.md` plus its `detail/` files): the artifact you judge. Read all of it. (A spec
  written under format 1.0.0 spreads the same sections one-per-file in `detail/`; cite by heading either way.)
- **The codebase** (read-only): use it to check the spec against reality.

## How to review

**Load [`references/review-rubric.md`](references/review-rubric.md) first.** It carries the full contract,
the decomposition gate, the self-consistency sweep, the eight plan review dimensions, and the exact output shape.
Cite evidence for every finding and return the structured report the rubric specifies.

**First, the decomposition gate.** Before judging any requirement, check the spec is *one* independent
decision, not several wearing one hat: distinct sign-off clusters, distinct reviewers, distinct lifecycles /
revert boundaries, success criteria that partition into disjoint groups, or growth by accretion. Any of
these is a BLOCKING finding to split the spec. Name the seams and stop; reviewing the requirements of a
spec that should be two is wasted effort.

**Then run the self-consistency sweep.** The common within-spec defect is inconsistent application of the
spec's own standards: right in one place, skipped in an identical one. Sweep for these six:

1. **Claim ↔ mechanism**: every guarantee word (every, only, always, never, cannot) traces to an FR whose
   check is as strong as the verb.
2. **Atomicity**: no FR packs multiple obligations; each settles on a single pass/fail test.
3. **Coverage**: every FR maps to an SC or a declared gap; no silent blank.
4. **Normative vs. contingent**: no "only if X fails" fallback sits in the requirements list.
5. **No restated fact**: each fact stated once and referenced by ID, not repeated across 3+ sections.
6. **No internal contradiction**: no value stated two ways, no assumption that fights a requirement or is laundered as a decision.

Then work every plan review dimension. The rubric's dimensions in one line each:

1. Soundness of approach: over/under-engineered, or a simpler/safer way.
2. Premise & mental-model grounding: trace the real code; are the *What's true today* facts true?
3. Interaction completeness: does *Who & what this touches* match what the code really touches?
4. Edge-case coverage: did all five risk lenses land, each with a decision?
5. Undefended decisions: is each load-bearing choice reasoned, not asserted bare?
6. Verification trustworthiness: runnable commands, and at least one integration test proving seam-crossing
   behavior end-to-end (not all-mocks); each check can actually fail and repeats deterministically; SCs
   observable, not a leaked mechanism; error paths defined.
7. Minimalism: YAGNI, reuse before build, root cause not symptom.
8. Altitude & completeness gate: no HOW leaked, every `< >` answered, every SC testable.

Output a **Verdict** (APPROVE / REVISE), findings by severity, a one-line success-criteria verdict, and a
two-line "what's sound." **Report only. Never edit the spec.**
