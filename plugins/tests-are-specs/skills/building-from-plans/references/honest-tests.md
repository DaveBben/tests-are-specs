# Honest checks: the properties, and the fakes to refuse

Every check that proves a task, the contract stubs `scoping` froze (once wired) and any finer test you add, must hold these properties. `verifying-work` reviews the diff from a fresh context and hunts the fakes below; ship one and it comes back. Cheaper to refuse it here.

## The five properties of an honest check

1. **Observable behavior, stated as an outcome.** "Expired link → 400", not "function `validate()` returns false". Assert what the user or caller can see at the boundary, not an internal step.
2. **Written before the code.** Write the check, run it, watch it fail for the *right* reason (the behavior is absent, not a typo, wrong import, or missing fixture). A check written after the code too easily asserts whatever the code already does.
3. **One observable behavior per test.** A test proves one thing. Don't fold three behaviors into one assertion; you lose which one broke.
4. **Executed.** Automated where there's a test surface; a written manual script a human actually runs where there isn't (UI feel, a post-deploy metric, a config-only edit). Prose nobody runs is not a check.
5. **Able to fail if the behavior regressed.** If the code broke and the check still passes, it proves nothing. Every check must have a way to go red.

The contract comes from `scoping`, not from you: complete tests frozen as the executable requirements, each a full assertion on a pinned outcome, marked expected-failure. Your only edit to one is removing its marker; never change a body, an input, or an expected value, and never skip or delete one. A fallback stub the plan flags is the one case you wire an assertion, and it must check exactly the outcome its description pins. If a contract test is wrong, impossible, or missing a case you need, that's a gap to raise with `scoping`, not to patch here. You may add finer-grained tests below the contract as you build; the properties above apply to those too.

## Use the repo's own tooling

Mirror the test framework, the runner, and the patterns already in the codebase; never impose a new framework or a named ceremony. When a change crosses a real boundary (a database, an HTTP call, a queue, a module-to-module contract) the check exercises that seam for real; don't mock away the very crossing under test. If the seam needs infra you can't run here, write the check now and run it when the infra exists. "Can't run it here" is never "don't write it."

## Faked-done: the anti-patterns to refuse

Each produces a green check that proves nothing.

- **Assertion on a constant / tautology.** `assert True`, `assert x == x`, asserting a literal you just set. It cannot fail.
- **Testing the mock.** Configure a mock to return X, then assert it returned X. You tested the mock setup, not the code.
- **Over-mocking the path under test.** Mocking the very function whose behavior the test is about leaves the real path unrun. Mock the boundary (the network, the clock, the external API), never the thing you're verifying.
- **Snapshot of current output as "expected."** Recording whatever the code emits today and asserting it stays that. It locks in bugs and passes by construction. Derive the expected value independently, with real numbers.
- **Happy-path only.** The edge cases `scoping` marked *handle* are acceptance criteria; if only the golden path is proven, those criteria are unproven.
- **Loosening or deleting a failing check to reach green.** Relaxing a bound, widening a tolerance, skipping the case, catching the exception the check should see. On a contract test this is the cardinal sin: its body is frozen, so any edit beyond removing the marker is moving the goalposts, not building. Fix the code, not the test. If the contract test itself is wrong, kick it back to `scoping`; never quietly weaken it.

If you reach for one of these because a test won't pass, stop; the honest fix is a found root cause, not a softened check. Reproduce the failure deterministically, read the whole error, work one hypothesis at a time, and binary-search the diff you just wrote to the cause. If the cause is the intent itself (ambiguous, impossible, or fighting a house rule), that's not a code fix: raise it, don't reinterpret the ask to force green.
