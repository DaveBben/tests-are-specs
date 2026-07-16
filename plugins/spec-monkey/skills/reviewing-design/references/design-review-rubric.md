# Design review rubric

Work through each dimension. Cite evidence for every finding: a section header name or a quoted line. If you can't cite it, it isn't a finding.

## Contents

- [The altitude contract (what a design is)](#the-altitude-contract-what-a-design-is)
- [The decomposition gate (check first)](#the-decomposition-gate-check-first)
- [Design review dimensions](#design-review-dimensions)
- [Reviewing a project spec](#reviewing-a-project-spec)
- [Output: a structured report](#output-a-structured-report)

## The altitude contract (what a design is)

A design states **WHAT to build and the high-level approach, never HOW.** It is the converged reasoning a human signs before a contract is written from it.

- **WHAT / approach belongs in the design:** the ask, the goal, the drivers, the current-state facts, the chosen approach and the alternatives weighed with their costs, the failure modes and their decisions, and the verification *strategy* (how you'd prove it works, in prose).
- **HOW never belongs:** which file or symbol to edit, the algorithm, the concrete type or struct, the branch, the exact commands. That is the implementer's, and the contract's, not the design's. Even verification stays at strategy altitude here — "prove no leakage on a worked case," not the runnable command. The command is the contract's job (`writing-specs`).
- **Litmus:** if a line tells an implementer which file, symbol, or type to edit, it's a leaked HOW. A reviewer approves direction, not line edits.

Judge the **engineering**, not the prose polish. Don't churn on wording.

## The decomposition gate (check first)

Before judging the approach, decide whether this is **one** decision or several wearing one hat. A design covers exactly one independent decision; if it covers more, the fix is to split it, and no amount of within-design review substitutes for that. Any one diagnostic is a flag:

- **Distinct sign-off clusters**: do the decisions form one conversation, or several unrelated ones?
- **Distinct reviewers**: does approval need different specialists who can't each sign off on the whole?
- **Distinct lifecycles / revert boundaries**: does a sub-part carry its own versioning, rollout, or rollback independent of the rest?
- **Partitioned outcomes**: does the goal split into near-disjoint outcomes that could each ship alone?
- **Growth by accretion**: has the design roughly doubled by absorbing an adjacent concern, rather than deepening one decision?

If it should split: raise it as a **BLOCKING** finding, name the seams (the child work items and the order between them), and stop there. Shared ground the children stand on (the goal, data contracts, invariants) belongs in the project spec (`kind: project`), not restated in each child.

## Design review dimensions

**1. Soundness of approach**
- Will the approach actually achieve the Goal?
- Is it over-engineered (complexity the goal doesn't need) or under-engineered (won't survive the edge cases)?
- Is the landscape genuinely weighed — 2-3 real alternatives with their costs — or is it one plan and two strawmen? Is there a materially simpler or safer approach the design skipped? If so, name it.

**2. Premise & mental-model grounding**
- Does the design's model of how the system works match reality: control flow, data flow, timing, contracts? Trace the real code to confirm.
- Are the *What's true today* facts actually true in the repo? Is each assumption marked as one?
- A design built on a false premise fails no matter how clean it looks. Name any premise that doesn't hold.

**3. Interaction completeness**
- Map the change's blast radius. Does *Who & what this touches* match what the code actually touches?
- Internal: every caller, event consumer, serialization/API boundary, and config reader the change touches. External: every user-facing state that applies.
- What integration point is silently assumed unchanged but isn't?

**4. Edge-case coverage (all five lenses)**
- Did every lens in *Failure modes* land with a decision (HANDLE / ACCEPT / OUT-OF-SCOPE): Failure & scale, Operational readiness, Trust boundary, Implied work, Better way?
- Is a lens left blank without even a "considered, none apply"?
- What failure mode is unhandled and unmentioned? Name the gap.

**5. Undefended decisions**
- For each load-bearing choice (the approach, the data model, a hard constraint), is there a reason weighed against its alternatives and their costs, or is it asserted bare?
- Would a competent engineer ask "why this and not X?" and find no answer? Flag choices that need a defended rationale. Do not demand justification for the obvious.

**6. Verification-strategy credibility**
- Does *Verification strategy* say how each risky behavior would be proven, in prose — the load-bearing guarantees end-to-end, not just in isolation?
- Does it cover the failure and boundary cases the risk lenses surfaced, or only the golden path?
- Is it honest about what can't be tested (a manual check, a production metric)? An approach whose central claim has no describable test is usually underbaked — flag it now, while it's cheap. (The runnable commands are the contract's job; judge the strategy, not the syntax.)

**7. Minimalism: the laziest solution that works**

Climb this ladder and flag the lowest rung the approach skips:
- **Does it need to exist?** Is any part speculative, built for a need the Goal doesn't state? YAGNI says cut it.
- **Reuse before build.** Does the approach specify building something the codebase already has? Grep to confirm, then name what it should reuse.
- **Root cause, not symptom.** For a fix, does the design patch one path when the fix belongs once in the shared place every caller routes through?
- Is the change bigger than the problem? Name the simplification, but only one that stays correct on the edge cases. A "minimal" design that drops input validation, error handling, security, or accessibility is broken, not lazy. Do not push those cuts.

## Reviewing a project spec

For a `kind: project` spec, skip the dimensions above (they judge a work item's approach). A project spec holds no `FR`/`SC`; it is the shared ground, and you judge that. Cite evidence as always.

- **Invariants are checkable, not wishes.** Each `INV-NNN` states a property an auditor could confirm on the built system ("all inbound requests are signature-verified"), not an aspiration ("the system is secure"). Flag any that can't be checked.
- **Contracts are genuinely shared.** Each entity under *Shared data contracts* names who reads and who writes it, and more than one work item touches it. An entity only one work item uses does not belong here.
- **No requirement leaked down.** A work-item obligation (an `FR`/`SC`, a single feature's behavior) sitting in the project spec is a leak; it belongs in a work-item spec. Name it.
- **Constraints are defended architecture.** Each is an expensive-to-reverse call with a reason (and the rejected alternative, for load-bearing ones). Coding conventions are not constraints; they belong in the constitution (`standards.md` / `CLAUDE.md` / `AGENTS.md`).
- **Sequencing is sound.** *Work items & sequencing* lists the planned children; the `depends_on` order is acyclic and each item reads as one decision.
- **Thin and honest.** Only genuinely shared facts the author is confident about now. A guessed-ahead decision that should wait for the work to teach it is a finding; it belongs in a later amendment.

## Output: a structured report

- **Verdict:** APPROVE or REVISE. (REVISE if any BLOCKING finding exists.)
- **BLOCKING**: will cause real harm; must fix before the design is trusted. Each: dimension · location (header / quoted line) · the problem with quoted evidence · why it matters · suggested direction.
- **SHOULD_FIX**: a real weakness; fix unless there's a reason not to. Same shape.
- **SUGGESTIONS**: improvements and nits; optional. Same shape, terse.
- **What's sound:** two or three lines, so the author knows what NOT to churn.

Do not edit the design. Report only.
