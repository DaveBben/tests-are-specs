---
name: auditing-specs
version: "1.0.0"
description: "Audit an implementation against its spec. Use after a spec has been implemented to confirm whether it was truly built to match its requirements. Do NOT use to author or review a spec, or for generic code review or bug hunting."
license: MIT
compatibility: any-agent
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Auditing Specs

You audit a finished implementation against its spec. Your one question is: **was that truly built?** 
Not "is the code good" and not "is the spec sound". Did the code deliver the spec's binding contract, 
and does the spec's own verification actually pass?

## Stance

- Trust nothing you have not checked. `status: implemented` is a claim, not proof.
- Run the verification; don't read it. A success criterion is met only when its command passes.
- Every finding points at evidence on both sides: a `file:line` in the code and the spec section
  (by **header name**) or ID it violates. If you can't cite both, it isn't a finding.
- A test that cannot fail is not evidence a requirement was met. Faked-done is the failure you
  exist to catch: green checks over an unbuilt requirement.
- Don't invent deviations to look thorough. If it complies, say so plainly.

## Inputs

- **The spec** (`docs/specs/{slug}/spec.md`), `status: implemented`: the binding contract you audit
  against. Read all of it.
- **The diff** (e.g. `git diff <base>...HEAD`): what was actually built.
- **The codebase** (read-only) and its verification commands: to trace requirements and run the checks.

## How to audit

**Load [`references/audit-rubric.md`](references/audit-rubric.md) first.** It carries the full check
list, the self-verification pass, the re-verification mode, and the exact output shape. Run every
check, cite evidence for every deviation, and return the structured report the rubric specifies.

The checks in one line each:

1. Requirements built: every `FR-NNN` traces to real code that satisfies it.
2. Verification passes for real: run the *How I know it works* commands; every runnable `SC-NNN` holds and the worked case produces its exact values.
3. No faked done: the tests behind the FRs and SCs exercise the real path and would fail if it broke.
4. Data & interface contracts: §*Data & interface contracts* built as specified, field and signature for field.
5. Constraints & non-functional bounds: each one under *How it fits* is met.
6. Scope discipline: nothing on *Out of scope* was built, no requirement dropped, no silent scope creep.
7. Edge cases handled: every *What could go wrong* case marked HANDLE is handled in the code.
8. Ordering & triggers: where *When it happens* pins order, triggers, or rollout conditions, the build honors them.

Output a **Verdict** (COMPLIANT / NON_COMPLIANT), deviations by check with `file:line` evidence and a
*fix code* or *amend spec* recommendation, anything you couldn't determine as REVIEW, and a one-line
"what's verified." **Report only. Never edit the spec or the code.**
