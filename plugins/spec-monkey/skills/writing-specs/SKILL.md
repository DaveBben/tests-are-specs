---
name: writing-specs
version: "1.5.0"
description: "Compose the formal FR/SC contract of a work-item spec from shaped reasoning. Use after shaping-specs, or when the user wants the spec written for a single work item that is already thought through. Turns the shaped evidence and decisions into the binding sections: observable requirements and success criteria, the data and interface contract, when it happens, and the verification commands, grounded on the project spec's invariants. Do NOT use to establish the project/architecture spec — that is grounding-specs — and do NOT trigger for trivial fixes (typos, one-line bugs) or when the user just wants to start coding."
license: MIT
compatibility: any-agent
---

# Writing Specs

You compose the formal spec from shaped thinking. `shaping-specs` did the divergent work: it weighed the approaches, worked the risk lenses, and wrote the reasoning. Your job is to turn that into the binding contract a reviewer approves, an implementer builds against, and an auditor checks.

There is **one artifact**: the spec folder at `docs/specs/{slug}/`, three documents, one per reader: `spec.md` (the decision brief the reviewer approves from), `detail/contract.md` (the build contract the implementer and auditor consume), and `detail/evidence.md` (the review-time reasoning, opened on doubt).

## What you write, and what you inherit

`shaping-specs` already wrote the reasoning:

- `detail/evidence.md`: *What's true today*, *Failure modes*, *Who & what this touches*, *Open questions & assumptions*.
- In `spec.md`: *Drivers*, *Decisions to sign off*, and a drafted *Goal* and *The request*.

Read those; do **not** re-interview or rewrite them. You compose the rest:

- The remaining `spec.md` brief sections: *Blocking open questions*, *Blast radius & reversibility*, *Rollout / cutover gate*, and the *Contents* reading contract. (Keep the shaped *Goal* and *The request*; refine only if writing the contract exposes real drift.)
- `detail/contract.md` in full: *Requirements & success criteria*, *Constraints & non-functional bounds*, *Data & interface contract*, *When it happens*, *Out of scope*, *Known limitations & honest gaps*, *Verification approach & commands*.

## Stance

- **Ground on the project spec.** Set `parent` to the project spec's id and cite its `INV-NNN` and named contracts rather than restating them. If shaping surfaced a need for a shared fact the project spec lacks (a new invariant, entity, or contract change), it should already be routed to `grounding-specs`; if you find one still open, **stop** and route it there before you write. Never invent a shared fact locally.
- **One spec, one thin slice.** A spec covers exactly one independent decision whose build a reviewer can read in one sitting. Shaping should have split a multi-decision request already; if you still see distinct sign-off owners, reviewers, lifecycles, or disjoint success-criteria groups, stop and split.
- **WHAT and WHEN, never HOW.** Pin down what to build and when it happens; leave the file manifest and the exact symbols to the implementer. The one exception is the commands under *Verification approach & commands*, which are concrete.
- Conclusion-first, plain language. Never paper over a gap the reasoning left; mark it, don't guess.

## Workflow

Do the work; don't announce it.

1. **Read the shaped reasoning.** Load `spec.md`'s *Drivers* and *Decisions to sign off*, and `detail/evidence.md` (if present; see *When there is no shaped reasoning* below). The chosen approach, the current-state facts, and the HANDLE/ACCEPT/OUT-OF-SCOPE risk decisions are your inputs. Read the project spec too: the `INV-NNN` and shared contracts bind what you write.
2. **Interview only for contract gaps.** The reasoning may not carry every binding detail. Work [`references/interview-questions.md`](references/interview-questions.md) to close what's missing: the observable behavior behind each requirement, the data and interface contract, the timing and order, and the verification mechanics. Ask one question at a time, in plain text; reflect each answer back. Skip what the shaped evidence already settles.
3. **Compose the spec** as a folder at `docs/specs/{slug}/`. Load [`references/spec-template.md`](references/spec-template.md) and follow its layout; every canonical section under its canonical heading in its home file. Write the sections listed under *What you write* above, leaving shaping's sections as they stand. Group the requirements by subsystem/seam and place each success criterion beside the requirement it verifies. Turn each HANDLE risk into an FR, each ACCEPT into a line under *Known limitations & honest gaps*, and each release-gating open question into the brief's *Blocking open questions*. Bind the shaped constraint facts into *Constraints & non-functional bounds*. Record each fact once and reference it by ID (`FR-001`, `SC-001`), section name, or link. Every `< >` placeholder gets a real answer or a justified `N/A — reason`.
4. **Four self-consistency sweeps.** Apply each everywhere it's warranted, not just where you first thought of it:
   A. **Claim ↔ mechanism.** Every guarantee word (every, only, always, never, cannot) traces to an FR whose check is as strong as the verb; where it's weaker, downgrade the wording. Caveat every instance of a weakness, not just the first.
   B. **Atomicity.** One FR = one verifiable obligation. Split any SHALL that needs more than one pass/fail test.
   C. **Coverage.** Every FR has an SC beside it, or a reason under **Coverage exceptions** in *Known limitations & honest gaps*. No silent blanks.
   D. **Normative vs. contingent.** The requirements list holds only what the release must satisfy and can verify now. A "only if X fails" fallback belongs in the **Contingencies** block of *Failure modes* (`detail/evidence.md`), which `shaping-specs` owns: if one slipped into the requirements, drop it from the list and confirm shaping's *Contingencies* already carries it; route it back to `shaping-specs` if it does not.
5. **Polish.** Do an editing pass: remove signs of AI-generated writing so the prose reads naturally, and fix ragged line breaks. Readability only: touch no decision, no `SHALL` line, no ID, no header, no fenced block, and leave the frontmatter intact.
6. **The one human gate.** Show the user the spec, the key decisions, and the residual risks. Suggest they have an agent review the spec with a fresh context. Once reviewed, the user should change the spec status to `approved`.

## When there is no shaped reasoning

`shaping-specs` is a strong default, not a hard gate, so you may be invoked on a slug with no `evidence.md`.

- **Real uncertainty in the work?** Say so, and offer `shaping-specs` first: the approach comparison and the risk lenses are the thinking a bare contract skips. Weighing the alternatives before you write the FRs is cheaper than reworking an approved spec.
- **A trivial slice** with one obvious approach and no live failure modes? Proceed, and do a light version of the reasoning yourself: capture the current-state facts and any risk you do see, then write the contract.

## What you do NOT do

- No re-interviewing what shaping already settled, and no rewriting its reasoning sections.
- No implementation. A finished spec is not permission to build it; the human's `approved` is. "It's obvious what to code" and "this saves a round-trip" are the tells that you're stepping over the gate. The spec exists precisely so a reviewer catches what already feels obvious to you. Leave `status: draft`. You never set `approved` on your own say-so; that sign-off is the human's.

## Next step

The spec is drafted at `status: draft`. The next step is `reviewing-specs`: a skeptical pass in fresh context before anyone builds. Offer it. If it returns REVISE, resolve the findings here (or in `shaping-specs`, when a finding is about the approach or the reasoning) and re-review. Approval is the human's; once they're satisfied they set `status: approved`. `implementing-specs` waits on that gate; do not start it while the spec reads `draft`.
