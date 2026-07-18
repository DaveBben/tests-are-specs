# tests-as-specs

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

## How to use
Once installed, the following workflow happens:

1. When you ask your AI agent for a non-trivial code change, it will start a scoping interview with you to understand the NFRs, FRs, edge cases and constraints. It also reads past ADRs (architecture decisions) to ground its context. These immediately get turned into failing test stubs during the interview. The output of the interview are two file:
  * A tiny **ADR File** (architecture decision record) which **should** be committed and optionally **reviewed** by your team before implementation.
  * A **plan.md** which **should not** be committed. It's only there to hand to the build agent. Very similair to Claude Code's planning mechnaism. 

2. After scoping, depending on your harness, the `building-from-plans` skill  will automatically be invoked (otherwise do it yourself) with a path to the `plan.md`. It builds, one slice at a time in a subagent.
3. Post implementation, again depending on your harness, the `verifying-work` skill will automatically be invoked with a subagent. It will verify the work matches the contract.

You will notice that this workflow almost matches Claude Code's default plan feature with just a few extra bells and whistles:

- Automatic ADR caption when needed
- Writing test stubs first to match NFRs and FRs and Constrinats
- Running full implementation to actually test each feature rather than relying on tests
- A step to review plans before implementation gets underway



## The three skills

Three portable Markdown skills, chained by hand-off. Each is independently launchable.

| Skill | Input | What it does |
|---|---|---|
| `scoping` | a change request | Explore the blast radius and past decisions, interview the human to uncover requirements (never inventing them), walk the edge cases, and author a failing test stub for each. Emit a short plan and an ADR receipt. |
| `building-from-plans` | a plan | Wire each stub into a real assertion and make it pass, in thin vertical slices on a branch. Never weaken a pinned outcome. After every slice, drive the real feature and watch it, not just a green suite. Commit with conventional commits. |
| `verifying-work` | a plan and a diff | From a fresh context, audit the diff against the plan: every requirement built, the contract intact and biting, no faked tests, the trust boundary checked, nothing crept in. Report-only, PASS/FAIL. |

The flow is `scoping → building-from-plans → verifying-work`. Trivial changes skip `scoping` and go straight to building. After scoping, the human decides whether the team reviews the direction before code. A subagent-capable harness can then dispatch each step; otherwise the human drives them.

## Artifacts

- **Plan** (`.tests-as-specs/plans/<slug>/plan.md`): goal, the verification contract, out-of-scope. Gitignored
- **ADRs** (`.tests-as-specs/adrs/`): one file per decision, the durable *why*, the rejected alternatives, the tradeoffs. Committed.
- **Task list** (`.tests-as-specs/task-list.md`): the build's slice checklist. Gitignored; Optionally created

## Configuration

Team settings live in a committed `.tests-as-specs/config.json`:

```json
{
  "task_list": ".tests-as-specs/task-list.md",
  "plan_dir": ".tests-as-specs/plans",
  "plan_template": ".tests-as-specs/plan-template.md",
  "adr_dir": ".tests-as-specs/adrs"
}
```

- **`plan_dir`** / **`plan_template`**: where per-change plans live, and the template `scoping` fills.
- **`adr_dir`**: directory of committed ADR files, one per decision (rebase-friendly). `scoping` reads them before interviewing and adds one after.
- **`task_list`**: the build's ephemeral slice checklist.

Each skill reads this file first, then falls back to a value in `CLAUDE.md` / `AGENTS.md`, then a built-in default.

## Installing

**Claude Code:**

```bash
/plugin marketplace add DaveBben/tests-as-specs
/plugin install tests-as-specs@tests-as-specs
```

Skills surface as `tests-as-specs:scoping`, `tests-as-specs:building-from-plans`, `tests-as-specs:verifying-work`.

**Any skills-compatible agent:** the skills are plain Markdown under `plugins/tests-as-specs/skills/`. Point your harness at the directory. Nothing to compile.

MIT.
