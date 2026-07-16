# Optional session bootstrap: auto-start the lifecycle

This directory is **not part of the portable plugin.** It holds the optional session-start bootstrap that auto-starts the `running-lifecycle` skill from the first message of a session, plus the per-harness glue that wires it in. It is opt-in and off by default, so `plugins/spec-monkey/` stays plain, portable Markdown that depends on no hook anywhere.

## Why it lives here, not in the plugin

spec-monkey's skills are portable: they must run in any harness, so they never depend on a hook, a subagent, or context forking. Auto-triggering a skill needs a session hook, which only some harnesses have. The portable pattern (the same one superpowers uses) keeps a single skills directory as the source of truth and puts each harness's integration in separate files outside the skills. The skill stays universal; this directory is the harness-specific glue you can choose to add. The per-harness *tool* mappings live next door in [`docs/harness-tools/`](../docs/harness-tools/), and the full architecture is in [`docs/porting-to-a-new-harness.md`](../docs/porting-to-a-new-harness.md).

The `metadata.best-in: claude-code` field on the `running-lifecycle` skill records that this glue exists; the skill itself still runs anywhere without it.

## What it does

On session start, [`session-start.sh`](session-start.sh) injects one short router line so an agent recognizes a build request and reaches for `running-lifecycle` instead of jumping to code:

> If the user is starting to build a project or feature, invoke the `running-lifecycle` skill to drive the full spec-monkey flow (ground → shape → review-design → write → review-spec → implement → audit), pausing at every human approval gate. For a single phase, invoke that phase's skill directly.

## One script, many harnesses

Shell-hook harnesses agree on the mechanism (run a command at session start, read JSON from its stdout) but not on the JSON shape. `session-start.sh` sniffs environment variables and emits exactly the shape the current harness consumes:

| Harness | Detected by | Emits |
|---|---|---|
| Cursor | `CURSOR_PLUGIN_ROOT` | `{"additional_context": "..."}` |
| Claude Code | `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PROJECT_DIR`, without `COPILOT_CLI` | `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}` |
| Copilot CLI / SDK standard | anything else | `{"additionalContext": "..."}` |

It emits exactly one field on purpose: a harness that reads more than one shape without de-duplicating would inject the line twice. Adding a harness means adding an env-var branch (ordered before any branch whose variable your harness also sets) — see the porting guide.

## How to enable it, per harness

### Claude Code (turnkey installer)

From the repo root, run one command. [`install-hook.sh`](install-hook.sh) merges a single `SessionStart` entry into your Claude Code settings, with the shipped script's absolute path resolved for you — no hand-typed paths:

```bash
hooks/install-hook.sh            # this project only: ./.claude/settings.json
hooks/install-hook.sh --user     # every session:     ~/.claude/settings.json
```

It is **idempotent** (run it twice, the second run is a no-op), it **merges** into an existing settings file rather than overwriting it, and it prints how to undo it (delete the one `SessionStart` entry it added). Restart Claude Code, or start a new session, and "let's build X" now reaches for `running-lifecycle`. Needs `python3` (already a dependency of `tools/spec-lint.py`).

Preview without changing anything:

```bash
hooks/install-hook.sh --print    # prints the exact settings block
```

Prefer hand-editing? Paste the `--print` output into your settings, or point a `SessionStart` command entry at `session-start.sh` wherever the repo lives.

### Cursor (rides the plugin install)

The Cursor adapter at the repo root (`.cursor-plugin/plugin.json`) declares `"hooks": "./hooks/hooks-cursor.json"`, which runs `session-start.sh` at `sessionStart`. Installing the Cursor plugin is the opt-in — Cursor loads nothing from this repo otherwise. Don't want the auto-start? Remove the `hooks` line from your installed copy of the manifest.

Note Cursor's hook-config schema is its own (`"version": 1`, lowercase `sessionStart`, a relative command, no matcher). Don't copy the Claude Code block into it.

### Codex (no hook, by design)

Codex runs no session-start hook; its adapter (`.codex-plugin/plugin.json`) declares an empty `hooks` object to say so explicitly. Start the flow by invoking `running-lifecycle` by name.

### Other shell-hook harnesses

The script's fallback branch already emits the SDK-standard shape (`additionalContext`, top-level), which Copilot CLI and several others consume. Register `session-start.sh` as a session-start hook through your harness's own config mechanism. If your harness needs a different field or nesting, add a branch — see [`docs/porting-to-a-new-harness.md`](../docs/porting-to-a-new-harness.md).

## What not to do

- Do not move this into `plugins/spec-monkey/`. A hook auto-discovered inside the plugin would fire for every user and break the "portable, no required hooks" contract.
- Do not make any skill depend on this hook. The skills must work with it absent.
- Do not emit more than one JSON shape from one run. Wrong-field or extra-field output either never injects or injects twice.
