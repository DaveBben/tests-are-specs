# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, OpenCode, and others) working in this repository.

## What this repo is

This repo is the `spec-monkey` skills: four portable skills for spec-driven development, named `creating-specs`, `reviewing-specs`, `implementing-specs`, and `auditing-specs`. Each skill is plain Markdown: a `SKILL.md` with YAML frontmatter and an instruction body, plus a reference file or two. There is no build step and nothing to compile. A skill has to run in any harness that can load Markdown skill instructions, so keep the wording harness-neutral. Name specific harnesses (Claude Code, Codex, OpenCode) only as examples.

## Key files

- `plugins/spec-monkey/skills/<name>/SKILL.md`: the four skills. Frontmatter (`name`, `version`, `description`, `license`, `compatibility`, `allowed-tools`) followed by the instruction body. **These are the source of truth for behavior.**
- `plugins/spec-monkey/skills/creating-specs/references/spec-template.md`: the canonical spec format, defined here once.
- `plugins/spec-monkey/skills/reviewing-specs/references/review-rubric.md`: the rubric the reviewer works through.
- `plugins/spec-monkey/skills/auditing-specs/references/audit-rubric.md`: the checklist the auditor runs against a finished build.
- `implementing-specs` has no reference file; its `SKILL.md` is self-contained.
- `README.md`: for humans. Install steps, the four-skill table, and the design principles.
- `.claude-plugin/marketplace.json`: the `spec-monkey` marketplace entry. It makes `/plugin marketplace add` work, and it lists each skill so `npx skills` groups them under the plugin.
- `plugins/spec-monkey/.claude-plugin/plugin.json`: the Claude Code plugin manifest.

## The maintenance contract

Behavior lives in the skills; the README and the manifests describe them. Change one, change the others in the same commit.

- **Skill set:** the plugin ships four skills. If you add, remove, or rename one, update the README's four-skill table and prose, the `skills` array in `marketplace.json`, and the plugin and marketplace descriptions together. A skill's `name` must match its directory name.
- **Version:** the package version lives in two places that must match: the `version` in the `marketplace.json` plugin entry and the `version` in `plugin.json`. Claude Code treats `plugin.json` as authoritative, so bump both together. Each skill also carries its own top-level `version` field; bump that when you change that skill's behavior.
- **Portability:** keep install and usage language harness-neutral. Harness-specific hints (`model`, `effort`, `argument-hint`) go under `metadata:`, where a harness that doesn't read them just skips them. Never require a subagent, a hook, or context forking from inside a skill. Only a handful of harnesses have those, so anything that depends on one stops being portable.
- **Descriptions:** `name` and `description` load at startup for every skill, so every token has to earn its place. Lead with the trigger, keep the description near 130 tokens or under, and push the detail into the body and the reference files.
- **One home for the spec format:** the format lives in `spec-template.md`. The rubric and `creating-specs` point at it; they don't restate it. If the format changes (a section, the `FR-`/`SC-` IDs, the `draft → approved → implemented` lifecycle), update the template, the rubric, and any README mention in one change.
- **WHAT and WHEN, never HOW:** a spec says what to build and when, not which file or symbol to edit. Don't let build detail leak into a skill or the template. The one exception is the verification commands, which belong in the spec.

## Editing a skill

- Keep the YAML frontmatter valid, in both formatting and indentation.
- The body under the frontmatter is the product. Edit it like a careful instruction document, not code.
- Keep reference files one level deep from `SKILL.md`, and move heavy detail down into them so the always-loaded body stays lean.
