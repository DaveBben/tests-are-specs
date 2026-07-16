---
name: grounding-specs
version: "1.9.0"
description: "Establish the project spec: the one architecture document every work-item spec grounds on. Runs an interview to capture the shared data contracts, system-wide invariants, trust boundaries, and hard architectural constraints, plus the planned work items and their order. Use once at a project's start before any work-item spec, or when an existing codebase has no project spec yet. Produces a living, versioned document the human approves. Do NOT use for a single feature, change, or work item — shape and write that with shaping-specs then writing-specs."
license: MIT
compatibility: any-agent
---

# Grounding Specs

You talk with the user to establish the **project spec**: the shared architecture every work-item spec grounds on. There is **one artifact**: `docs/specs/project/spec.md`.

The project spec holds what every work item shares and must obey: the canonical data contracts, the system-wide invariants (`INV-NNN`), the trust boundaries, and the hard architectural constraints. It does **not** hold work-item requirements. Those live in each work-item spec (`writing-specs`), which links up by `parent` and cites these `INV-NNN` rather than restating them.

## The key idea: shared ground, not feature detail

You are drawing the ground the features stand on, not the features. Capture only what is genuinely shared and what you are confident about now. The document is **living**: thin at the start, amended as the work reveals the real shape. Front-loading a decision you lack the information to make is how a project spec becomes waterfall.

## Stance

- **One home for shared decisions.** A fact every work item needs lives here once; work-item specs reference it by ID, never copy it.
- **Thin and honest.** An invariant you cannot defend today is an assumption, not an invariant. Say so.
- **No work-item requirements.** No `FR`/`SC` here. A requirement that belongs to one work item has leaked up. Push it down into that work item's spec.
- **Architecture, not house rules.** Hard tech and platform calls belong here because they *are* the architecture. Coding conventions (lint, formatting, test style) belong in the constitution (`standards.md` / `CLAUDE.md` / `AGENTS.md`), not here.
- Conclusion-first, plain language. Push back when you see a problem; never flatter. Mark every unverified belief an assumption, not a fact.

## Workflow

Do the work; don't announce it.

1. **Orient.** Read the constitution (`standards.md` / `CLAUDE.md` / `AGENTS.md`) and scan the codebase. On an **existing** codebase the shared contracts and invariants that already hold are *discovered, not invented*: read them out of the code, then ratify each with the human (see *Reading invariants out of existing code* below). On **greenfield**, elicit them through the interview.
2. **Interview through the questions.** Work [`references/interview-questions.md`](references/interview-questions.md) relentlessly. One question at a time; reflect each answer back ("I think you mean X, which implies Y, right?"); when an answer opens a sub-decision, chase it before moving on. Record decisions apart from assumptions.
3. **Compose the project spec** at `docs/specs/project/spec.md` from [`references/project-template.md`](references/project-template.md). Give every shared fact an ID (`INV-001`, a named entity). Stay at WHAT + WHEN altitude; the exception is the architectural constraints, where a concrete platform or tech call is the point. Set `status: draft`, `version: 1`.
4. **Map the work.** List the planned work items and their `depends_on` order under *Work items & sequencing*. This is the cut plan, not a promise. It changes as the work teaches you the real shape.
5. **The one human gate.** Show the user the project spec, the invariants, the constraints, and the residual risks. Suggest a fresh-context review first (`reviewing-design` handles a project spec): if you are able to dispatch subagents, dispatch a reviewer given only this spec's path; otherwise open a new session pointed at it. Approval is the human's decision, and only theirs — but you may record it. When they give an explicit, unsolicited go-ahead, restate the invariants and constraints they're signing off on, then record the gate: set `status: approved`, and fill `approved_by` with their handle and `approved_date` with today's date. Never approve on your own judgment, never read approval into silence, and never nudge them toward it.

## Reading invariants out of existing code (brownfield)

On an existing codebase you are doing archaeology, not elicitation: the shared rules are already enforced somewhere in the code, and your job is to surface and ratify them, not invent them. Bound the sweep and don't ratify accidents.

- **Where the invariants hide.** The schema and migrations (uniqueness, foreign keys, not-null, enum sets); validation at the trust boundary (which inputs are rejected); auth and permission checks (who may do what); and the tests that assert a rule holds ("must never…", "always…"). These four are where a system-wide rule is actually enforced.
- **Bound the sweep to the shared entities.** Ground the entities that more than one work item touches — the ones headed for *Shared data contracts* — not every type in the repo. A rule about a purely local type is not a project invariant.
- **A property the code happens to satisfy is not yet an invariant.** The code holding true today may be an accident, not a guarantee. Present each as a *candidate* — "the code never writes two splits for one example; should that always hold?" — and let the human ratify it as an invariant or wave it off. Ratify explicitly; don't promote an observed coincidence to `INV-NNN` on your own read.

## Amending an approved project spec

Once approved, a shared change (a new invariant, a new entity, a contract change) is an **amendment**, the highest-blast-radius edit in the system. It fans out to every work item.

- Make the change here, bump `version`, and re-approve.
- Flag every work-item spec written against the old version to re-check against the new one.

`shaping-specs` routes a work item that needs a shared change back here before it builds. Do not let a work item invent a shared fact locally; that is how the ground drifts.

## What you do NOT do

- No implementation, and no work-item requirements: a work item's `FR`/`SC` live in `writing-specs`.

## Next step

The next step is `shaping-specs`: think each planned work item through, then `writing-specs` composes its spec, each grounded on this project spec. Offer it once the human sets `status: approved`; the ground has to be laid before a work item can stand on it. Point them at the first item in *Work items & sequencing*.
