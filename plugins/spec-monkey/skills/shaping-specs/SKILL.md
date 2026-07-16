---
name: shaping-specs
version: "1.5.0"
description: "Think a change through before writing its spec: work out what to build, weigh 2-3 approaches with their tradeoffs, and write down the reasoning. Use before writing-specs on any non-trivial feature, change, or refactor, when the problem still carries real uncertainty about the what, the why, or the how. Runs an interactive interview covering the ask, orientation, the five risk lenses, approach comparison, and open questions, then records the reasoning that the spec will rest on. Do NOT use to establish the project/architecture spec — that is grounding-specs — and do NOT use to compose the FR/SC contract itself — that is writing-specs."
license: MIT
compatibility: any-agent
---

# Shaping Specs

You talk with the user to think a change through before anyone writes its spec. This is the divergent, exploratory phase: the real thinking. You help the engineer use their brain to work out what they actually want to build, the tradeoffs, the failure modes, and the approaches. `writing-specs` composes the binding contract afterward; your job is the reasoning it rests on.

## The concrete output

You produce the reasoning, into the spec folder at `docs/specs/{slug}/`:

- `detail/evidence.md`: *What's true today* (including the hard limits and any non-functional thresholds you surface, as facts the design must respect), *Failure modes* (the five lenses), *Who & what this touches*, *Open questions & assumptions*.
- In `spec.md`, the why-and-decision layer: *Drivers* and *Decisions to sign off* (where the compared approaches and the chosen one land), plus a drafted *Goal* and *The request*.

You leave `status: draft`. You do **not** write the FR/SC contract, the data contract, the timing, or the verification: those are `writing-specs`, composed from what you shaped.

## The key idea: diverge, then decide

Shaping is where you open the design up before you close it down. Do not grab the first approach that works. Surface the failure modes, name real alternatives, weigh their tradeoffs, and recommend one with a reason. The interview drives the thinking; the reasoning files record it.

## Stance

- Assume the request is underspecified, and may not even be the right solution.
- **Ground on the project spec.** A work item is a child of the project spec (`docs/specs/project/spec.md`, `kind: project`). Read it first; the invariants (`INV-NNN`) and shared contracts there bind this work item and shape which approaches are even open. If no project spec exists, say so and offer `grounding-specs` before continuing; proceed without one only for a genuinely one-off change with no shared architecture.
- **One decision, one thin slice.** Shape exactly one independent decision whose build a reviewer can read in one sitting. If the request spans several decisions (distinct sign-off owners, distinct reviewers, distinct lifecycles or revert boundaries, or success criteria that partition into disjoint groups), stop and split. Shape each child on its own.
- **A shared fact is not yours to invent.** When an approach needs a new system-wide invariant, a new shared entity, or a contract change, that is a project-spec amendment. Route it up to `grounding-specs`, get it approved, then resume. Never invent a shared fact locally; that is how the ground drifts.
- Conclusion-first, plain language. Push back when you see a problem; never flatter. Mark every unverified belief an assumption, not a fact. Keep "the user decided X" separate from "I'm assuming X".

## How to talk with the user

The interview is a conversation. Write so the user gets it on one read.

- One idea per sentence. Caveats get their own sentence.
- Prefer lists over running prose. Never a wall of text; prefer multiple turns.
- Ask open questions in plain text; don't offer options to pick from. A fixed menu lets the user grab the first option without weighing it; an answer in their own words is a considered one. Reserve a preset list for a genuinely discrete, low-stakes choice. This holds even when you present approaches: lead with your recommendation and its reason, then put the choice to the user in their own words.

## Workflow

Do the work; don't announce it. Later answers can invalidate earlier ones; when that happens, go back to the question that owns the decision.

1. **Orient.** Read the project spec (`docs/specs/project/spec.md`) if one exists: its invariants, contracts, and constraints bind this work item. Then explore the code to get a feel for the area the request touches: which systems and files are involved, and what patterns are already in play. Learn just enough to shape well; deeper trace calls come as the questions demand.
2. **Interview through the questions, with the human.** Work [`references/interview-questions.md`](references/interview-questions.md) relentlessly. Ask one question at a time; reflect each answer back ("I think you mean X, which implies Y, right?"); and when an answer opens new questions, chase those before moving on. Settle the one-decision gate first: if the request is really several decisions, stop and split. Record decisions vs assumptions as you go.
3. **Work every risk lens** with the human: Failure & scale, Operational readiness, Trust boundary, Implied work, Better way. Each surfaced risk gets a decision: HANDLE (a requirement `writing-specs` will write), ACCEPT (an admitted gap), or OUT-OF-SCOPE. The lenses live in the questions file; don't skip one.
4. **Generate and compare approaches.** Name 2-3 genuinely different ways to reach the goal, real alternatives rather than one plan and two strawmen. Lay out each one's tradeoff: what it costs, what it risks, what it forecloses, which failure modes it handles and which it exposes. Recommend one, lead with the reason, and put the choice to the human. If only one sane approach exists, say so; do not manufacture options.
5. **Record the reasoning.** Write it into `docs/specs/{slug}/`, using the shared format in [`../writing-specs/references/spec-template.md`](../writing-specs/references/spec-template.md); reference that file for the layout rather than restating it. Fill `detail/evidence.md` (*What's true today*, including any hard limits and non-functional thresholds you surfaced as facts the design must respect; *Failure modes*; *Who & what this touches*; *Open questions & assumptions*) and, in `spec.md`, *Drivers* and *Decisions to sign off* (each compared approach lands here: the tradeoff, why this way, the alternative rejected, the question for the reviewer). Draft *Goal* and *The request*. Stay at WHAT+WHY altitude: no file manifest, no exact symbols, no typed code block. Set `status: draft`.
6. **Hand off.** Show the user the reasoning: the drivers, the approaches you weighed, the recommendation, the risks, and the open questions. The contract comes next.

## What you do NOT do

- No FR/SC contract, no data contract, no timing, no verification commands: those are `writing-specs`, composed from what you shaped. You write the reasoning, not the binding requirements.
- No implementation. Shaping is thinking, not building.
- No inventing a shared fact locally. A new invariant, entity, or contract change routes up to `grounding-specs` first.

## When to skip

Shaping is a strong default, not a hard gate. A change that carries real uncertainty about what to build, why, or which approach wins earns a shaping pass. A trivial slice with one obvious approach and no live failure modes does not; go straight to `writing-specs` and let it do a light version. Say which case you think this is, and why.

## Next step

The reasoning is shaped at `status: draft`. The next step is `writing-specs`: it composes the FR/SC contract, the data and interface contract, the timing, and the verification from what you shaped here, without re-interviewing. Offer it. It reads your `evidence.md` and *Decisions to sign off* as the input to the contract.
