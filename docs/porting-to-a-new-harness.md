# Porting spec-monkey to a new harness

This guide explains how to make spec-monkey work — and, where possible, auto-trigger — on a harness that isn't Claude Code: another CLI, an IDE agent, an agent runner. It follows the architecture superpowers proved out (see its `docs/porting-to-a-new-harness.md`); this is spec-monkey's version of the same invariants.

The one-sentence summary: **the skills are the same everywhere; a port only adds a thin per-harness adapter that delivers them and translates their action words into real tools.** When this guide and the files disagree, the files win; fix the guide.

## The three-component architecture

1. **Skills (harness-agnostic).** Everything under `plugins/spec-monkey/skills/` is the source of truth, shared verbatim by every harness. Skills follow the open Agent Skills standard (agentskills.io): a `SKILL.md` with `name` + `description` frontmatter and a Markdown body, plus reference files. The standard standardizes only the SKILL.md file; hooks, subagents, and triggering are harness glue and live outside it.

2. **Tool mapping (per-harness).** Skill bodies describe *actions* — "invoke a skill," "dispatch a subagent," "open a new session with an empty context," "run the spec linter" — and never name a tool. Each supported harness gets a file in [`docs/harness-tools/`](harness-tools/) translating that vocabulary into its real tool names. That directory's README lists the full action vocabulary a mapping must cover.

3. **Bootstrap (per-harness, optional).** Auto-starting the flow from the first "let's build X" message needs the harness to inject a router line at session start. That glue lives in `hooks/` and the per-harness manifest dirs at the repo root — never inside the plugin, and always opt-in. Without it nothing breaks; the user starts the flow by invoking `running-lifecycle` by name.

### The rule that makes it work: skills name actions, not tools

Do **not** edit a skill body to fit your harness. No `Task`, no `TodoWrite`, no `subagent_type`, no slash-command syntax, no `.claude/` paths inside `plugins/spec-monkey/skills/`. If a port seems to need a skill edit, the fix belongs in your tool-mapping file instead. Skill content is behavior-shaping instruction text under a testing discipline (`docs/testing-skill-changes.md`); rewording it for harness compliance is a regression, not a port.

## Can the harness run spec-monkey at all?

spec-monkey has two hard requirements and several degradable ones.

| Capability | Needed by | If absent |
|---|---|---|
| **File read / write / edit** | every skill — specs, designs, contracts, and the build ledger are files | **Hard requirement. No workaround.** |
| **Run shell commands** | `implementing-specs` (tests, verification commands), `auditing-specs` (re-running verification) | **Hard requirement** for those two; the authoring/review skills survive without it but can't run the linter. |
| Skill discovery + invocation | all — the skills must reach the model somehow | Degradable: with no skill tool, the sanctioned mechanism is reading the relevant `SKILL.md` with the file-read tool. Say so in your mapping. |
| Subagent dispatch | fresh-context reviews/audit; `implementing-specs`' opt-in orchestrated build | Degradable by design: the single-agent workflow is always the default, and fresh context falls back to a new session. The skills already say so; never fabricate a dispatch call. |
| Session-start injection | auto-starting `running-lifecycle` | Degradable: with no hook, the user invokes the skill by name. Auto-start is a convenience, never a dependency. |
| `python3` | `tools/spec-lint.py` (mechanical spec checks) | Degradable: `reviewing-specs` does the mechanical checks by hand under the rubric. |
| Todo / task tracking | none | spec-monkey tracks build progress in a file (`.spec-monkey/progress.md`); no tool needed. |

Note the difference from superpowers: superpowers treats session-start injection as the non-negotiable core of a port, because its bootstrap skill is the whole triggering story. spec-monkey's skills trigger through the harness's normal skill discovery (their `description` frontmatter leads with the trigger), so a port without any hook mechanism is still a full port — it just starts by name.

## How each skill degrades

| Skill | Optional capability it can use | Fallback when absent |
|---|---|---|
| `running-lifecycle` | subagent dispatch (fresh-context phases); session hook (auto-start) | tell the human to open a new session pointed at the spec path; invoke by name |
| `grounding-specs` | subagent dispatch (fresh-context review of the project spec) | a new session pointed at the spec |
| `shaping-specs` | subagent dispatch (fresh-context design review) | a new session pointed at the design |
| `reviewing-design` | none | — |
| `writing-specs` | subagent dispatch (fresh-context contract review) | a new session pointed at the spec folder |
| `reviewing-specs` | the spec linter | do the mechanical checks by hand under the rubric |
| `implementing-specs` | subagent dispatch (the orchestrated build, 3+ FR-groups) | the single-agent workflow in its SKILL.md — always sufficient |
| `auditing-specs` | none (runs best in a fresh context, however obtained) | a new session pointed at the spec |

## Steps to add a harness

1. **Study the closest existing adapter.** Shell-hook harness → Cursor (`.cursor-plugin/plugin.json` + `hooks/hooks-cursor.json` + `hooks/session-start.sh`). Native-skill-discovery harness with no session hook → Codex (`.codex-plugin/plugin.json`). superpowers' porting guide catalogs the further shapes (in-process plugins, instructions files) if your harness matches neither.

2. **Create the manifest.** Add `.<harness>-plugin/` (or whatever entry point the harness recognizes) at the repo root. Point its skills field at `./plugins/spec-monkey/skills/` — note the path differs from superpowers, whose skills sit at the repo root. Confirm empirically that the harness actually discovers the directory; a `skills` path field is not universally honored.

3. **Write the tool mapping.** Add `docs/harness-tools/<harness>.md` covering the full action vocabulary in `docs/harness-tools/README.md`. Get real tool names from the harness's docs or by asking a live session to enumerate its tools; never invent them. If the harness lacks a capability, point the mapping at the skills' existing fallback wording rather than papering over the gap.

4. **Wire the bootstrap, if the harness has a session-start surface.** If it runs a shell command at session start and reads JSON from stdout, extend `hooks/session-start.sh`: add an env-var branch that emits the exact JSON field/nesting your harness consumes, ordered before any branch whose env var your harness also sets. Emit exactly one shape — some harnesses read multiple fields without de-duplicating, and the wrong field fails silently or double-injects. Add a `hooks/hooks-<harness>.json` if the harness takes a hook-config file, matching *its* schema (compare `hooks-cursor.json` to the Claude Code block in `install-hook.sh` — they share nothing). Keep it opt-in: the plugin itself stays hook-free.

5. **Update the contract surfaces.** Add the new adapter to `AGENTS.md`'s key files, mention the harness in `README.md`'s install section, and bump the package version in `plugin.json` and `marketplace.json` together (new package-visible structure).

6. **Verify live.** Install through the harness's own mechanism, start a clean session, and check: (a) the skills are discoverable; (b) "let's build a small feature" reaches for `running-lifecycle` (with the bootstrap) or `running-lifecycle` invoked by name runs the flow (without it); (c) a fresh-context review resolves to a real mechanism from your mapping. Reading the code is not verification.

## What a port must never do

- Edit a skill body to name a harness tool. The mapping file is the only place tool names live.
- Move hooks inside `plugins/spec-monkey/`. A hook auto-discovered inside the plugin fires for every user of that harness and breaks the "portable, no required hooks" contract.
- Make any skill depend on the bootstrap, a subagent, or the linter. Optional capability, capability-gated wording, portable default path — that ordering is the contract (`AGENTS.md`, "Harness-specific glue lives outside the skills").
- Write into the user's own config files as an install step. Ship what the harness's install mechanism carries; `hooks/install-hook.sh` is the one sanctioned settings-merger, and it is explicitly opt-in, idempotent, and reversible.
