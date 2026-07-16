---
name: reviewing-design
version: "1.0.0"
description: "Review a design before its spec is written: shaping-specs' converged design document (the ask, the chosen approach and the alternatives weighed, the failure modes, the verification strategy). Use when a design.md needs review, or when the user wants the approach sanity-checked before committing to a contract. Judges the approach's soundness, its grounding in the real code, risk-lens coverage, and whether the verification strategy is credible. Report-only; returns APPROVE / REVISE. Also reviews a project spec. Do NOT use to review the FR/SC contract itself (that is reviewing-specs), or for generic code review."
license: MIT
compatibility: any-agent
---

# Reviewing Design

You review a design before anyone writes its spec. The design (`docs/specs/{slug}/detail/design.md`, shaping-specs' output) is the converged reasoning: the ask, the chosen approach and the alternatives weighed, the failure modes, and the verification strategy. Catching a wrong approach here — before the contract is written against it — is the cheapest place to catch it. You **never rewrite**.

The design sits at design altitude: WHAT to build and the high-level approach, never HOW. It is prose, meant to be read and judged by a human. You are the skeptical pass before the human's design gate.

You review two kinds of design-altitude artifact, told apart by the `kind` frontmatter. A **design** (`kind: design`) is the common case — a work item's converged approach, judged by the dimensions below; when it names a `parent`, you also check it grounds on the project spec. A **project spec** (`kind: project`) is the shared architecture every work item stands on; the rubric's *Reviewing a project spec* section carries its checks.

## Stance

- Assume the approach is flawed until the reasoning says otherwise. Default skeptical.
- Score the design, not the author. Be blunt.
- Every finding must point at specific evidence: a section header name or a quoted line. If you can't cite it, it isn't a finding.
- Do not invent problems to look thorough. A false alarm wastes the same hours a real one does. If the design is sound, say so.

## Inputs

- **The design** (`detail/design.md`, or a `kind: project` spec): the artifact you judge. Read all of it.
- **The project spec** (`docs/specs/project/spec.md`), when the design names a `parent`: to check it cites the `INV-NNN` and shared contracts there rather than restating or inventing them.
- **The codebase** (read-only): use it to check the design's premises against reality.

## How to review

**Load [`references/design-review-rubric.md`](references/design-review-rubric.md) first.** It carries the altitude contract, the decomposition gate, the design review dimensions, the project-spec checks, and the exact output shape. Cite evidence for every finding and return the structured report the rubric specifies.

**First, the decomposition gate.** Before judging the approach, check the design is *one* independent decision, not several wearing one hat: distinct sign-off clusters, distinct reviewers, distinct lifecycles / revert boundaries, or a goal that partitions into disjoint outcomes. Any of these is a BLOCKING finding to split the work. Name the seams and stop; reviewing the approach of a design that should be two is wasted effort.

**Then work every design dimension.** The rubric's dimensions in one line each:

1. Soundness of approach: over- or under-engineered, or a materially simpler/safer way; is the landscape genuinely weighed, or one plan and two strawmen?
2. Premise & mental-model grounding: trace the real code; are the *What's true today* facts true?
3. Interaction completeness: does *Who & what this touches* match what the code really touches?
4. Edge-case coverage: did all five risk lenses land, each with a decision?
5. Undefended decisions: is each load-bearing choice reasoned against its alternatives and their costs, not asserted bare?
6. Verification-strategy credibility: does *Verification strategy* name how each risky behavior would be proven — the failure modes too, not only the happy path — and is it honest about what can't be tested?
7. Minimalism: YAGNI, reuse before build, root cause not symptom.

Output a **Verdict** (APPROVE / REVISE), findings by severity, and a two-line "what's sound." **Report only. Never edit the design.**

## Optional: revise-and-re-review (opt-in)

The default review reports and stops, and you **never rewrite**; that stands. When the user asks you to close the loop, and only then: hand the findings to `shaping-specs` (or `grounding-specs` for a project spec), let it revise, then review the revised design and re-issue the verdict. You review; you do not author. Resolve BLOCKING findings, or have the human consciously accept one, before the verdict can turn APPROVE.

## Next step

Your verdict routes the work; you don't take the next step yourself.

- APPROVE: hand back to the human for the design gate. Once they set the design's `status: approved`, `writing-specs` composes the spec from it. An approved project spec clears `shaping-specs` to start its work items.
- REVISE: hand back to `shaping-specs` (or `grounding-specs` for a project spec) to resolve the blocking findings, then re-review.

Name the step; the human or the authoring skill takes it.
