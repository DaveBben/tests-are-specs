# Review rubric

Work through each dimension. Cite evidence for every finding: a section header name, an ID
(`FR-NNN` / `SC-NNN`), or a quoted line. If you can't cite it, it isn't a finding.

## Contents

- [The altitude contract (what the spec is)](#the-altitude-contract-what-the-spec-is)
- [The decomposition gate (check first)](#the-decomposition-gate-check-first)
- [The self-consistency sweep](#the-self-consistency-sweep)
- [Plan Review Dimensions](#plan-review-dimensions)
  1. Soundness of approach
  2. Premise & mental-model grounding
  3. Interaction completeness
  4. Edge-case coverage (all five lenses)
  5. Undefended decisions
  6. Verification trustworthiness
  7. Minimalism: the laziest solution that works
  8. Altitude & completeness gate
- [Output: a structured report](#output-a-structured-report)

## The altitude contract (what the spec is)

A spec states **WHAT to do and WHEN, never HOW.**

- **WHAT / WHEN belongs in the spec:** the ask, why, observable behavior, requirements, triggers, ordering,
  rollout conditions, reversibility, external contracts, risks, blast radius, success criteria. Everything a
  human signs off on.
- **HOW never belongs in the spec:** which file or symbol to edit, the algorithm, the concrete type or
  struct, the branch, the rollback script, the task breakdown. The implementor owns all of it. The one
  exception is verification: the run commands that prove success DO belong in the spec, under *Verification
  approach & commands* (in `detail/`).
- **Litmus:** if a line tells an implementer which file, symbol, or type to edit, it's a leaked HOW. A
  reviewer approves direction, not line edits. (Verification run commands are the exception; they belong in
  the spec.)

Judge the **engineering**, not the prose polish. Don't churn on wording. But a formatting problem is fair
game where it would mislead a builder: a duplicated decision that will drift, a requirement hiding
implementation trivia, a broken FR→success-criterion trace.

## The decomposition gate (check first)

Before judging any requirement, decide whether this is **one** reviewable decision or several wearing one
hat. A spec must cover exactly one independent decision; if it covers more, the fix is to split it, and no
amount of within-spec review substitutes for that. Any one diagnostic is a flag:

- **Distinct sign-off clusters** — do the *Decisions to sign off* form one conversation, or several
  unrelated ones?
- **Distinct reviewers** — does approval need different specialists who can't each sign off on the whole?
- **Distinct lifecycles / revert boundaries** — does a sub-part carry its own versioning, rollout, or
  rollback independent of the rest?
- **Partitioned success criteria** — do the SCs cluster into near-disjoint groups? If they partition
  cleanly, the requirements under them do too. That's decomposition asking to happen.
- **Growth by accretion** — has the spec roughly doubled by absorbing an adjacent concern, rather than
  deepening one decision?

If it should split: raise it as a **BLOCKING** finding, name the seams (the child specs and the shared
parent: goal, shared contract, orchestration), and stop there. Reviewing the requirements of a spec that
should be two is wasted effort.

## The self-consistency sweep

After the decomposition gate, before the dimensions. The recurring within-spec defect is **inconsistent
application of the spec's own standards**: doing the right thing in one place and skipping it in an
identical one. Look for these six early; each is a finding under the normal evidence rule and feeds the
same severity buckets as the dimensions.

- **S1 — Claim stronger than its mechanism.** A guarantee word (every, only, always, never, cannot) in the
  Goal, *Drivers*, or a rationale, but the enforcing FR checks something weaker. Name the FR; if its check
  is weaker, downgrade the wording or strengthen the check. Call out every uncaveated instance, not just
  the first.
- **S2 — Non-atomic requirement.** An FR you can't settle with a single pass/fail test: "and"-joined or
  carrying a list. Split it into one obligation per FR.
- **S3 — Unverified requirement.** Every FR connects to an `SC-NNN` (or the worked case), and each SC
  states a measurable outcome. An FR with no SC and no declared gap, or a "must preserve" behavior with no
  dedicated SC, is a blocking gap. (Verification trustworthiness judges whether the SC is trustworthy.)
- **S4 — Contingency in the normative list.** A requirement that applies "only if X fails" belongs in
  *Contingencies*, not the requirements list.
- **S5 — Restated fact.** The same fact near-verbatim in 3+ places instead of stated once and referenced
  by ID. Name the canonical home and the copies. (One incidental duplicate is a nit; systemic restatement
  is real.)
- **S6 — Internal contradiction.** A value stated two ways, an assumption that fights a requirement, or a
  low/med-confidence assumption laundered as a decision. Name both sides of the conflict.

## Plan Review Dimensions

**1. Soundness of approach**
- Will the approach actually achieve the Goal?
- Is it over-engineered (complexity the requirements don't need) or under-engineered (won't survive the
  edge cases)?
- Is there a materially simpler or safer approach? If so, name it.

**2. Premise & mental-model grounding**
- Does the spec's model of how the system works match reality: control flow, data flow, timing, contracts?
  Trace the real code to confirm.
- Are the *What's true today* facts actually true in the repo? Is the *Data & interface contract* consistent
  with what the code and its consumers expect?
- A spec built on a false premise fails no matter how clean it looks. Name any premise that doesn't hold.

**3. Interaction completeness**
- Map the change's blast radius. Does *Who & what this touches* match what the code actually touches?
- Internal: every caller, event consumer, serialization/API boundary, and config reader the change touches.
  External: every user-facing state that applies (empty, loading, error, partial, success).
- What integration point is silently assumed unchanged but isn't?

**4. Edge-case coverage (all five lenses)**
- Did every lens in *Failure modes* land in requirements, Known limitations & honest gaps, or scope: Failure & scale,
  Operational readiness, Trust boundary, Implied work, Better way?
- Does each surfaced risk carry a decision (HANDLE / ACCEPT / OUT-OF-SCOPE)? Is a lens left blank without
  even a "considered, none apply"?
- What failure mode is unhandled and unmentioned? Name the gap.

**5. Undefended decisions**
- For each load-bearing choice (the approach, the data model, a hard constraint), is there a reason, or is
  it asserted bare?
- Would a competent engineer ask "why this and not X?" and find no answer? Flag choices that need a
  defended rationale or an alternative-rejected note. Do not demand justification for the obvious.

**6. Verification trustworthiness**

Verification is the one place the spec gets concrete: it carries the actual run commands that prove success,
not just prose. Tests are the spec's proof, so hold them to a real standard. Judge whether those commands,
the *Verification approach & commands*, and the success criteria would convince a skeptic:

- **Runnable, not hand-waved:** does the *Verification approach & commands* give the actual commands to run,
  not just a description? Verification with no runnable check is weak.
- **At least one integration test:** when the change has behavior that crosses a real boundary (a database,
  an HTTP call, a queue, a contract between two modules), does the *Verification approach & commands* prove
  at least one path end-to-end across that boundary, rather than leaning entirely on isolated units or
  mocks? A change with real seams and an all-unit, all-mocked verification is weak. Require the crossing be
  proven.
- **Observable end-to-end:** is each `SC-NNN` something an outside observer can check on the running
  system, not a description of an internal mechanism?
- **No leaked HOW as a criterion:** an SC met only by a mechanism ("uses Redis", "the unit test passes") is
  a leaked HOW disguised as an outcome. Flag it, and ask for the observable outcome it stands in for.
- **Each check can actually fail:** would every check flip to failing if the behavior it guards broke? A
  check that passes regardless proves nothing: an assertion on a constant, a mock verifying itself, or a
  *Worked case* whose `Then` values are read back from the thing under test instead of derived independently
  with real numbers.
- **Error and edge paths, not only happy path:** is success defined for the failure and boundary cases the
  risk lenses surfaced, or only for the golden path?
- **Deterministic and reproducible:** does each check give the same verdict every run, or does it ride on
  timing, ordering, network flakiness, or real-world nondeterminism the spec never pins? A check that
  cannot be trusted to repeat is weak evidence.
- **Real coverage:** does an outcome exist for each requirement, and does it pin THAT requirement?

**7. Minimalism: the laziest solution that works**

Climb this ladder and flag the lowest rung the approach skips:
- **Does it need to exist?** Is any requirement speculative, built for a need the Goal doesn't state? YAGNI
  says cut it.
- **Reuse before build.** Does the approach specify building something the codebase already has? Grep to
  confirm, then name what it should reuse.
- **Root cause, not symptom.** For a fix, does the spec patch one path when the fix belongs once in the
  shared place every caller routes through?
- Is the change bigger than the problem? Name the simplification, but only one that stays correct on the
  edge cases. A "minimal" spec that drops input validation, error handling, security, or accessibility is
  broken, not lazy. Do not push those cuts.

**8. Altitude & completeness gate**

- **No HOW leaked.** No file or symbol pinned as content (a pin is allowed only as cited evidence for a
  doubtable *What's true today* fact); no language-typed struct or class block; no task manifest or waves;
  no branch or rollback-script mechanics; no pattern-to-mirror. (Verification run commands are allowed;
  they belong in *Verification approach & commands*.)
- **Every question answered.** No unfilled `< >` placeholder. Every risk lens carries a decision (or
  "considered, none apply"). Timing is complete across the brief's *Rollout / cutover gate* and *Blast
  radius & reversibility* and *When it happens*: triggers, ordering, rollout condition and mechanics,
  reversibility. The brief's *Blocking open questions* and *Open questions & assumptions* are empty, or
  each item is explicitly deferred with a revisit trigger.
- **Every success criterion is testable and technology-agnostic.** (Cross-checks Verification trustworthiness.)

## Output: a structured report

- **Verdict:** APPROVE or REVISE. (REVISE if any BLOCKING finding exists.)
- **BLOCKING**: will cause real harm; must fix before the spec is trusted. Each: dimension · location
  (header / ID / quoted line) · the problem with quoted evidence · why it matters · suggested direction.
- **SHOULD_FIX**: a real weakness; fix unless there's a reason not to. Same shape.
- **SUGGESTIONS**: improvements and nits; optional. Same shape, terse.
- **Success-criteria verdict:** one sentence on whether the outcomes are trustworthy. If not, name the
  single worst offender.
- **What's sound:** two or three lines, so the author knows what NOT to churn.

Do not edit the spec. Report only.
