# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, opencode, Cursor, and others) working in this repository.

## What this repo is

This repo is the `spec-intents` plugin: three portable skills for intent-first agentic coding, `scoping`, `build`, and `check`, each handing off to the next through its `## Next step`. There is no orchestrator. Each skill is plain Markdown: a `SKILL.md` with YAML frontmatter and an instruction body, plus a reference file or two. There is no build step and nothing to compile. A skill must run in any harness that can load Markdown skills, so keep the wording harness-neutral. Name specific harnesses only as examples.

The method these skills enact is written up in [`method-brief.md`](method-brief.md). The problems they answer are in [`problems-with-spec-driven-development.md`](problems-with-spec-driven-development.md). Keep the "why" in those documents, not in the skills.

## Key files

- `plugins/spec-intents/skills/<name>/SKILL.md`: the three skills. Frontmatter (`name`, `version`, `description`, `license`, `compatibility`, `metadata`) followed by the instruction body. These are the source of truth for behavior.
- `plugins/spec-intents/skills/scoping/references/`: `interview-questions.md` (uncover functional and non-functional requirements from the human) and `edge-cases.md` (the systematic edge-case walk). Loaded on demand.
- `plugins/spec-intents/skills/build/references/honest-tests.md`: the five properties of an honest check and the faked-done anti-patterns to refuse.
- `.spec-intents/config.json`: the three team knobs, `decision_review`, `task_list`, and `pr_template`. Committed, repo-scoped. Each skill reads this first.
- `.claude-plugin/marketplace.json` and `plugins/spec-intents/.claude-plugin/plugin.json`: the install manifests.
- `README.md`: for humans. The flow, the config, install steps, and the problem-to-solution mapping.

## The maintenance contract

Behavior lives in the skills; the README and manifests describe them. Change one, change the others in the same commit.

- **Skill set:** the plugin ships three skills. If you add, remove, or rename one, update the README's skill table, the `skills` array in `marketplace.json`, and the plugin and marketplace descriptions together. A skill's `name` must match its directory name.
- **Handoffs are the orchestration.** There is no orchestrator skill. Each skill's `## Next step` names the next skill by directory name, and the chain (`scoping → build → check`) drives the flow. If you rename a skill, update every `## Next step` line that names it, in the same commit.
- **Config lives in `.spec-intents/config.json`, not the manifest.** Three knobs sit there: `decision_review`, `task_list`, and `pr_template`. Each skill reads the file as its first operational step, falls back to a value in `CLAUDE.md` / `AGENTS.md`, then to a hardcoded default. `config.json` and `pr-template.md` are committed team settings; the task list (default `.spec-intents/task-list.md`) is gitignored per-change scratch, and the repo's `.gitignore` encodes that split. Do not put config in `plugin.json`: the manifest is off-schema for arbitrary keys and never reaches the agent at runtime. If you add a knob, add it in three places: `config.json`, the reading skill's first step, and the README config section.
- **Versions.** The package version lives in `plugin.json` and the `marketplace.json` entry; the two must match, and you bump them together on any shipped change. Each `SKILL.md` carries its own skill `version`; bump it when that skill's behavior changes. The package line and the skill lines are independent by design.
- **Portability.** Keep install and usage language harness-neutral. Never require a subagent or a hook from inside a skill; use capability-conditional wording ("if your harness can launch a subagent, do so; otherwise drive it inline"). Harness-specific hints go under `metadata`, where a harness that does not read them just skips them.
- **Descriptions.** `name` and `description` load at startup for every skill, so every token earns its place. Lead with the trigger, keep the description near 130 tokens, and push detail into the body and reference files.

## Editing a skill

- Keep the YAML frontmatter valid, in both formatting and indentation.
- The body under the frontmatter is the product. Edit it like a careful instruction document, not code.
- **Brevity.** Every word is context. Write concise, plain language. Keep methodology and rationale out of the skill body; the "why" belongs in `method-brief.md`.
- **No AI-writing tells.** No em or en dashes, no filler, no significance inflation, no rule-of-three padding. A neutral instructional voice is the correct voice for these files.
- Keep reference files one level deep from `SKILL.md`, and move heavy detail into them so the always-loaded body stays lean.

## Changing a skill's behavior

A skill edit is a behavior change until you have watched it change behavior. Wording that reads clearly to you can move an agent not at all. Before you commit an edit meant to change what an agent does (not a typo or a link fix), test it against a no-guidance control: run the task with a fresh agent that does not have the skill. If it already does the right thing, the wording has nothing to fix, so do not add it.
