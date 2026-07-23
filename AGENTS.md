# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, opencode, Cursor, and others) working in this repository.

## What this repo is

This repo is the `tests-are-specs` plugin: three portable skills for intent-first agentic coding, `scoping`, `building-from-plans`, and `verifying-work`, each handing off to the next through its `## Next step`. There is no orchestrator. Each skill is plain Markdown: a `SKILL.md` with YAML frontmatter and an instruction body, plus a reference file or two. There is no build step and nothing to compile. A skill must run in any harness that can load Markdown skills, so keep the wording harness-neutral. Name specific harnesses only as examples.

Keep the methodology and rationale, the "why", out of the skill bodies. The README carries it for humans.

## Key files

- `plugins/tests-are-specs/skills/<name>/SKILL.md`: the three skills. Frontmatter (`name`, `version`, `description`, `license`, `compatibility`, `metadata`) followed by the instruction body. These are the source of truth for behavior.
- `plugins/tests-are-specs/skills/scoping/references/`: `interview-questions.md` (uncover functional and non-functional requirements from the human) and `edge-cases.md` (the systematic edge-case walk). Loaded on demand.
- `plugins/tests-are-specs/skills/building-from-plans/references/honest-tests.md`: the five properties of an honest check and the faked-done anti-patterns to refuse.
- `.claude-plugin/marketplace.json` and `plugins/tests-are-specs/.claude-plugin/plugin.json`: the install manifests.
- `README.md`: for humans. The flow, the default paths, install steps, and the problem-to-solution mapping.

## The maintenance contract

Behavior lives in the skills; the README and manifests describe them. Change one, change the others in the same commit.

- **Skill set:** the plugin ships three skills. If you add, remove, or rename one, update the README's skill table, the `skills` array in `marketplace.json`, and the plugin and marketplace descriptions together. A skill's `name` must match its directory name.
- **Handoffs are the orchestration.** There is no orchestrator skill. Each skill's `## Next step` names the next skill by directory name, and the chain (`scoping → building-from-plans → verifying-work`) drives the flow. If you rename a skill, update every `## Next step` line that names it, in the same commit.
- **No config file.** Artifact paths are hardcoded defaults in the skill bodies, overridable by the user in conversation: the plan at `docs/plans/.build-intents/<slug>/plan.md`, the task list beside it, ADRs at `docs/adrs/`. The plan and ADRs are committed at the end of scoping with a conventional commit; the task list is never committed; once `verifying-work` passes, the plan and task list are deleted in a final chore commit, so history keeps the plan and the tree does not. If you change a default path, change it in every skill and reference file that names it and in the README, in the same commit. Do not put config in `plugin.json`: the manifest is off-schema for arbitrary keys and never reaches the agent at runtime.
- **Versions.** The package version lives in `plugin.json` and the `marketplace.json` entry; the two must match, and you bump them together on any shipped change. Each `SKILL.md` carries its own skill `version`; bump it when that skill's behavior changes. The package line and the skill lines are independent by design.
- **Portability.** Keep install and usage language harness-neutral. Never require a subagent or a hook from inside a skill; use capability-conditional wording ("if your harness can launch a subagent, do so; otherwise drive it inline"). Small harness-specific hints go under `metadata`. The chain hand-off is human-driven and harness-neutral by construction: each skill's `## Next step` tells the human to clear context and run the next skill with the plan's slug, so the plan file on disk is the only thing a fresh context needs.
- **Descriptions.** `name` and `description` load at startup for every skill, so every token earns its place. Lead with the trigger, keep the description near 130 tokens, and push detail into the body and reference files.

## Editing a skill

- Keep the YAML frontmatter valid, in both formatting and indentation.
- The body under the frontmatter is the product. Edit it like a careful instruction document, not code.
- **Brevity.** Every word is context. Write concise, plain language. Keep methodology and rationale out of the skill body; the "why" belongs in the README, not the always-loaded skill.
- **No AI-writing tells.** No em or en dashes, no filler, no significance inflation, no rule-of-three padding. A neutral instructional voice is the correct voice for these files.
- Keep reference files one level deep from `SKILL.md`, and move heavy detail into them so the always-loaded body stays lean.

## Changing a skill's behavior

A skill edit is a behavior change until you have watched it change behavior. Wording that reads clearly to you can move an agent not at all. Before you commit an edit meant to change what an agent does (not a typo or a link fix), test it against a no-guidance control: run the task with a fresh agent that does not have the skill. If it already does the right thing, the wording has nothing to fix, so do not add it.
