---
name: writing-specs
version: "1.11.1"
description: "Compose the formal FR/SC contract of a work-item spec from shaped reasoning. Use after shaping-specs, or when the user wants the spec written for a single work item already thought through. Turns the design into the binding sections: requirements and success criteria, the data and interface contract, when it happens, and the verification commands, grounded on the project spec. Do NOT use to establish the project/architecture spec (that is grounding-specs), and do NOT trigger for trivial one-line fixes or when the user just wants to start coding."
license: MIT
compatibility: any-agent
---

# Writing Specs

You compose the formal spec from shaped thinking, into the binding contract a reviewer approves, an implementer builds against, and an auditor checks.

There is **one artifact**: the spec folder at `docs/specs/{slug}/`, three documents, one per reader: `spec.md` (the decision brief the reviewer approves from), `detail/contract.md` (the build contract the implementer and auditor consume), and `detail/design.md` (the review-time reasoning, opened on doubt).

## What you write, and what you inherit

The reasoning already exists in `detail/design.md`, shaping-specs' output: *The request*, *Goal*, *Drivers*, *What's true today*, *Approach*, *Failure modes*, *Verification strategy*, *Who & what this touches*, and *Open questions & assumptions*. Read it (and the project spec); do **not** re-interview or rewrite it. You compose `spec.md` and `detail/contract.md` from it:

- `spec.md`, the whole decision brief: carry *The request*, *Goal*, and *Drivers* over from the design (refine only if writing the contract exposes real drift); turn the design's *Approach* into *Decisions to sign off* (the calls a human signs); promote the release-gating items from *Open questions & assumptions* into *Blocking open questions*; write *Blast radius & reversibility*, *Rollout / cutover gate*, and the *Contents* reading contract.
- `detail/contract.md` in full: *Requirements & success criteria*, *Constraints & non-functional bounds*, *Data & interface contract*, *When it happens*, *Out of scope*, *Known limitations & honest gaps*, *Verification approach & commands*.

## Stance

- **Ground on the project spec.** Set `parent` to the project spec's id and cite its `INV-NNN` and named contracts rather than restating them. If a shared fact the project spec lacks is still open (a new invariant, entity, or contract change), **stop** and route it to `grounding-specs` before you write. Never invent a shared fact locally.
- **One spec, one thin slice.** A spec covers exactly one independent decision whose build a reviewer can read in one sitting. If you see distinct sign-off owners, reviewers, lifecycles, or disjoint success-criteria groups, stop and split.
- **WHAT and WHEN, never HOW.** Pin down what to build and when it happens; leave the file manifest and the exact symbols to the implementer. The one exception is the commands under *Verification approach & commands*, which are concrete.
- Conclusion-first, plain language. Never paper over a gap the reasoning left; mark it, don't guess.

## Workflow

Do the work; don't announce it.

1. **Read the shaped reasoning, and check the design gate.** Load `detail/design.md` (if present; see *When there is no shaped reasoning* below). If it exists, its `status` must read `approved`: the design gate comes before the contract. If it still reads `draft`, stop — route it through `reviewing-design` and the human's design approval first, then resume. Then read it: *The request*, *Goal*, and *Drivers* frame the brief; *Approach* is the chosen design and the alternatives weighed; *What's true today* and *Failure modes* carry the current-state facts and the HANDLE/ACCEPT/OUT-OF-SCOPE risk decisions; *Verification strategy* is the prose you turn into concrete commands. Read the project spec too: the `INV-NNN` and shared contracts bind what you write.
2. **Interview only for contract gaps.** The reasoning may not carry every binding detail. Work [`references/interview-questions.md`](references/interview-questions.md) to close what's missing: the observable behavior behind each requirement, the data and interface contract, the timing and order, and the verification mechanics. Ask one question at a time, in plain text; reflect each answer back. Skip what the shaped design already settles.
3. **Compose the spec** as a folder at `docs/specs/{slug}/`. Load [`references/spec-template.md`](references/spec-template.md) and follow its layout; every canonical section under its canonical heading in its home file. Write `spec.md` and `detail/contract.md` (the sections under *What you write* above), and leave `detail/design.md` as shaping wrote it. Group the requirements by subsystem/seam and place each success criterion beside the requirement it verifies. Turn each HANDLE risk into an FR, each ACCEPT into a line under *Known limitations & honest gaps*, and each release-gating open question into the brief's *Blocking open questions*. Bind the shaped constraint facts into *Constraints & non-functional bounds*. Record each fact once and reference it by ID (`FR-001`, `SC-001`), section name, or link. Every `< >` placeholder gets a real answer or a justified `N/A — reason`.
4. **Polish.** Do an editing pass: remove signs of AI-generated writing so the prose reads naturally, and fix ragged line breaks. Readability only: touch no decision, no `SHALL` line, no ID, no header, no fenced block, and leave the frontmatter intact. The self-consistency sweep — claim↔mechanism, atomicity, coverage, contingency placement — is `reviewing-specs`' job now, run in fresh context; compose cleanly, but don't self-grade it here.
5. **The one human gate.** Show the user the spec, the key decisions, and the residual risks. Suggest a fresh-context review first (see *Next step*). Approval is the human's decision, and only theirs — but you may record it for them. When they give an explicit, unsolicited go-ahead ("approve it", "looks good, ship it"), restate the decisions and residual risks they're signing off on one last time, then record the gate: set `status: approved`, and fill `approved_by` with their handle and `approved_date` with today's date. That record is what lets a later audit tell a human-granted gate from a self-set flip, so it is not optional once you write `approved`. Never approve on your own judgment, never read approval into silence or a vague "looks good" aimed at something else, and never nudge them toward it. If you had to argue them into it, it isn't their gate anymore.

## Amending an approved spec

An approved spec is a contract the human signed. Changing it after approval follows the same discipline as a project-spec amendment, scaled to one work item. This is where the `status` line runs backward. It happens when the audit tags a deviation `amend-spec` (the contract is wrong, not the code), or when the build or review reveals the approved contract is incomplete or out of step with reality.

- **Status regresses.** Set `status` back to `draft`, and clear `approved_by` and `approved_date`. `approved` records that the human signed *these* obligations; once you change them, that signature no longer covers the spec, and the gate record has to be re-earned along with the status. Don't rewrite the sections it guaranteed while it still reads `approved`.
- **Re-scope the review by the change.** A material change — an FR added, removed, or reworded; an SC weakened; a data-contract, timing, or scope change — re-enters `reviewing-specs` and a fresh human gate. A cosmetic fix that changes no obligation (a typo, a broken link, a clarifying rewrite) does not; note it and move on.
- **Built code goes stale.** Code built against the old contract is now unproven against the new one. Every FR whose obligation changed goes back through `implementing-specs` and the audit; the untouched FRs stand. Say which is which.
- **A shared fact is not yours to change here.** If the amendment is a new invariant, a shared entity, or a cross-work-item contract change, route it to `grounding-specs` as a project-spec amendment first, then flow the result back down.
- **Large enough to be a new decision?** If the change would rewrite the contract past recognition, write a successor spec instead of mutating this one: set the new spec's `supersedes` to this spec's id and mark this one `archived`. Delta lineage over an unrecognizable diff.

## When there is no shaped reasoning

You may be invoked on a slug with no `design.md`.

- **The user has a written brief or PRD?** Ingest it before you write, the same way `shaping-specs` would: read it, map what it settles, mark what you inferred as an assumption, and confirm the extraction. The method is in [`../shaping-specs/references/ingesting-briefs.md`](../shaping-specs/references/ingesting-briefs.md). A brief that carries real uncertainty about the approach still wants a shaping pass; a brief that settles it lets you go straight to the contract with the residual gaps confirmed.
- **Real uncertainty in the work?** Say so, and offer `shaping-specs` first: the approach comparison and the risk lenses are the thinking a bare contract skips. Weighing the alternatives before you write the FRs is cheaper than reworking an approved spec.
- **A trivial slice** with one obvious approach and no live failure modes? Proceed, and do a light version of the reasoning yourself: capture the current-state facts and any risk you do see, then write the contract.

## What you do NOT do

- No implementation. A finished spec is not permission to build it; the human's approval is. "It's obvious what to code" and "this saves a round-trip" are the tells that you're stepping over the gate. The spec exists precisely so a reviewer catches what already feels obvious to you. Until the human gives an explicit go-ahead, the spec stays `draft`. You may write `approved` only to record their decision, never on your own say-so.

## Next step

The spec is drafted at `status: draft`. The next step is `reviewing-specs`: a skeptical pass in fresh context before anyone builds. Fresh context is a clean slate that hasn't watched you write the spec. If you are able to dispatch subagents, dispatch a reviewer given only the spec folder path and told to run `reviewing-specs`; otherwise open a new session with an empty context and point it at the spec path. Either way the reviewer starts from the spec, not from your authoring context. Offer it. If it returns REVISE, resolve the findings here (or in `shaping-specs`, when a finding is about the approach or the reasoning) and re-review. Approval is the human's decision; once they give it, you record `status: approved` for them (step 6). `implementing-specs` waits on that gate; do not start it while the spec reads `draft`.
