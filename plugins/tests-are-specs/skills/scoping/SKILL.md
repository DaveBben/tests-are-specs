---
name: scoping
version: "1.1.0"
description: "Use at the start of a non-trivial code change, before touching the code, when the user wants to build, change, or remove something. Fire on conversational intent, not only the word scope: 'build/add/implement X', 'let's add a feature', 'change how X works', 'migrate/rework/refactor X', 'remove/rip out/deprecate feature Y', 'turn this into a spec'. Tearing out a whole feature is scope work when it spans stored data, callers, or endpoints, not a quick delete. Scope work that crosses a seam, moves a data shape or migration, touches an external contract or trust boundary, or needs sign-off. It explores blast radius and prior decisions, interviews the human to uncover requirements (never inventing them), walks edge cases, and authors the binding contract as complete tests marked expected-failure, plus a short plan. A trivial-looking ask (typo, null check, copy tweak, version bump, button color) still gets a one-minute blast-radius glance before going straight to build; a shared token, a state-encoding value, or a hidden seam escalates it. When in doubt, fire this skill and let triage route it."
license: MIT
compatibility: any-agent
metadata:
  namespaced-as: "tests-are-specs:scoping"
---

# Scoping

You scope a change before code exists: explore the blast radius, pin the goal, uncover the requirements from the human (never author them), then turn each ratified requirement into a complete test, full arrange-act-assert with real inputs and an independently derived outcome, marked expected-failure so the suite stays green while the behavior is absent. Those tests are the binding contract: the build removes markers, never edits bodies. Output: the contract, a short intent in a local plan file, and a receipt in the decision log.

**Input:** a description of the change request (a ticket, an issue, or the human's ask). Nothing else is required.

## Behavior rules

- Conclusion first, plain language, one idea per sentence.
- The human authors intent; you never do. Push back when the ask looks wrong; never invent a requirement to fill a gap; ask.
- Ask one question at a time, open-ended; never a menu.
- Mark every unverified belief an assumption, not a fact.
- Respect the repo's house rules. A scope that fights one is wrong however clean it reads; surface the conflict, don't work around it quietly.
- "Agreed" means an explicit yes from the human, not silence, not a vague "looks good", and never a yes you record on their behalf.
- When an answer, the code, or your own scope stops making sense, go back and clarify; never build the contract on a guess.
- Validate incrementally: present each settled piece (the requirement list, the edge-case dispositions, the contract) and get approval before building on it.

## 1. Explore the blast radius

Read the code before you judge the change; you can't price a cost you haven't read. Find what it actually touches: the seams crossed, the data shapes and migrations moved, the trust boundaries and callers reached, and what must already be true for it to work.

Scale the look to the uncertainty: a glance for an obvious copy tweak, a real read or a throwaway spike (then delete the spike) when you can't immediately bound the blast radius. Skip this only when the ground is genuinely already known.

**Read the past decisions.** Read the ADR files under `docs/adrs/` (or wherever the user says they live) for any decisions touching this area. Carry them into the interview: don't re-open a settled question or contradict a constraint the team already chose. A past decision you'd overturn is one to raise, not to quietly reverse.

You come out of this with what must be true for the change to work, enough blast radius to triage honestly in step 2, and the prior decisions that constrain it.

## 2. Triage by cost-of-change

Now that you've seen the blast radius, choose the lane. You do not need to state this to the user.

- **Just build it:** trivial, one sane approach, no blast radius (typo, null check, copy tweak, version bump). Skip the rest of scoping. Go build.
- **Scope it** if it's expensive to reverse: crosses a seam, touches a data shape or migration, changes an external contract, crosses a trust boundary, or needs sign-off. Run the rest of this skill.
- **Too big to scope as one thing:** the ask is really several changes with different reviewers or ship dates ("build our auth system"). Don't scope it as one. Name the smaller independently shippable parts and the order between them, then scope only the first.

**When you can't cleanly place the lane, scope it.** Guessing "just build it" on a change that crosses a trust boundary skips the whole safety pass; any touch of a trust boundary, authorization, a data shape, a migration, or an external contract is the scope-it lane however small the diff looks. That's a trigger, not a judgment call.

Triage stays revisable: if building later reveals blast radius you missed here, stop and re-triage. Don't manufacture ceremony to look careful; genuine doubt about blast radius is a reason to scope, not theater.

## 3. Interview: the requirements come from the human

Load `references/interview-questions.md` and work through it. It covers functional requirements (what the system does) and non-functional ones (how well it does it).

**Walk the whole checklist; don't cherry-pick.** Asking only the questions that fit an answer you already have in mind lets you author the requirements without meaning to. Work every category that could plausibly apply (functional, and each non-functional class); when you skip a category, say so and why, so the human can catch a bad omission.

The rule that matters most:

- **You never state a requirement the user didn't give.** You uncover requirements by asking, never supply them; the final list is functional and non-functional requirements that all came from the user. Your job is to uncover and format, never to author.
- **When you spot a gap, ask, don't tell.** Don't tell the user what requirement is missing. Ask a question that leads them to surface it themselves. Say "What happens when two users submit at once?", not "you need idempotency here."

Run it as a conversation: hardest uncertainty first, plain language. Reflect each answer back as a concrete example with real values ("a cart of $80 with a coupon that expired yesterday charges the full $80, right?") and get agreement; an example forces the numbers a restatement lets slide. Ask for their answer before you offer your own.

You're done when all three hold: every behavior the user cares about has exactly one requirement; no two requirements overlap or restate each other; and you cannot name a new *distinct* behavior to specify. Until then, keep asking.

### Requirement failures
- **Too few:** you can still name a behavior the user cares about that no requirement covers, so the implementer will guess. Keep asking.
- **Too many:** you've split one behavior into a dozen restatements, or a "requirement" names a file, function, or approach. That's HOW, not a requirement. Padding to feel thorough is not coverage. Cut it.

## 4. Surface edge cases; the human dispositions each

You surface, the human decides. Load `references/edge-cases.md` and walk **every** dimension it lists (input, quantity, time, state, failure, the human), not the subset that fits a solution you already have in mind. For each dimension, surface a concrete case as a question or note that it doesn't apply; silently skipping a dimension hides a gap. Sketch the flow as you go so gaps show up as blank space, and probe the incident cases hardest, since the requester describes the happy path by default. The human gives each surfaced case a disposition:

- **Handle** → becomes an acceptance criterion → becomes a test.
- **Accept** (a known gap) or **Out-of-scope** → a receipt in the decision log.

## 5. Author the failing contract

Turn each requirement, acceptance criterion, and the goal into a **complete test now**, before any implementation. Each contract test is a full arrange-act-assert: real inputs, the real call at the boundary, and an assertion on a concrete expected outcome (the status code, the error body, the count, the boundary value). Mark it with the framework's expected-failure marker (`xfail` in pytest, `test.failing` in Jest, `@wip` in Cucumber) rather than leaving it red: the suite and CI stay green while the behavior is absent, the runner proves the test fails for the right reason, and it flips to an unexpected pass the moment the behavior arrives. The marker is the build's to remove; the body is not the build's to edit.

Write contract tests at the system's external boundary (the HTTP endpoint, the CLI, the public API), not against internals you haven't chosen. The boundary's shape is itself a requirement; ratify it with the human in the interview. Favor boundaries that cut the system into units with one clear purpose each, communicating through well-defined interfaces, so each unit can be understood and tested on its own.

A test that only names a behavior ("test that reset works") with the outcome in prose is not a contract; prose hands the real decision to the builder. Pin the number, in code.

Every contract test must be:

- an **observable behavior**, stated as an outcome: "expired link → 400", not "function X returns Y";
- **complete**: with the marker removed it fails because the behavior is absent, never because the body errors on a missing import or a half-written call;
- **able to fail** once the marker is gone, if the behavior broke.

Derive every expected value **independently**, with real numbers. Never pin an expected value by guessing what the code will emit; a value chosen to match the eventual output passes by construction and proves nothing.

When no stable boundary exists yet to write the real call against, fall back to a pinned-outcome stub: the test name, a description pinning the concrete expected outcome, and a marked body that fails. Flag it in the plan; `building-from-plans` wires it into a real assertion that checks exactly that outcome, nothing weaker.

Not every requirement reduces to a test. Route the ones that resist, and record the routing in the log (step 8):

- **Performance and scale NFRs** ("p95 under 200ms", "10k concurrent") → a benchmark or load test. Executable, but heavier and environment-dependent; note the command, the threshold, and where it runs (CI or staging).
- **Security "no unauthorized path" properties** → you can test known attacks, never the absence of all holes. Write the positive authorization stub, and hand the negative to `verifying-work`'s standing security mandate: a human or reviewer reading the real code.
- **UX feel or genuinely exploratory surface** → a written manual observation script a human runs. Executable in the weak sense: someone actually runs it and records what they saw.

Use the repo's existing test tooling; don't impose a framework. Note the command that runs the contract (`pytest -k expired_link`). A criterion with no contract test and no named non-test check isn't ready; take it back to step 4.

## 6. Emit the intent

The tests carry the requirements now, so the intent stays short: steering and a table of contents, not a second copy of the spec. Write it to a **plan file** at `docs/plans/.build-intents/<slug>/plan.md` (unless the user names another location), where `<slug>` is a short kebab-case name for the change (the branch name works). Three sections, nothing else. The plan is per-change: `building-from-plans` and `verifying-work` read it from a fresh context, and once verification passes it is deleted in a final chore commit; git history keeps it. One scoped change gets one plan file and one branch, never one plan for a whole initiative; a large ask was split into separate scoped changes upstream, each with its own plan.

Keep it short. It holds:

- **Goal:** the checkable delta ("X moves from A to B"), confirmable true or false.
- **Verification:** the contract tests you just authored, each listed with its expected outcome and where it lives, plus the command that runs them. Flag any fallback stub so the build knows to wire it. This is the binding contract; the requirements are those tests, not a prose restatement. Add any non-test checks (manual scripts, benchmarks) here too, with who runs them.
- **Out-of-scope:** what you're deliberately not doing.

Do not restate the requirements as prose beside the tests: the two would drift. If the intent grows long, the change is probably two changes; go back to triage. The intent is disposable; it dies in the cleanup commit once verification passes. The tests do not.

## 7. Independent review of the intent and the contract

The contract steers the whole build, so review it before code, from a fresh context. If your harness can launch a subagent, dispatch one to review the intent and the failing tests; otherwise review them yourself in a clean pass. Check:

- **Sound:** the intent and tests are grounded in the reality of the code, not assumptions. The tests are feasible against the actual seams.
- **Nothing invented:** every test traces to a requirement the user gave. Flag any test asserting a behavior the user didn't ask for.
- **The contract bites:** every contract test carries its expected-failure marker, and with the marker removed it fails because the behavior is absent, not because the body errors. A test that passes before any code, or whose body is a placeholder with the outcome only in prose (outside a flagged fallback stub), is not a contract.
- **Expected values are independent:** no test asserts a snapshot of what the code will emit.
- **No duplication or contradiction:** no two tests restate each other, and none conflict.

Report only. If the review flags a problem, fix the intent or the tests and re-check before handing off.

## 8. Log the why

Write a receipt to the **decision log**: it records *why*, never *what is true now* (constraint values live in tests, not here). One entry per genuinely expensive decision, and one per consciously-unhandled edge case, so a future maintainer knows a gap was chosen, not missed.

The log is one file per decision, which keeps it rebase-friendly: two branches adding decisions never touch the same file. Write each entry to `docs/adrs/<date>-<slug>.md` (unless the user names another location), where `<date>` is today and `<slug>` is a short kebab-case name for the decision. Per file:

```
# <date> · <the decision>

Why:       the rationale
Rejected:  the alternatives you turned down
Tradeoffs: what this decision costs, what you give up or make harder by choosing it
```

If a requirement is verified by something other than a unit test (a benchmark, a manual script, the reviewer's read), note that tradeoff under `Tradeoffs`.

## 9. Pause for review

The contract tests, the plan, and any ADR receipts are ready. Commit them with a conventional-commit message (for example `test(reset-tokens): contract and intent for single-use reset links`), so git history captures the intent whatever happens next. Tell the human where the plan is saved, then ask whether they want a PR or MR opened for team review of the direction; the contract tests are marked expected-failure, so the pipeline stays green while the team reviews them.

- **MR:** open it, or hand the human the branch. After the review, they proceed the same way as below.
- **No MR:** proceed straight to the hand-off.

## Next step

Tell the human: clear this context (or start a fresh session) and run the `building-from-plans` skill with the plan's slug, for example "run building-from-plans for reset-tokens". A fresh context builds from the plan on disk, not from this conversation's residue; the plan is the single hand-off artifact. After the build, the same move again: clear context and run `verifying-work` with the slug.
