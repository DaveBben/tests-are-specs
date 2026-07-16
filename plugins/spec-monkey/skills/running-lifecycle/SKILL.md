---
name: running-lifecycle
version: "1.5.0"
description: "Drive the full spec-monkey lifecycle end to end: ground the project, then for each work item shape, write, review, implement, and audit its spec, pausing at every human approval gate. Use when the user wants to build a project or feature through the whole spec-driven flow in one guided pass rather than invoking each skill by hand. It invokes the six skills in order and never crosses an approval gate on its own. Do NOT use when the user wants only one phase (just a spec, just a review) — invoke that skill directly."
license: MIT
compatibility: any-agent
metadata:
  best-in: claude-code
---

# Running the Lifecycle

You drive the whole spec-monkey flow so the user doesn't have to remember each hop: ground → shape → write → review → implement → audit. You invoke each skill in turn and stop at every human gate. You do not do the phases' work yourself; each phase is owned by its skill.

## Stance

- **Orchestrate, don't author.** Each phase is done by its skill (`grounding-specs`, `shaping-specs`, `writing-specs`, `reviewing-specs`, `implementing-specs`, `auditing-specs`). Invoke it; do not reimplement its work here.
- **Never cross a human gate.** Approval (`status: approved`) is the human's, both on the project spec and on each work-item spec. You stop and ask; you never set `approved` yourself.
- **One work item at a time.** Finish a work item's loop (shape → write → review → approve → implement → audit) before you start the next.
- **Portable by default.** You invoke skills by name and require no hook or subagent. Whether a phase uses its own optional mode (the subagent build, the fix-and-re-audit loop) is that skill's call, not yours.

## The flow

1. **Ground.** Is there an approved project spec at `docs/specs/project/spec.md` (`status: approved`)?
   - No: invoke `grounding-specs` to establish it. Stop at its human gate; the user sets `approved`.
   - Yes: read it. Its *Work items & sequencing* lists what to build and in what order.
2. **Pick the next work item** from *Work items & sequencing*, respecting `depends_on`.
3. **Shape.** Invoke `shaping-specs` for that work item. It thinks the change through and writes the reasoning (`detail/evidence.md`, the brief's *Drivers* and *Decisions to sign off*) at `status: draft`.
4. **Write.** Invoke `writing-specs`. It composes the FR/SC contract onto that reasoning, keeping `status: draft`.
5. **Review.** Offer `reviewing-specs` in fresh context. Resolve any REVISE findings through the authoring skill and re-review.
6. **Gate.** Stop. The user sets the work-item spec to `status: approved`. Do not proceed while it reads `draft`.
7. **Implement.** Invoke `implementing-specs`. It builds and sets `status: implemented`.
8. **Audit.** Invoke `auditing-specs` in fresh context.
   - COMPLIANT: the work item is done.
   - NON_COMPLIANT: route each deviation by tag (`fix-code` → `implementing-specs`, `amend-spec` → `writing-specs`, an approach or reasoning change → `shaping-specs`, a shared-fact change → `grounding-specs`), then re-audit.
9. **Loop.** Return to step 2 for the next work item until *Work items & sequencing* is exhausted.

## What you do NOT do

- No authoring, building, reviewing, or auditing yourself; each phase's skill owns its work.
- No crossing an approval gate. The human approves; you wait.
- No skipping the review or the audit to save a hop. The gates are the point of the flow.

## Auto-starting this (Claude Code only)

Being invoked is what forces the flow. Making it *auto-start* from the first "let's build X" message is harness-specific and does not belong in a portable skill. It lives outside `skills/`, as an optional Claude Code session hook (see the repo's `hooks/` directory and its README). The hook is opt-in and Claude-Code-only; it is not enabled by default, so the plugin stays portable and hook-free everywhere else. Without it, start the flow by invoking this skill by name (in Claude Code, `/spec-monkey:running-lifecycle`).
