# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, OpenCode, and others) working in this repository.

## What this repo is

This repo is the `spec-monkey` skills: seven portable skills for spec-driven development. Six are the phases of the flow, `grounding-specs`, `shaping-specs`, `writing-specs`, `reviewing-specs`, `implementing-specs`, and `auditing-specs`, and `running-lifecycle` drives them end to end. Each skill is plain Markdown: a `SKILL.md` with YAML frontmatter and an instruction body, plus a reference file or two. There is no build step and nothing to compile. A skill has to run in any harness that can load Markdown skill instructions, so keep the wording harness-neutral. Name specific harnesses (Claude Code, Codex, OpenCode) only as examples.

## Key files

- `plugins/spec-monkey/skills/<name>/SKILL.md`: the seven skills. Frontmatter (`name`, `version`, `description`, `license`, `compatibility`, `allowed-tools`) followed by the instruction body. **These are the source of truth for behavior.**
- `plugins/spec-monkey/skills/grounding-specs/references/`: the project-spec format (`project-template.md`) and the architecture interview (`interview-questions.md`).
- `plugins/spec-monkey/skills/shaping-specs/references/interview-questions.md`: the thinking interview (the ask, orientation, the five risk lenses, and the approach comparison) that produces the reasoning.
- `plugins/spec-monkey/skills/writing-specs/references/`: the canonical work-item spec format (`spec-template.md`, defined here once and shared with `shaping-specs`) and the contract interview (`interview-questions.md`).
- `plugins/spec-monkey/skills/reviewing-specs/references/review-rubric.md`: the rubric the reviewer works through.
- `plugins/spec-monkey/skills/auditing-specs/references/`: the audit checklist (`audit-rubric.md`) and the opt-in fix-and-re-audit loop (`remediation.md`, loaded only when the user asks to fix).
- `plugins/spec-monkey/skills/implementing-specs/references/subagent-mode.md`: the opt-in subagent-orchestrated build, loaded only when that mode is used.
- `plugins/spec-monkey/skills/running-lifecycle/SKILL.md`: the orchestrator; it invokes the six phase skills and has no reference file.
- `docs/testing-skill-changes.md`: the maintainer method for testing a skill-behavior change. Not shipped as a skill.
- `hooks/`: an optional, Claude-Code-only session hook that auto-starts `running-lifecycle`. Outside the plugin, off by default, so the plugin stays hook-free.
- `README.md`: for humans. Install steps, the seven-skill table, and the design principles.
- `.claude-plugin/marketplace.json`: the `spec-monkey` marketplace entry. It makes `/plugin marketplace add` work, and it lists each skill so `npx skills` groups them under the plugin.
- `plugins/spec-monkey/.claude-plugin/plugin.json`: the Claude Code plugin manifest.

## The maintenance contract

Behavior lives in the skills; the README and the manifests describe them. Change one, change the others in the same commit.

- **Skill set:** the plugin ships seven skills. If you add, remove, or rename one, update the README's seven-skill table and prose, the `skills` array in `marketplace.json`, and the plugin and marketplace descriptions together. A skill's `name` must match its directory name.
- **Handoffs:** each skill's `## Next step` section names the next skill by directory name, and `running-lifecycle` names all six phases. If you add, remove, or rename a skill, update every `## Next step` line and `running-lifecycle` that names it, in the same commit.
- **Harness-specific glue lives outside the skills.** A skill declares intent with `compatibility` and `metadata`, never a hard dependency. Anything that needs a hook or a subagent stays optional and external: the Claude Code auto-start lives in `hooks/` (outside the plugin, off by default); the orchestrated build and the fix-and-re-audit loop are capability-gated opt-in modes with a portable default path.
- **Version:** the package version lives in two places that must match: the `version` in the `marketplace.json` plugin entry and the `version` in `plugin.json`. Claude Code treats `plugin.json` as authoritative, so bump both together. Each skill also carries its own top-level `version` field; bump that when you change that skill's behavior.
- **Portability:** keep install and usage language harness-neutral. Harness-specific hints (`model`, `effort`, `argument-hint`) go under `metadata:`, where a harness that doesn't read them just skips them. Never require a subagent, a hook, or context forking from inside a skill. Only a handful of harnesses have those, so anything that depends on one stops being portable.
- **Descriptions:** `name` and `description` load at startup for every skill, so every token has to earn its place. Lead with the trigger, keep the description near 130 tokens or under, and push the detail into the body and the reference files.
- **One home for each spec format:** two document types, one format file each. The work-item format lives in `writing-specs/references/spec-template.md` (shared: `shaping-specs` composes into it too); the project-spec format lives in `grounding-specs/references/project-template.md`. The rubric and the skills point at them; they don't restate them. Both share the `spec_monkey` version and the lifecycle convention; the ID conventions split by document (`FR-`/`SC-` in work-item specs, `INV-` in the project spec). If any of those change, update both templates, the rubric, and any README mention in one change.
- **WHAT and WHEN, never HOW:** a spec says what to build and when, not which file or symbol to edit. Don't let build detail leak into a skill or the template. The one exception is the verification commands, which belong in the spec.

## Editing a skill

- Keep the YAML frontmatter valid, in both formatting and indentation.
- The body under the frontmatter is the product. Edit it like a careful instruction document, not code.
- Keep reference files one level deep from `SKILL.md`, and move heavy detail down into them so the always-loaded body stays lean.

## Changing a skill's behavior

A skill edit is a behavior change until you have watched it change behavior. Wording that reads clearly to you can move an agent not at all. Before you commit an edit meant to change what an agent does (not a typo, a link, or a ragged line), test it against a no-guidance control. The method is in [`docs/testing-skill-changes.md`](docs/testing-skill-changes.md).

- **Control first.** Run the task with a fresh agent that does not have the skill. If it already does the right thing, the wording has nothing to fix; don't add it.
- **Match the form to the failure.** A shaping problem (the spec comes out with HOW in it) wants a positive recipe. A discipline problem (the agent skips the interview when the user is impatient) wants a prohibition plus the excuse it answers. The two forms backfire when swapped; don't reach for a prohibition by default.
- **This is a maintainer method, not a skill.** Don't add a testing skill to the shipped seven. It would trip the maintenance contract above and spend description tokens every session for something only maintainers run.
