---
name: running-lifecycle
version: "1.11.1"
description: "Drive the full spec-monkey lifecycle end to end: ground the project, then for each work item triage it into a lane, shape, review the design, write, review the spec, implement, and audit its spec, pausing at every human approval gate. Use when the user wants to build a project or feature through the whole spec-driven flow in one guided pass rather than invoking each skill by hand. It never crosses an approval gate on its own. Do NOT use when the user wants only one phase (just a spec, just a review) — invoke that skill directly."
license: MIT
compatibility: any-agent
metadata:
  best-in: claude-code
---

# Running the Lifecycle

You drive the whole spec-monkey flow so the user doesn't have to remember each hop: ground → shape → review-design → write → review-spec → implement → audit. You invoke each skill in turn and stop at every human gate. You do not do the phases' work yourself; each phase is owned by its skill.

## Stance

- **Orchestrate, don't author.** Each phase is done by its skill (`grounding-specs`, `shaping-specs`, `reviewing-design`, `writing-specs`, `reviewing-specs`, `implementing-specs`, `auditing-specs`). Invoke it; do not reimplement its work here.
- **The human decides the gate; you only record it.** Approval (`status: approved`) is the human's call, on the project spec, on each work item's design, and on its spec. You may write `approved` to record an explicit, unsolicited go-ahead — never on your own judgment, never read into silence, never after talking them into it.
- **Right-size the ceremony.** Not every work item earns all seven phases. Triage each one first (step 3) and pick a lane. Forcing the full flow on a one-line change is the "waterfall with extra homework" charge landing; skipping the flow on a multi-seam change is how quality is lost. Match the lane to the item.
- **One work item at a time.** Finish a work item's loop before you start the next.
- **Portable by default.** You invoke skills by name and require no hook or subagent. Whether a phase uses its own optional mode (the subagent build, the fix-and-re-audit loop) is that skill's call, not yours.

## The flow

1. **Ground.** Is there an approved project spec at `docs/specs/project/spec.md` (`status: approved`)?
   - No: invoke `grounding-specs` to establish it. Stop at its human gate; the human approves, you record it.
   - Yes: read it. Its *Work items & sequencing* lists what to build and in what order.
2. **Pick the next work item** from *Work items & sequencing*, respecting `depends_on`.
3. **Triage: pick the lane.** Size the item before you run it, and say which lane you're taking and why. If the user handed you a written brief or PRD for the item, the shaping and writing phases ingest it and interview only the gaps rather than starting from scratch (see `shaping-specs`).
   - **No spec** — a one- or two-line change with nothing observable to sign (a typo, a constant bump, a comment fix): make it directly, note what you did, and don't open the flow at all. This is the case the README means by "a one-line change doesn't need a spec." Below the trivial lane, not inside it.
   - **Trivial slice** — small, but with a contract worth signing: one obvious approach, no live failure modes, no new shared fact, a build a reviewer reads in a glance. Skip shaping and its design gate; go straight to `writing-specs` for a **light contract** (`profile: light`): a single `spec.md` with the reduced section set — Goal, The request, one FR with its SC, and the verification — grounded on the project spec, with the reasoning-and-contract split dropped rather than stubbed with `N/A`. The profile and its exact required-vs-dropped sections are defined in `writing-specs/references/spec-template.md` ("THE LIGHT PROFILE"); `tools/spec-lint.py` checks a light spec against that reduced set. A worked example is `examples/clf-pipeline/docs/specs/run-summary-log/`. A purely cosmetic item with nothing to trace may skip the audit too. Do not skip the human's approval gate; even a light spec gets signed.
   - **Standard or complex** — real uncertainty about the what, the why, or the approach; multiple seams; a shared-fact change; anything touching a trust boundary: run the full flow below. When in doubt, take the full lane; the ceremony is cheaper than a missed requirement on a change that mattered.
4. **Shape.** (Full lane.) Invoke `shaping-specs` for that work item. It works the change through and writes the converged reasoning — the ask, the *Approach* and the alternatives weighed, the failure modes, the verification strategy — to `detail/design.md` at `status: draft`.
5. **Review the design.** Offer `reviewing-design` in a fresh context (see *Running a phase in fresh context* below). It judges the approach before a contract is written. Resolve any REVISE findings through `shaping-specs` and re-review.
6. **Design gate.** Stop and put the design in front of the human. Approval is theirs. When they give an explicit go-ahead, record it: the design's `status: approved`, plus `approved_by` and `approved_date`. `writing-specs` does not start while the design reads `draft`.
7. **Write.** Invoke `writing-specs`. It reads the approved design and composes `spec.md` (the decision brief) and `detail/contract.md` (the FR/SC contract) at `status: draft`.
8. **Review the spec.** Offer `reviewing-specs` in a fresh context. It runs the self-consistency sweep and judges the contract. Resolve any REVISE findings through `writing-specs` (or back through `shaping-specs` and `reviewing-design` when a finding is really about the approach) and re-review.
9. **Spec gate.** Stop and put the spec in front of the human. Approval is theirs. When they give an explicit go-ahead, record the gate: `status: approved`, plus `approved_by` and `approved_date`. Do not proceed while it reads `draft`, and never set `approved` on your own read of the review.
10. **Implement.** Invoke `implementing-specs`. It builds slice by slice, test-first, and sets `status: implemented`.
11. **Audit.** Invoke `auditing-specs` in a fresh context.
    - COMPLIANT: the work item is built and proven. Close it out (step 12).
    - NON_COMPLIANT: route each deviation by tag (`fix-code` → `implementing-specs`, `amend-spec` → `writing-specs`, an approach or reasoning change → `shaping-specs`, a shared-fact change → `grounding-specs`), then re-audit. An `amend-spec` or shared-fact route changes the signed contract: the spec regresses to `draft` and re-earns its gate (`writing-specs` "Amending an approved spec"). A bare `fix-code` route does not; the contract still stands.
12. **Close the loop.** The build stops before pushing; finishing is the human's step. Name it — open the PR or merge, then the human sets `status: shipped` — and don't take it yourself. A superseded or abandoned item goes `archived`.
13. **Loop.** Return to step 2 for the next work item until *Work items & sequencing* is exhausted.

## Running a phase in fresh context

The two reviews and the audit are worth more when a clean context runs them — one that hasn't watched the design get shaped, the spec get written, or the code get built, so it catches what the author's context glosses over. Concretely: if you are able to dispatch subagents, dispatch one given only the spec folder path and the skill to run. Otherwise, tell the human to open a new session with an empty context, pointed at the spec path, and hand back. Naming the mechanism is the point; "review it fresh" without one just runs in the same polluted context.

## What you do NOT do

- No authoring, building, reviewing, or auditing yourself; each phase's skill owns its work.
- No approving on your own judgment. The human decides; you record their explicit go-ahead, or you wait.
- No dropping a phase to save a hop. Triage (step 3) is the only place a phase is skipped, and only for an item that genuinely doesn't need it — never to rush a change that does. The approval gate is never skipped.

## Auto-starting this

Being invoked is what forces the flow. Making it *auto-start* from the first "let's build X" message needs a session-start hook, which is harness-specific and does not belong in a portable skill. That glue lives outside `skills/`, in the spec-monkey repository's per-harness adapter layer (the `hooks/` directory and its README, plus `docs/porting-to-a-new-harness.md`). It is opt-in and off by default, so the plugin stays portable and hook-free. Without it, start the flow by invoking this skill by name through your harness's skill mechanism.
