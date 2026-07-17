# spec-intents

Intent-first agentic coding. The human authors the intent; the agent never invents requirements. The code and its tests are the only source of truth.

spec-intents is three portable skills for building software with an AI agent. It replaces the heavy, generated prose spec with something smaller and honest: a one-page intent you author, a build that proves every slice against real behavior, and an independent review of the actual diff. Nothing that can rot survives a merge.

The core idea is a split. A traditional spec fuses three jobs that want opposite things: steering the model (short, disposable), verifying the result (executable, deterministic), and preserving the reasoning (the "why", durable). spec-intents gives each job its own home. Steering goes in a disposable intent. Verification goes in executable checks. The reasoning goes in an append-only decision log.

## The three skills

| Skill | When it fires | What it does |
|---|---|---|
| `scoping` | A change expensive to reverse: crosses a seam, touches a data shape or migration, changes an external contract or trust boundary, or needs sign-off. Trivial changes skip it. | Triage by cost-of-change, probe unfamiliar ground, interview the human to uncover requirements (never inventing them), walk the edge cases, and emit a one-page intent to the PR body plus a why-receipt to the decision log. |
| `build` | After `scoping`, or for a small clear change straight from a ticket. | Implement in thin vertical slices on an isolated branch. Each check is written before the code and states an observable outcome. After every slice, drive the real feature and observe it, not just a green test. |
| `check` | After `build`, before merge. Also early on a flagged foundational slice. | The independent Gate B, from a fresh context. Trace each criterion to code, re-run the targeted verification, hunt faked-done tests, inspect the trust boundary, flag scope creep. Report-only, PASS/FAIL, with `file:line` evidence on both sides. |

The flow is `scoping → build → check`. Each skill names the next by hand-off; there is no orchestrator. Most changes skip `scoping` and go straight to `build`. `check` wants a fresh context (a subagent or a new session); the rest run inline.

## The artifacts, and how long they live

- **Intent** (PR body): the goal, requirements, acceptance criteria, verification plan, and out-of-scope list. Disposable. It dies at merge.
- **Task list** (default `.spec-intents/task-list.md`): the thin-slice checklist that `build` writes and resumes from. Gitignored per-change scratch, never committed. Deleted at merge.
- **Decision log** (append-only, ADR-style): the *why*, the rejected alternatives, and the edge cases you consciously chose not to handle. Kept forever.
- **Code and tests**: the source of truth for what the system does. Kept forever.

## Configuration

Team settings live in a repo-committed `.spec-intents/config.json`:

```json
{
  "decision_review": "expensive-only",
  "task_list": ".spec-intents/task-list.md",
  "pr_template": ".spec-intents/pr-template.md"
}
```

- **`decision_review`** (`always` | `expensive-only` | `never`): how a scoped decision gets ratified before code. `always` opens a decision-only PR every time. `expensive-only` (the default) puts the decision in the feature branch's draft PR and escalates to a separate PR only for a big irreversible call. `never` is solo or high-trust: the human still authors the intent, but there is no separate gate.
- **`task_list`**: path for the ephemeral slice checklist that `build` writes and resumes from. Default `.spec-intents/task-list.md`, which the repo's `.gitignore` keeps out of version control. The checklist stays on disk for a dead session or a fresh-context read, but never enters git or reaches your mainline. Set it to `PLAN.md` at the repo root if you would rather commit it and see it on the branch.
- **`pr_template`**: path to the intent template that `scoping` fills in. Default `.spec-intents/pr-template.md`. Edit it to match your team's PR format.

Each skill reads the config as its first step, then falls back to a value stated in `CLAUDE.md` / `AGENTS.md`, then to the built-in default. The config file is the reliable channel: a Markdown skill only acts on what it reads, and a plugin manifest never reaches the agent at runtime.

**Per project.** The config does not ship with the plugin. Installing spec-intents does not create `.spec-intents/` in your repo. In each project where you use it, add `.spec-intents/config.json` (and optionally `pr-template.md`) at the root and commit them; the skills read those files from the project root at runtime. Without them, the built-in defaults apply and the skills still run.

## Installing

**Claude Code (plugin):**

```bash
/plugin marketplace add DaveBben/spec-intents
/plugin install spec-intents@spec-intents
```

Skills surface namespaced: `spec-intents:scoping`, `spec-intents:build`, `spec-intents:check`.

**Any skills-compatible agent (Cursor, Codex, opencode, and others):** the skills are plain Markdown under `plugins/spec-intents/skills/`. Point your harness at the directory. There is nothing to compile and nothing to configure beyond the optional `.spec-intents/config.json`.

## How it answers the problems with spec-driven development

spec-intents is a direct response to the documented failures of spec-driven development (see [`problems-with-spec-driven-development.md`](problems-with-spec-driven-development.md)). Each problem below is one the plugin actually solves, with the mechanism named. Problems the plugin does not solve are left off this list rather than dressed up.

### Less overhead, no illusion of progress

**Reviewing the spec costs more than reviewing the code.** `scoping` caps its output at a one-page intent in the PR body (step 6); the code and tests stay the only source of truth. There is no generated multi-thousand-line spec to read.

**Reviewing prose instead of the thing that runs.** The binding review is `check`, which audits the actual `git diff` with `file:line` evidence and re-runs the verification. It reads the code that runs, not prose about it.

**Over-decomposition.** `build`'s bug-fix protocol forbids the fan-out: a one-line bug is a one-line fix plus its regression check. `scoping`'s cost-of-change triage sends trivial changes straight to build with no stories at all.

**Undefined bug-fix protocol.** `build` names one: reproduce with a single failing check, fix the code, keep that check as a regression guard. No re-run of any spec.

**Manufactured scope creep.** The intent carries an explicit out-of-scope list, and `check`'s scope-discipline check fails the diff if any behavior crept in that nobody asked for.

**Illusion of work.** The deliverables are a one-page intent and running, proven code, not hours of generated conversation. Triage refuses ceremony by default.

### No frozen waterfall

**Freezing design up front kills iteration.** Only expensive-to-reverse work gets scoped ahead of code. The triage sends everything else straight to `build`, which iterates in thin vertical slices, each proven before the next.

**You can't spec what you don't understand yet.** `scoping` step 2 tells you to build a throwaway spike to learn the ground, delete it, then scope. Understanding comes from building, not before it.

**Poor fit for legacy and maintenance.** Nothing assumes a greenfield repo or whole-team adoption. Scoping is per-change, the bug-fix protocol fits a maintenance backlog, and `build` mirrors the codebase's existing patterns and test tooling rather than imposing a framework.

### Nothing to rot

**Stale specs that agents execute anyway.** The intent is disposable and dies at merge. There is no persistent spec to drift out of sync and be executed confidently.

**The spec as a second codebase.** spec-intents ships no spec artifact with a lifecycle. The code and tests are the only source of truth, so there is no second one to disagree with the first.

**Context pollution and the one-page comprehension ceiling.** The intent is one page, sized to what an agent reliably follows. No large spec file crowds the context window.

### Rigor that is enforced, not theatrical

**Agents mark work done without doing it.** `build`'s Gate A proves every slice by driving the real feature and observing the outcome, not "tests green." `check`'s faked-done check then hunts hollow tests from a clean context, with the anti-patterns catalogued in `honest-tests.md`.

**False sense of rigor from templates agents ignore.** Rigor comes from running checks, not from templates: `check` executes rather than reads, and a PASS is never allowed without running the targeted set that session.

**Specs read non-deterministically where code is deterministic.** Every acceptance criterion must become a runnable check that can fail. The binding artifact is an executable test, not prose three people read three ways.

**Spec-as-source: MDD's inflexibility plus the LLM's non-determinism.** spec-intents refuses spec-as-source. The intent is disposable steering, never the authority the build is generated from.

### A real review of the real code

**No code-review gate.** `check` is exactly that missing gate: an independent, fresh-context review over the finished diff, tracing each criterion to code and re-running the verification. It runs on the code, before merge.

**No security guarantee from the ceremony.** `check`'s trust-boundary check is a standing mandate on every run: inspect where untrusted input crosses into trusted code, and check authorization on the real code. `scoping`'s edge-case walk also probes the malicious version of the flow.

**Whole-document regeneration kills diff review.** Review is diff-based by construction: `check` reads `git diff`. The intent is a single page, so a change of direction never triggers a full spec regeneration.

### The intent can't be corrupted at authoring

**Generators fabricate requirements you never gave.** The load-bearing rule in `scoping` step 3: you never state a requirement the user didn't give. When a gap appears you ask a question that leads the human to surface it. You never supply the requirement.

**Requirements mutate between pipeline stages.** There is no spec-to-plan-to-tasks chain of one LLM generating from the last. One human-authored intent is carried straight through: `build` builds only from its criteria, and `check` audits against that same intent.

**The spec is the highest-leverage, least-governed file.** `scoping` requires ratifying the direction before any code, governed by the `decision_review` policy. The intent gets a deliberate sign-off gate instead of an ungoverned edit.

### Keeping the "why", dropping the throwaway

**Specs record the "what" but never the "why".** `scoping` appends an ADR-style receipt to a durable decision log recording the rationale and the rejected alternatives, the tradeoffs the next maintainer needs. It is the one artifact kept at merge.

**Specs have near-zero value after ship.** The split resolves the waste: the throwaway steering is thrown away at merge, while the durable "why" survives in the decision log. You stop maintaining the part nobody revisits.

### Room for the model to solve it

**Over-structuring pigeonholes the model.** The intent states observable outcomes ("expired link → 400"), never implementation. It fixes *what* and *when*, leaving `build` to choose *how* against the codebase's own patterns.

**The functional-vs-technical boundary is unmanageable.** spec-intents draws it operationally: a requirement is an observable behavior asserted at the boundary. That is a concrete test for where requirements stop and implementation begins, instead of asking people to feel the line.

## Layout

```
spec-intents/
├── .claude-plugin/plugin.json
├── skills/
│   ├── scoping/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── interview-questions.md    # uncover functional + non-functional requirements
│   │       └── edge-cases.md             # the systematic edge-case walk
│   ├── build/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── honest-tests.md           # the five check properties + faked-done catalog
│   └── check/
│       └── SKILL.md
```

The repo root also carries `.spec-intents/config.json` (the config template), `method-brief.md` (the full method this plugin enacts), and `problems-with-spec-driven-development.md` (the problem list it answers).

MIT.
