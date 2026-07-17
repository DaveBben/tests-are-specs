# Build discipline: honest tests and a real self-review

Two disciplines the workflow leans on: the test-first loop (SKILL step 3) and the diff self-review (step 5). Both guard the same thing — that "implemented" means built and proven, not built and asserted. The anti-patterns below are the exact defects `auditing-specs` hunts; ship one and the audit sends it back. Cheaper to refuse it here.

## Test-first: red before green

For each success criterion a test can check:

1. **Write the test, run it, watch it fail — for the right reason.** A failing test you have seen fail is proof the check is real. A test written after the code too easily asserts whatever the code already does. Read the failure: it must fail because the behavior is absent, not because the test is broken (wrong import, typo, missing fixture). A test that fails for the wrong reason and then "passes" proves nothing.
2. **Build until it goes green,** and no further. Don't add behavior the SC doesn't ask for.
3. **No test surface? Say so.** When an SC is a manual check, a post-deploy metric, or a pure config edit, there's nothing to unit-test. Name it and lean on the spec's *Verification approach & commands*. Don't manufacture a hollow test to have a green light.
4. **An artifact is due even when a unit test already passes.** When an SC also carries a boundary-crossing or NEEDS-INFRA line under *Artifacts to author*, a green unit test does not discharge it — author that artifact too. A NEEDS-INFRA artifact is written now and run when the infra exists. "Can't run here" is never "don't write it."

## Faked-done: the anti-patterns to refuse

Each of these produces a green check that proves nothing. The auditor's check 3 exists to find them; don't write them.

- **Assertion on a constant / tautology.** `assert True`, `assert x == x`, asserting a literal you just set. It cannot fail, so it verifies nothing.
- **Testing the mock.** The test configures a mock to return X, then asserts it returned X. You tested your mock setup, not the code.
- **Over-mocking the path under test.** Mocking the very function whose behavior the FR is about leaves the real path unrun. Mock the boundary (the network, the clock), not the thing you're verifying.
- **Snapshot of current output as "expected."** Recording whatever the code emits today and asserting it stays that. It locks in bugs and passes by construction. Derive expected values independently, with real numbers.
- **Happy-path only.** The risk lenses surfaced failure and edge cases; if success is defined only for the golden path, the failure paths are unproven.
- **Loosening or deleting a failing check to reach green.** Relaxing a bound, widening a tolerance, `skip`-ping the case, catching the exception the test should see. This fakes the result instead of meeting it. Fix the code, not the check.

## Self-review: read your own diff as a hostile reviewer (step 5)

Before you set `status: implemented`, read the whole diff against the spec as if you were auditing someone else's work:

- **Trace.** Every FR maps to a real change in the diff; every SC maps to a test that would flip to failing if the behavior broke. Every entry in *Artifacts to author* exists in the diff, the NEEDS-INFRA ones included. An FR with no corresponding change, an SC whose test can't fail, or a listed artifact with no file is a hole — even if another test covers the same SC.
- **Scope.** Nothing on *Out of scope* got built; no requirement got quietly dropped; no adjacent feature crept in.
- **Seams.** At least one non-mocked test crosses each real boundary the change touches (a database, an HTTP call, a queue, a contract between two modules). An all-unit, all-mocked diff over a change with real seams is weak.
- **Invariants.** Every cited `INV-NNN` still holds in the assembled code. A local fix that satisfies an FR by breaking an invariant is not done.
- **Honesty.** No anti-pattern from the list above survived. No `TODO`/stub left on a path an FR needs. No commented-out failing assertion.
- **Simplicity.** You reused what the codebase already had rather than rebuilding it; the fix lives once at the root, not patched per caller.

This rubric is deliberately the same standard `auditing-specs` applies from a fresh context. Meeting it yourself first means the independent audit confirms rather than corrects — and when it doesn't, the gap is real, not a difference of taste.
