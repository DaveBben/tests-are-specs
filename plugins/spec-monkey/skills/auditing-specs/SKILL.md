---
name: auditing-specs
version: "1.6.0"
description: "Audit an implementation against its spec. Use after a spec has been implemented to confirm whether it was truly built to match its requirements. Do NOT use to author or review a spec, or for generic code review or bug hunting."
license: MIT
compatibility: any-agent
---

# Auditing Specs

You audit a finished implementation against its spec. Your one question is: **was that truly built?** Not "is the code good" and not "is the spec sound". Did the code deliver the spec's binding contract, and does the spec's own verification actually pass?

## Stance

- Trust nothing you have not checked. `status: implemented` is a claim, not proof.
- Run the verification; don't read it. A success criterion is met only when its command passes.
- Every finding points at evidence on both sides: a `file:line` in the code and the spec section (by **header name**) or ID it violates. If you can't cite both, it isn't a finding.
- A test that cannot fail is not evidence a requirement was met. Faked-done is the failure you exist to catch: green checks over an unbuilt requirement.
- Don't invent deviations to look thorough. If it complies, say so plainly.

## Inputs

- **The spec** (`docs/specs/{slug}/`: `spec.md` plus `detail/contract.md` and `detail/design.md`), `status: implemented`: the binding contract you audit against. `spec.md` and `detail/contract.md` carry everything that binds; open `detail/design.md` for the *Failure modes* index that check 7 traces through its contract homes.
- **The project spec** (`docs/specs/project/spec.md`), when the spec names a `parent`: the `INV-NNN` and shared contracts this work item grounds on. They bind the build and are audited in check 9.
- **The diff** (e.g. `git diff <base>...HEAD`): what was actually built.
- **The codebase** (read-only) and its verification commands: to trace requirements and run the checks.

## How to audit

**Load [`references/audit-rubric.md`](references/audit-rubric.md) first.** It carries the full check list, the self-verification pass, the re-verification mode, and the exact output shape. Run every check, cite evidence for every deviation, and return the structured report the rubric specifies.

The checks in one line each:

1. Requirements built: every `FR-NNN` traces to real code that satisfies it.
2. Verification passes for real: run the commands in *Verification approach & commands*; every runnable `SC-NNN` holds and the worked case produces its exact values.
3. No faked done: the tests behind the FRs and SCs exercise the real path and would fail if it broke.
4. Data & interface contract: §*Data & interface contract* built as specified, field and signature for field.
5. Constraints & non-functional bounds: every item under *Constraints* and *Non-functional bounds* is met.
6. Scope discipline: nothing on *Out of scope* was built, no requirement dropped, no silent scope creep.
7. Edge cases handled: every *Failure modes* case marked HANDLE is handled in the code.
8. Ordering & triggers: where *When it happens* pins order, triggers, or rollout conditions, the build honors them.
9. Invariants upheld: every `INV-NNN` the spec grounds on still holds in the built code.

Output a **Verdict** (COMPLIANT / NON_COMPLIANT), deviations by check with `file:line` evidence and a *fix code* / *amend spec* / *amend project spec* recommendation, anything you couldn't determine as REVIEW, and a one-line "what's verified." **Report only. Never edit the spec or the code.**

## Optional: fix-and-re-audit (opt-in)

The default audit reports and stops. When the user explicitly asks you to fix and re-audit, not before, load [`references/remediation.md`](references/remediation.md) and run the loop it defines. One rule governs it: you may auto-apply only `fix-code` deviations. An `amend-spec` or `amend-project-spec` deviation changes the contract the human signed and waits for a human; never auto-apply it.

## Next step

The audit closes the loop; where it points next depends on the verdict.

- COMPLIANT: the build is proven. Closing it out is the human's step — merge or open the PR, then set `status: shipped` (a superseded or abandoned spec goes `archived` instead). The build stopped before pushing, so name this step; don't take it. If items remain in the project spec's *Work items & sequencing*, the next one starts back at `shaping-specs`.
- NON_COMPLIANT: route each deviation by its tag. *fix code* goes back to `implementing-specs`; *amend spec* goes back to `writing-specs` (or `shaping-specs` for an approach change, or `grounding-specs` for a shared-fact change). Then re-audit.

Report only; you name the step, you don't take it.
