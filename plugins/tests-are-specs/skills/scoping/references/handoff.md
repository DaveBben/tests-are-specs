# Hand-off: scoping to building-from-plans to verifying-work

Harness-specific guidance for driving the chain after scoping. The skill bodies stay harness-neutral; a harness that can't launch subagents ignores this, and the human drives each step by hand.

Scoping has written the plan file (`<plan_dir>/<slug>/plan.md`) and the failing-stub contract. If the human wanted the direction reviewed, that has happened. Now drive the build, then the review.

## Claude Code (or any harness with subagents)

1. **Build.** Launch a subagent running `building-from-plans`, pointed at the plan file. It implements the change slice by slice, wires each stub into a real assertion, proves each slice against the real feature, and commits with conventional-commit messages.
2. **Review.** When the build subagent returns, launch a *separate, new* subagent running `verifying-work`, given the diff (`git diff <base>...HEAD`) and the same plan file. One context doing both build and review defeats the review's independence; a fresh subagent never watched the code get written.
3. **Route the verdict.** PASS: the human merges. FAIL: route each finding. "Fix code" goes to a new `building-from-plans` subagent, pointed at the same plan file (`<plan_dir>/<slug>/plan.md`) plus the findings to fix. "The ask is wrong" goes back to `scoping`. Then dispatch a fresh `verifying-work` subagent to re-review.

## No subagents

Hand the plan to the human. They run `building-from-plans`, then run `verifying-work` in a fresh session, then route the verdict. Same steps, driven by hand.
