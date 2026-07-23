# tests-are-specs

**The tests are the spec.**

This plugin is my attempt to address the short-comings within Spec-driven development. The intent of spec-driven development is that the planning and specification of features is done upfront and reviewed before beinghanded to an AI agent to implement.

A lot of people point out this is just waterfall in disguise. While I don't 100% agree with that (shares some similarities but not an entire repeat of the process), I have encountered pitfalls with working with specs.

### Pitfalls with Specs:

- A spec does not gurantee that you will get the exact results. You could hand the same spec to different LLMs and get different implementations. Therefore, the spec becomes less of a contract and more of an aspiration.
- Reviewing markdown files requires more cognitive effort than reviewing specs. If a code change comes in, it's easier to read the diff and run the tests than it is to match every FR to the matching code it's supposed to produce.
- A 1K line Markdown file gets produced for a 20 line change. When it ends up taking more time to review the markdown file than the actual code, there is an imbalance
- Specs go stale quickly and confuse the agent. A spec might list a particular detail that is relevant at the time of authoring but no longer relevant a couple of features later. However, the agent might still anchor onto that detail and try to use it as a constraint even if it's no longer relevant
- Context overload when you have 100 different specs sitting in a repo that needs to be manually looked through to avoid later contradictions
- A lot of existing specs frameworks are heavy on ceremony, not brownfield friendly, and feel awkward when trying to work in an agile fashion.

### Solution

We already have specs. Those are tests. They are deterministic pass/fail results. They don't lie. The thing tests/code doesn't tell us is the **why**. This can be documented by short ADR decisions.

The contract is written as **complete tests marked expected-failure** (`xfail` in pytest, `test.failing` in Jest, `@wip` in Cucumber), not as empty stubs or red tests. That buys three things:

- The contract-review MR has a green pipeline, and trunk-based teams can commit the contract straight to main. CI can tell "agreed but unbuilt" apart from "broken".
- The runner executes the marked test, proving it fails for the right reason (behavior absent, not a typo), and reports an unexpected pass the moment the behavior lands.
- Verification becomes mechanical: the build's only legal edit to a contract test is removing the marker, so `verifying-work` just diffs the test file. Any edited assertion is a caught goalpost move.

An empty stub with the outcome in prose ("expired link should 400") would hand the real decision to the builder, and prose is ambiguous; the full test body pins the inputs and the outcome in code. A pinned-outcome stub remains only as a flagged fallback for the rare case where no stable boundary exists yet to call.

## How to use
Once installed, the following workflow happens:

1. When you ask your AI agent for a non-trivial code change, it will start a scoping interview with you to understand the NFRs, FRs, edge cases and constraints, playing each answer back as a concrete example. It also reads past ADRs (architecture decisions) to ground its context. The ratified examples get turned into complete tests marked expected-failure during the interview. The output of the interview are two file:
  * A tiny **ADR File** (architecture decision record) in `docs/adrs/`, committed, and optionally **reviewed** by your team before implementation.
  * A **plan.md** in `docs/plans/.build-intents/<slug>/`, committed with the contract in a conventional commit and deleted in a final chore commit once verification passes, so git history keeps the intent without a stale file in the tree. The agent asks whether to open an MR for the direction before building.

2. After scoping, clear your context (or start a fresh session) and run the `building-from-plans` skill with the plan's slug. It decomposes the plan into turn-efficient tasks and builds one task at a time, each in a fresh subagent whose context is the task entry, on the cheapest model tier the task allows, with a review after each task and a refactor pass on green.
3. Post implementation, the agent offers a choice: launch a fresh subagent running `verifying-work` and report its verdict, or you clear context and run it yourself with the same slug. Either way the reviewer starts fresh and verifies the work matches the contract.

You will notice that this workflow almost matches Claude Code's default plan feature with just a few extra bells and whistles:

- Automatic ADR caption when needed
- Writing complete expected-failure tests first to match NFRs and FRs and Constrinats
- Running full implementation to actually test each feature rather than relying on tests
- A step to review plans before implementation gets underway, with a green pipeline
- Per-task subagents with explicit model tiers, and a refactor pass on every green task



## The three skills

Three portable Markdown skills, chained by hand-off. Each is independently launchable.

| Skill | Input | What it does |
|---|---|---|
| `scoping` | a change request | Explore the blast radius and past decisions, interview the human to uncover requirements (never inventing them), walk the edge cases, and author a complete expected-failure test for each. Emit a short plan and an ADR receipt. |
| `building-from-plans` | a plan | Remove each contract test's marker and make it pass, decomposed into turn-efficient tasks on a branch, refactoring on green. Never edit a contract test body. Dispatch a fresh subagent per task where the harness allows. After every task, drive the real feature and watch it, not just a green suite. Commit with conventional commits. |
| `verifying-work` | a plan and a diff | From a fresh context, audit the diff against the plan: every requirement built, the contract diff marker-removal only, no faked tests, the trust boundary checked, nothing crept in. Report-only, PASS/FAIL. |

The flow is `scoping → building-from-plans → verifying-work`. Trivial changes get scoping's one-minute blast-radius glance, then skip the rest and go straight to building; the glance is what catches the "trivial" change that is secretly load-bearing. After scoping, the human decides whether the team reviews the direction before code. Each hand-off is the same move: clear context, run the next skill with the plan's slug. The plan on disk carries everything a fresh context needs, which is what keeps every stage independent of the last one's blind spots.

## Artifacts

- **Plan** (`docs/plans/.build-intents/<slug>/plan.md`): goal, the verification contract, out-of-scope. Committed at scoping, deleted in a chore commit once verification passes; history keeps it.
- **ADRs** (`docs/adrs/`): one file per decision, the durable *why*, the rejected alternatives, the tradeoffs. Committed.
- **Task list** (`docs/plans/.build-intents/<slug>/task-list.md`): the build's task checklist, one turn-efficient task per dispatch with files, tests, model tier, and status. Never committed; optionally created.

There is no config file. These paths are the defaults; tell the agent if your repo keeps plans or ADRs elsewhere.

## Installing

**Claude Code:**

```bash
/plugin marketplace add DaveBben/tests-are-specs
/plugin install tests-are-specs@tests-are-specs
```

Skills surface as `tests-are-specs:scoping`, `tests-are-specs:building-from-plans`, `tests-are-specs:verifying-work`.

**Any skills-compatible agent:** the skills are plain Markdown under `plugins/tests-are-specs/skills/`. Point your harness at the directory. Nothing to compile.

MIT.
