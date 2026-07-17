# Review rubric (the contract)

Work through the sweep and each dimension. Cite evidence for every finding: a section header name, an ID (`FR-NNN` / `SC-NNN`), or a quoted line. If you can't cite it, it isn't a finding. The design and the approach were judged already by `reviewing-design`; here you judge the **binding contract** — `spec.md` plus `detail/contract.md`.

## Contents

- [The altitude contract (what the contract is)](#the-altitude-contract-what-the-contract-is)
- [The self-consistency sweep (check first)](#the-self-consistency-sweep-check-first)
- [Contract review dimensions](#contract-review-dimensions)
- [Output: a structured report](#output-a-structured-report)

## The altitude contract (what the contract is)

A spec states **WHAT to do and WHEN, never HOW.**

- **WHAT / WHEN belongs:** observable behavior, requirements, triggers, ordering, rollout conditions, reversibility, external contracts, success criteria. Everything a human signs off on.
- **HOW never belongs:** which file or symbol to edit, the algorithm, the concrete type or struct, the branch, the rollback script, the task breakdown. The implementer owns all of it. The one exception is verification: the run commands that prove success DO belong, under *Verification approach & commands* (in `detail/contract.md`).
- **Litmus:** if a line tells an implementer which file, symbol, or type to edit, it's a leaked HOW. A reviewer approves direction, not line edits.

Judge the **engineering**, not the prose polish. But a formatting problem is fair game where it would mislead a builder: a duplicated decision that will drift, a requirement hiding implementation trivia, a broken FR→success-criterion trace.

## The self-consistency sweep (check first)

The recurring within-spec defect is **inconsistent application of the spec's own standards**: doing the right thing in one place and skipping it in an identical one. Look for these six early; each is a finding under the normal evidence rule and feeds the same severity buckets as the dimensions.

- **S1: Claim stronger than its mechanism.** A guarantee word (every, only, always, never, cannot) in the Goal, a *Decisions to sign off* line, or an FR rationale, but the enforcing FR checks something weaker. Name the FR; downgrade the wording or strengthen the check. Call out every uncaveated instance, not just the first.
- **S2: Non-atomic requirement.** An FR you can't settle with a single pass/fail test: "and"-joined or carrying a list. Split it into one obligation per FR.
- **S3: Unverified requirement.** Every FR connects to an `SC-NNN` (or the worked case), and each SC states a measurable outcome. An FR with no SC and no declared gap, or a "must preserve" behavior with no dedicated SC, is a blocking gap.
- **S4: Contingency in the normative list.** A requirement that applies "only if X fails" belongs in *Contingencies* (in `detail/design.md`), not the requirements list.
- **S5: Restated fact.** The same fact near-verbatim in 3+ places instead of stated once and referenced by ID. Name the canonical home and the copies. A shared fact copied from the project spec (an `INV-NNN`, a shared entity) instead of cited by ID is the same defect across documents: cite it, don't restate it.
- **S6: Internal contradiction.** A value stated two ways, or an assumption that fights a requirement. Name both sides of the conflict.

If the contract has grown a **second independent decision** the design didn't carry — distinct sign-off clusters, distinct reviewers, or success criteria that partition into disjoint groups — that is a BLOCKING finding to split it, routed back through `reviewing-design`. (Decomposition is design review's gate; you only catch what leaked past it.)

## Contract review dimensions

**1. Verification trustworthiness**

Verification is the one place the spec gets concrete, carrying the actual run commands that prove success. Tests are the spec's proof; hold them to a standard that would convince a skeptic:

- **Runnable, not hand-waved:** does *Verification approach & commands* give the actual commands to run, not just a description? Verification with no runnable check is weak.
- **At least one integration test:** when the change crosses a real boundary (a database, an HTTP call, a queue, a contract between two modules), does it prove at least one path end-to-end across it, not lean entirely on isolated units or mocks? Require the crossing be proven.
- **Observable, not a mechanism:** is each `SC-NNN` something an outside observer can check on the running system, not an internal mechanism? An SC met only by a mechanism ("uses Redis", "the unit test passes") is a leaked HOW disguised as an outcome; ask for the observable outcome it stands in for.
- **Each check pins its requirement and can actually fail:** an outcome exists for each requirement and pins THAT requirement, and every check would flip to failing if the behavior it guards broke. A check that passes regardless proves nothing: an assertion on a constant, a mock verifying itself, or a *Worked case* whose `Then` values are read back from the thing under test instead of derived independently with real numbers.
- **Error and edge paths, not only happy path:** is success defined for the failure and boundary cases the risk lenses surfaced, or only for the golden path?
- **Deterministic and reproducible:** does each check give the same verdict every run, or does it ride on timing, ordering, or network flakiness the spec never pins? A check that cannot be trusted to repeat is weak evidence.

**2. Altitude & completeness gate**

- **No HOW leaked.** No file or symbol pinned as content (a pin is allowed only as cited evidence for a doubtable *What's true today* fact); no language-typed struct or class block; no task manifest or waves; no branch or rollback-script mechanics; no pattern-to-mirror. (Verification run commands are allowed; they belong in *Verification approach & commands*.)
- **Every question answered.** No unfilled `< >` placeholder. Timing is complete across the brief's *Rollout / cutover gate*, *Blast radius & reversibility*, and *When it happens*: triggers, ordering, rollout condition and mechanics, reversibility. The brief's *Blocking open questions* are empty, or each item is explicitly deferred with a revisit trigger.
- **Every success criterion is testable and technology-agnostic.** (Cross-checks Verification trustworthiness.)
- **Grounded on the project spec.** If the spec names a `parent`, it resolves to a real project spec; every invariant or shared contract it leans on is cited by `INV-NNN`/name, not restated; and no fact that belongs to the whole system is defined locally. A locally-invented shared fact is a BLOCKING finding: it belongs in the project spec by amendment.

## Output: a structured report

- **Verdict:** APPROVE or REVISE. (REVISE if any BLOCKING finding exists.)
- **BLOCKING**: will cause real harm; must fix before the spec is trusted. Each: dimension · location (header / ID / quoted line) · the problem with quoted evidence · why it matters · suggested direction.
- **SHOULD_FIX**: a real weakness; fix unless there's a reason not to. Same shape.
- **SUGGESTIONS**: improvements and nits; optional. Same shape, terse.
- **Success-criteria verdict:** one sentence on whether the outcomes are trustworthy. If not, name the single worst offender.
- **What's sound:** two or three lines, so the author knows what NOT to churn.

Do not edit the spec. Report only.
