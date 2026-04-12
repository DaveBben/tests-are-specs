# Review rubric

Work through each dimension. Cite evidence for every finding: a section header name, an ID
(`FR-NNN` / `SC-NNN`), or a quoted line. If you can't cite it, it isn't a finding.

## Contents

- [The altitude contract (what the spec is)](#the-altitude-contract-what-the-spec-is)
- [Dimensions](#dimensions)
  1. Soundness of approach
  2. Premise & mental-model grounding
  3. Interaction completeness
  4. Edge-case coverage (all five lenses)
  5. Undefended decisions
  6. Traceability & consistency
  7. Verification trustworthiness
  8. Minimalism: the laziest solution that works
  9. Altitude & completeness gate
- [Output: a structured report](#output-a-structured-report)

## The altitude contract (what the spec is)

A spec states **WHAT to do and WHEN, never HOW.**

- **WHAT / WHEN belongs in the spec:** the ask, why, observable behavior, requirements,
  triggers, ordering, rollout conditions, reversibility, external contracts, risks, blast
  radius, success criteria. Everything a human signs off on.
- **HOW never belongs in the spec:** which file or symbol to edit, the algorithm, the concrete
  type or struct, the branch, the rollback script, the task breakdown. The implementor owns all of it.
  The one exception is verification: the run commands that prove success DO belong in the spec,
  under *How I know it works*.
- **Litmus:** if a line tells an implementer which file, symbol, or type to edit, it's a leaked
  HOW. A reviewer approves direction, not line edits. (Verification run commands are the exception;
  they belong in the spec.)

Judge the **engineering**, not the prose polish. Don't churn on wording. But a formatting problem
is fair game where it would mislead a builder: a duplicated decision that will drift, a requirement
hiding implementation trivia, a broken FR→success-criterion trace.

## Dimensions

**1. Soundness of approach**
- Will the approach actually achieve the Goal?
- Is it over-engineered (complexity the requirements don't need) or under-engineered (won't
  survive the edge cases)?
- Is there a materially simpler or safer approach? If so, name it.

**2. Premise & mental-model grounding**
- Does the spec's model of how the system works match reality: control flow, data flow, timing,
  contracts? Trace the real code to confirm.
- Are the *What's true today* facts actually true in the repo? Are the *Data & interface contracts*
  consistent with what the code and its consumers expect?
- A spec built on a false premise fails no matter how clean it looks. Name any premise that
  doesn't hold.

**3. Interaction completeness**
- Map the change's blast radius. Does *Who & what this touches* match what the code actually
  touches?
- Internal: every caller, event consumer, serialization/API boundary, and config reader the change
  touches. External: every user-facing state that applies (empty, loading, error, partial, success).
- What integration point is silently assumed unchanged but isn't?

**4. Edge-case coverage (all five lenses)**
- Did every lens in *What could go wrong* land in requirements, edge cases, or scope: Failure &
  scale, Operational readiness, Trust boundary, Implied work, Better way?
- Does each surfaced risk carry a decision (HANDLE / ACCEPT / OUT-OF-SCOPE)? Is a lens left blank
  without even a "considered, none apply"?
- What failure mode is unhandled and unmentioned? Name the gap.

**5. Undefended decisions**
- For each load-bearing choice (the approach, the data model, a hard constraint), is there a reason,
  or is it asserted bare?
- Would a competent engineer ask "why this and not X?" and find no answer? Flag choices that need a
  defended rationale or an alternative-rejected note. Do not demand justification for the obvious.

**6. Traceability & consistency**
- Does every requirement trace to a way to be verified? Each `FR-NNN` should connect to an `SC-NNN`
  or the worked case, and each `SC-NNN` should state a measurable outcome.
- Are there internal contradictions: a value stated two ways, an assumption that fights a requirement?
- Are low/med-confidence assumptions surfaced as assumptions, or laundered as decisions?
- Is any decision re-stated in 3+ places instead of referenced by ID? That will drift. Name the
  canonical home and the copies. (One incidental duplicate is a nit; systemic restatement is real.)

**7. Verification trustworthiness**

Verification is the one place the spec gets concrete: it carries the actual run commands that prove
success, not just prose. Tests are the spec's proof, so hold them to a real standard. Judge whether
those commands, the *Verification approach*, and the success criteria would convince a skeptic:

- **Runnable, not hand-waved:** does the *Verification approach* give the actual commands to run,
  not just a description? Verification with no runnable check is weak.
- **At least one integration test:** when the change has behavior that crosses a real boundary (a
  database, an HTTP call, a queue, a contract between two modules), does the *Verification approach*
  prove at least one path end-to-end across that boundary, rather than leaning entirely on isolated
  units or mocks? A change with real seams and an all-unit, all-mocked verification is weak. Require
  the crossing be proven.
- **Observable end-to-end:** is each `SC-NNN` something an outside observer can check on the running
  system, not a description of an internal mechanism?
- **No leaked HOW as a criterion:** an SC met only by a mechanism ("uses Redis", "the unit test
  passes") is a leaked HOW disguised as an outcome. Flag it, and ask for the observable outcome it
  stands in for.
- **Each check can actually fail:** would every check flip to failing if the behavior it guards
  broke? A check that passes regardless proves nothing: an assertion on a constant, a mock verifying
  itself, or a *Worked case* whose `Then` values are read back from the thing under test instead of
  derived independently with real numbers.
- **Error and edge paths, not only happy path:** is success defined for the failure and boundary
  cases the risk lenses surfaced, or only for the golden path?
- **Deterministic and reproducible:** does each check give the same verdict every run, or does it
  ride on timing, ordering, network flakiness, or real-world nondeterminism the spec never pins?
  A check that cannot be trusted to repeat is weak evidence.
- **Real coverage:** does an outcome exist for each requirement, and does it pin THAT requirement?

**8. Minimalism: the laziest solution that works**

Climb this ladder and flag the lowest rung the approach skips:
- **Does it need to exist?** Is any requirement speculative, built for a need the Goal doesn't state?
  YAGNI says cut it.
- **Reuse before build.** Does the approach specify building something the codebase already has?
  Grep to confirm, then name what it should reuse.
- **Root cause, not symptom.** For a fix, does the spec patch one path when the fix belongs once in
  the shared place every caller routes through?
- Is the change bigger than the problem? Name the simplification, but only one that stays correct on
  the edge cases. A "minimal" spec that drops input validation, error handling, security, or
  accessibility is broken, not lazy. Do not push those cuts.

**9. Altitude & completeness gate**

- **No HOW leaked.** No file or symbol pinned as content (a pin is allowed only as cited evidence for
  a doubtable *What's true today* fact); no language-typed struct or class block; no task manifest or
  waves; no branch or rollback-script mechanics; no pattern-to-mirror. (Verification run commands are
  allowed; they belong in *How I know it works*.)
- **Every question answered.** No unfilled `< >` placeholder. Every risk lens carries a decision (or
  "considered, none apply"). *When it happens* is complete: triggers, ordering, rollout conditions,
  reversibility. *Open questions & assumptions* is empty, or each item is explicitly deferred with a
  revisit trigger.
- **Every success criterion is testable and technology-agnostic.** (Cross-checks dimension 7.)

## Output: a structured report

- **Verdict:** APPROVE or REVISE. (REVISE if any BLOCKING finding exists.)
- **BLOCKING**: will cause real harm; must fix before the spec is trusted. Each: dimension ·
  location (header / ID / quoted line) · the problem with quoted evidence · why it matters ·
  suggested direction.
- **SHOULD_FIX**: a real weakness; fix unless there's a reason not to. Same shape.
- **SUGGESTIONS**: improvements and nits; optional. Same shape, terse.
- **Success-criteria verdict:** one sentence on whether the outcomes are trustworthy. If not, name
  the single worst offender.
- **What's sound:** two or three lines, so the author knows what NOT to churn.

Do not edit the spec. Report only.
