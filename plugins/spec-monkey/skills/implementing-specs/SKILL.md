---
name: implementing-specs
version: "1.2.0"
description: "Implement an engineering spec end-to-end. Build the code that satisfies its requirements and verify it against the spec's own success criteria and commands. Use when the user provides you a spec to implement. Do NOT use to author or review a spec or for a change with no approved spec."
license: MIT
compatibility: any-agent
---

# Implementing Specs

You take an approved spec and build it. The spec says WHAT to do and WHEN; the HOW is yours. You work
that out from the spec and the real code.

## Stance

- Build what the spec says. Don't add scope it didn't ask for, and don't drop a requirement.
- If the spec is wrong, impossible, or missing something load-bearing, stop and raise it with the human.
  Don't silently reinterpret it.
- You are not done until verification passes and every FR and non-functional bound is met.

## Workflow

Do the work; don't narrate the steps.

1. **Find the spec.** Locate the approved spec folder at `docs/specs/{slug}/` (its `spec.md` `status` reads
   `approved`). Read `spec.md` and `detail/contract.md` — together they are the full build contract: the
   requirements (`FR-NNN`) and their success criteria (`SC-NNN`), *When it happens* (triggers and ordering),
   the *Data & interface contract*, the scope and *Out of scope* lines, and *Verification approach &
   commands*. `detail/evidence.md` is review-time reasoning; open it only when the contract leaves a
   decision unclear. (A spec written under format 1.0.0 spreads these sections one-per-file in `detail/`;
   locate them by heading and read them all.)

2. **Plan the build.** Work the implementation out from the spec and the code. Find the seams the change
   touches: the callers, the types, the tests. Let *When it happens* set the order. How you break the work
   up is up to you: steps, tasks, or independent non-conflicting pieces run in parallel.

3. **Build it.** Implement until every `FR-NNN` holds. Respect the constraints, the data and interface
   contracts, and the ordering. Stay inside scope, and build nothing on the *Out of scope* list. Mirror the
   patterns already in the codebase rather than inventing new ones.

4. **Verify.** Run the spec's verification from *Verification approach & commands*. Every success criterion
   must hold, and the worked case must produce the exact values it states. The work isn't done until the
   checks pass. When one fails, fix the code, not the check.

5. **Review the change.** Read your own diff critically against the spec: does every requirement trace to a
   real change, are the edge cases handled, are the tests honest (no vacuous assertions, no over-mocking
   that leaves the real path untested)?

6. **Finalize.** Set the spec's `status` to `implemented`, then commit with a message that says what
   changed and why, and points back to the spec.


## What you do NOT do

- No scope creep. If you find the spec needs to change, raise it; don't quietly expand the work.
- No authoring or reviewing the spec itself.
