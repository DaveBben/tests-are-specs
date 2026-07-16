# Debugging a slice that won't go green (escape hatch)

Load this mid-build, the moment a slice fails in a way you don't understand: a test won't pass, or it passes and breaks another, or the behavior is wrong and the cause isn't obvious. Work it **before you touch the code again**.

The failure it exists to stop is the shotgun edit: changing things half-understood until the error moves, trading a bug you understand for one you don't. That is exactly how implementation quality falls behind spec quality — the sharpest complaint against spec tools. A found root cause is worth more than three lucky patches.

## The discipline

1. **Reproduce it, deterministically, before you theorize.** Get the failure to happen on command — the failing test, or a one-line repro. A bug you can't reproduce, you can't confirm you fixed. If it's flaky, the flakiness *is* the bug (timing, ordering, shared state); pin that first.

2. **Read the actual error, all of it.** The real message, the real stack, the real diff between expected and got — not the error you assume it is. Most mid-build bugs are named in the output you skimmed. Print the values at the failure point if the message is thin.

3. **One hypothesis at a time. Predict, then test.** State what you think is wrong and what you'd expect to see if it were. Make the smallest change or probe that would confirm or kill it. If the result doesn't match the prediction, the hypothesis was wrong — drop it, don't patch around it. Don't stack three speculative changes; you won't know which one mattered.

4. **Binary-search the delta.** The code worked before this slice; the break is in the change you just made. Bisect it: `git diff` the slice, `git stash` half, or comment out half the new code, and see which side carries the failure. Narrow to the smallest span that still fails. This beats staring at the whole diff.

5. **Fix the root cause, not the symptom.** A `try/except` that swallows the error, a retry that hides a race, an `if` that special-cases the one input that broke — these move the symptom, not the cause. Fix it once, in the shared place every caller routes through, so it can't recur two callers over.

6. **Know when it's the spec, not the code.** If the failure traces to a contract that is ambiguous, self-contradictory, impossible as written, or in conflict with a cited `INV-NNN`, stop — this is not a code bug. It is an `amend-spec` (or `amend-project-spec`) situation. Raise it with the human with the evidence; do **not** silently reinterpret the contract to make the test pass. Reinterpreting a spec you signed under is how "a missing field turns into a redefined interface."

7. **Cap the loop.** After a few full cycles with no narrowing — the failure hasn't moved toward a cause — stop and hand the human what you have: the repro, the hypotheses you killed, and where you're stuck. More solo cycles past that point burn tokens and start the shotgun edits. A fresh context or a human eye is cheaper than the tenth guess.

## What never counts as fixed

- The check now passes because you loosened it, skipped the case, mocked the failing boundary, or read the expected value back from the thing under test. That is faked green; the audit exists to catch it, and it will. Fix the code the check guards.
- The error "went away" and you don't know why. An unexplained pass is not a pass — you've likely moved the bug. Reproduce the original failure once more against the fix and confirm it's the fix that closed it.
