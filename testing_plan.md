# Testing Plan — Does `create-spec` Actually Produce Better Outcomes?

## Problem

We have a skill (`create-spec`) that generates specs, plus an executor
(`execute-spec`) that implements them. We have **no empirical evidence**
that these specs lead to better outcomes than the `plan.md` Claude
generates by default. Two questions follow:

1. **Efficacy** — "Does this produce better outcomes, or is it just
   burning tokens?"
2. **Component justification** — "Why is each thing in the spec? Is
   there data to support including it vs leaving it out?"

Question 1 is one experiment (a handful of arms, run once). Question 2
is that same test run once per
spec component (~12 ablations), plus interaction effects — so it is
**strictly harder**, and only meaningful if Question 1 is positive.
**Answer Question 1 first.** It gates everything else.

## Scope decision: the skill is domain-general, the mandates are not

The `create-spec` *process* (read code → challenge → pin constraints at
`file:line` → write a verification command) is domain-general — it
applies to kernel/backend work as much as Python/JS. But the
`engineering-mandates` (the quality bar) are ~70% userspace-Python/JS
idioms (asyncio, Pydantic, pip lockfiles) and do not speak kernel C
(errno conventions, RCU/locking, memory barriers).

Consequence for testing: **prove the thesis first in a domain where we
can measure objectively (Python/TS with runnable tests).** If we A/B on
kernel tasks and specs lose, we can't tell "specs don't help" from "the
mandates have nothing to say in C." Treat domain-generality as a
separate, later validation — and note the mandate gap is a real finding
about the skill, not just the test.

---

## The core experiment (Question 1)

A set of arms run under identical conditions, compared pairwise. Each
contrast changes exactly one thing (spec vs no spec; reviewer on vs
off), so the quality gap in that contrast is attributable to that one
thing. The arms and what each contrast isolates are defined in "Arms:
review × artifact" below.

### Setup

1. **Tasks** — ~10 real coding tasks from a well-run Python/TS repo with
   a **runnable test suite**. Each task = `{issue text, the actual
   merged fix, the repo's tests}`. Use the real *issue* as the problem
   statement (not the diff — the diff is the answer and reverse-
   engineering a prompt from it leaks the solution). Prefer
   post-training-cutoff PRs to avoid contamination, or a curated source
   like SWE-bench Verified.
   - Pick tasks where the mandates actually bite (I/O, parsing, error
     handling) — e.g. `httpx`, `pydantic`, `fastapi`, `sqlalchemy`.

2. **Arms per task** (the reviewer is its own component, so we split it
   out — see "Arms: review × artifact" below):
   - **A — Plan (baseline)** — vanilla Claude, told "read the relevant
     code, think hard, write a plan." **Effort-matched**: same model,
     same code access, same thinking budget — just *without* the spec
     structure, the challenge step, and the reviewer. The critical
     control. (A truly-vanilla one-shot `plan.md` would just measure
     "more effort wins," which we already know — we want to isolate the
     *spec*, not the effort.)
   - **C — Spec, reviewer disabled** — `create-spec` produces the spec,
     but the `spec-monkey-spec-reviewer` step is turned off.
   - **D — Full `create-spec`** — spec + reviewer. The shipping product.
   - **B — Plan + review (optional)** — arm A's plan run through an
     *analogous* generic critique-and-revise pass. Add only to test "is
     the value just having an agent review anything?"

3. **Execution** — hand each artifact to the **same** executor. Run each
   arm **N ≥ 5 times** per task (outputs are stochastic; one run proves
   nothing).

### Arms: review × artifact (what each contrast buys)

`create-spec` bundles two things the baseline lacks: the spec
**structure/process** and a **reviewer** pass. Whether including the
reviewer is "unfair" depends on the claim:

- *"My product beats plain plan mode"* → **A vs D** is fair and honest
  (product vs default; the reviewer ships as part of the product).
- *"The spec format is what helps"* → the reviewer is a confound and
  must be held constant.

So the reviewer is just another component. Lay it out as a 2×2 (this is
**review × artifact** — a different 2×2 than spec-vs-execution below):

|            | no review | + review-and-revise |
|------------|-----------|---------------------|
| **plan**   | A — bare plan | B — plan + reviewer |
| **spec**   | C — spec, reviewer off | D — full `create-spec` |

- **A vs D** — honest product comparison (shipping thing vs default).
- **A vs C** — the spec format *alone* (reviewer removed): the fair "is
  the structure better" test.
- **C vs D** — what the reviewer adds *on top of* a spec.
- **A vs B** — does review alone, on a plain plan, capture the value?

**First run: 3 arms — A, C, D.** One run yields the product comparison
(A vs D), the spec-isolated comparison (A vs C), AND the reviewer's
marginal value (C vs D). Add **B** later to test the "it's just the
review" hypothesis directly.

Each contrast is scored with the pairwise method below (5 × 5 = 25
matchups × both orders); pass-rate is computed per arm. Three arms =
three pairwise contrasts (A–C, A–D, C–D).

**Wrinkle:** `spec-monkey-spec-reviewer` is specialized for specs (it checks
vague constraints, weak verification, untestable NFRs — sections a plain
plan lacks). You can't bolt the identical agent onto the plan; B uses an
*analogous* generic review pass, recorded as an analog, not an identical
control.

### Interactivity — both arms must be treated identically

Both arms can pause to ask the user questions: `create-spec` has a
challenge conversation, and Claude's plan mode sometimes asks for
clarification. A live human answering breaks reproducibility and makes
*the human's answers* part of what's measured — and an unfair confound
if one arm gets richer answers than the other.

**Rule: whatever you do about interaction, apply it identically to both
arms.** Letting the spec arm have a rich conversation while the plan arm
runs cold measures "conversation vs none," not the skill.

**Option A — Suppress (both arms one-shot).** Add to both prompts: *"You
may not ask the user anything. Where you'd ask, state the assumption
you're making and proceed."* Reproducible, symmetric, matches the
one-shot decision. Note the handicap is **not** symmetric — `create-spec`
is built around its conversation, so suppressing it hurts the spec arm
more; a win under A is therefore a *strong* result. Bonus: the
assumptions each arm writes down become inspectable artifacts.

**Option B — Simulate the user (both arms talk to the same bot).** A
user-agent holds the task's *intent* (requirements/acceptance criteria
from the issue — **never the diff**) and answers either arm's questions
in character, consistently. Tests the full skill, including whether
`create-spec` asks better questions. Trap: the simulator must know
*what* the user wants, never *how* to build it — if it leaks the accepted
solution, both arms are contaminated.

**Recommendation:** start with **A** (isolates the spec artifact from the
interaction; matches the one-shot choice). Later run **B**; **B − A = the
value of the interaction itself**, separate from the artifact.

**Always log** every question asked, assumption stated, and (in B) answer
given — raw material for rationale-mining.

### Runs (how many outputs, and why)

Everything below is **per task** (we have ~10 tasks total).

- Run **each arm 5 times**. With the first-run set (A, C, D) that's
  **15 code outputs per task** (5 × 3 arms).

Why 5 each: the executor is **random** — one run could be a lucky or
unlucky draw. Five runs *samples the distribution* of what each arm
typically produces. The 5 runs are NOT "5 scores"; they are 5 samples
of each arm's behavior.

### Scoring — two separate numbers, don't blend them

We measure each task two ways. Keep them distinct.

**1. Pass-rate (objective correctness).** Each output either passes the
repo's tests or not. Count per arm (each arm has 5 runs).
- Example: D passes 4 of 5, A passes 3 of 5.
- This is the objective floor: does the code actually work.

**2. Win-rate (pairwise quality).** This is **comparisons, not
per-output scores.** The judge never scores one output alone — it always
sees **one output from each of the two arms in a contrast** (e.g. an A
output next to a D output) and picks the better one. (Absolute scoring was rejected: it's noisy and the judge anchors
poorly with nothing to compare against.)

How to pair 5 vs 5:
- **Compare all pairs:** 5 × 5 = **25 matchups** per contrast.
  (Don't pair them 1-to-1 — the pairing would be arbitrary.)
- **Run each matchup in both orders** to cancel the judge's position
  bias → **50 judge calls per contrast, per task**.
- **Win-rate** = one arm's share of those 50 calls.
  - Example (A vs D): D wins 36 of 50 → **72%** on that task.
- With the first-run set you score **three contrasts** (A–C, A–D, C–D),
  so 150 judge calls per task.
- The judge is **blind** (doesn't know which arm is which) and
  **anchored on the mandate rubric** (or a domain-appropriate quality
  rubric), so "better" means something consistent.

Per-task summary, the two numbers side by side:

| Metric | What it measures | Example (one task, A vs D) |
|---|---|---|
| **Pass-rate** | does the code work (objective) | D 4/5 vs A 3/5 |
| **Win-rate** | which output is better (quality) | D 72% (36 of 50 matchups) |

### Aggregating across the 10 tasks

Aggregate **per contrast**, across all 10 tasks:
- **Headline win-rate** = average the per-task win-rates for that
  contrast → e.g. "for A vs D, the spec output is preferred ~70% of the
  time."
- **Headline pass-rate** = each arm's total passes across all tasks →
  e.g. "D passes as often or more than A."

Read them together: pass-rate is the objective floor (does it work),
win-rate is the quality signal on top (is it better). A clear win needs
the spec to be **at least as correct AND meaningfully preferred**.

### Stop / scale rule

10 tasks × N runs only detects a *large* effect. If the result is
ambiguous, add tasks before concluding. Don't read signal into a margin
the sample can't support.

### What the outcome shows

Read it by contrast:
- **A vs D (product)** — does the shipping workflow beat plain plan
  mode? The headline question.
- **A vs C (spec format)** — if C beats A, the spec *structure* carries
  value on its own. If C ≈ A, the structure alone isn't the lever.
- **C vs D (reviewer)** — if D beats C, the reviewer is doing the work;
  "what's in the spec" matters less than "what the reviewer fixes."

Overall reads:
- **Clear win (D ≫ A)** → the workflow earns its tokens. Use A–C and
  C–D to see *where* the value lives, then Question 2 to go finer.
- **Tie (D ≈ A)** → mostly burning tokens. Trim (Question 2) or
  reconsider.
- **Loss (D < A)** → the structure is actively hurting (over-
  constraining, misdirecting). Most important to learn early.

### The one caveat (don't forget this)

This test only measures **the code that comes out.** Half the spec (Why,
Alternatives, Current behavior — everything *above* the "Implementation
contract" divider) exists so a **human can reject a bad approach before
any code is written.** This test is blind to that value. So a "tie"
does NOT mean those sections are useless — it means their value lives in
the review gate, which needs a *separate* test (do reviewers make better
approve/reject calls with vs without them?).

---

## Question 2 (only if Question 1 is positive): what in the spec made the difference?

The goal: produce data for each spec component, and **delete the ones
without data** — applying the skill's own Deletion mandate to the
template itself. A leaner, evidence-backed spec is the strongest answer
to the "you're just burning tokens" critique.

Work cheapest → most expensive. Each layer *targets* the next, so you
never run an expensive ablation you didn't need.

### Layer 0 — Which big lever? (free, already in your data)

Before looking *inside* the spec, the A/C/D contrasts already partition
the value:
- **C ≈ A but D ≫ C** → the difference isn't "in the spec" — it's the
  **reviewer**. The right question becomes "what does the reviewer fix,"
  not "what's in the spec."
- **C ≫ A** → the spec *content* is carrying it; open the spec.

This decides whether to even look inside.

### Layer 1 — Rank the suspects (free, correlational)

Mine the pairwise judge's *written reasons* across every matchup the
spec arm won. Tally the themes ("handled the error path," "respected the
unbounded-input constraint," "matched the existing pattern") and map
each back to the spec section that plausibly caused it → a **ranked
hypothesis list** of which sections matter, for free.

- **Trap:** this is correlation, not causation. *Every* spec has a
  Constraints section, so "the winners all had Constraints" proves
  nothing on its own. Layer 1 *ranks* suspects; it can't convict them.

### Layer 2 — Convict the suspects (expensive, causal)

For the top-ranked sections **only**, ablate: full-spec vs
spec-with-that-section-removed, same harness, measure the
win-rate/pass-rate delta. Two refinements that make this far more
informative:

- **Degrade, don't just delete.** Replace specific `file:line`
  constraints with *vague* ones. If quality drops, it's the
  **specificity** that matters — not the section's mere presence. Far
  more actionable.
- **Diff the outputs, don't just score.** When pulling a section drops
  quality, *diff* the resulting code against the full-spec runs to see
  the **mechanism** ("removed Constraints → executor dropped the
  timeout"), not just the magnitude. The mechanism tells you how to
  rewrite the skill.

### Layer 3 — Don't mis-measure the human-facing half

(Per the template's two-audience design, split at the "Implementation
contract" divider.)
- **Executor-facing** (Constraints, Do NOT, Files that matter,
  Verification) → judge by **output quality** (the harness above).
- **Human-facing** (Why, Current behavior, Alternatives, Edge cases,
  Approach) → their value is in *review decisions*, invisible to output
  ablation; needs a **separate review-decision test** (do reviewers make
  better approve/reject calls with vs without them?).

### Three honest possible answers ("if at all")

1. **One section dominates** → trim the rest, ship a leaner spec.
2. **It's diffuse** → no single section moves the needle, but several
   together do; the *structured package* is the value. Harder to act on.
3. **It's not the content** → it's the reviewer (Layer 0) or the act of
   forcing code-reading; "what's in the spec" was the wrong frame.

---

## Extension: where does the value come from — spec or execution? (2×2)

A **separate, later** decomposition. Its cell labels (I–IV) are local to
this table — don't confuse them with arms A–D above. If we want to
attribute value to the spec artifact vs the `execute-spec` enforcement:

|            | default execution | execute-spec |
|------------|-------------------|--------------|
| **plan**   | I — true baseline | II — does the executor help a plain plan? |
| **spec**   | III — does the spec help with vanilla execution? | IV — full workflow |

- **IV − I** = total lift · **III − I** = spec artifact alone · **II − I**
  = executor alone · interaction if (IV−I) > (III−I)+(II−I).
- "Focus on the spec" = the **III-vs-I** column; run that slice first.
- Caveat: cell II is semi-degenerate (`execute-spec` expects spec
  structure), so feeding it a plain plan tests it off-distribution.

---

## Sequence

1. **Question 1** — the core A/B. Cheap, gates everything, and it's the
   one that could tell us to stop. Do it first.
2. **Rationale mining** — free byproduct of step 1; targets step 3.
3. **Question 2 ablations** — only if step 1 is positive; only on
   flagged components; split executor-facing vs human-facing.
4. **2×2 / domain-generality** — later, once the core thesis holds.
