# Cursor tool mapping

How spec-monkey's action vocabulary resolves on Cursor.

| Action the skills name | Cursor tool |
|---|---|
| Invoke a skill | Cursor discovers the skills the plugin manifest points at (`.cursor-plugin/plugin.json` → `plugins/spec-monkey/skills/`); invoke the skill by name. If no skill tool is exposed, read the skill's `SKILL.md` directly with the file-read tool — on a harness without a skill tool, that *is* the sanctioned mechanism. |
| Dispatch a subagent | Use Cursor's background/parallel agent facility if your version exposes one to the model. If none is exposed, the capability is absent: do the work inline and use a new chat for fresh context. Never fabricate a dispatch call. |
| Open a new session with an empty context | Start a new chat pointed at the spec path. This is the default fresh-context mechanism on Cursor. |
| Run the spec linter | The terminal tool: `python3 tools/spec-lint.py docs/specs`. |
| Read / write files, run shell commands | Cursor's native read/edit/search and terminal tools. |

## Auto-start

Installing the Cursor plugin wires the session bootstrap: `.cursor-plugin/plugin.json` declares `"hooks": "./hooks/hooks-cursor.json"`, which runs `hooks/session-start.sh` at `sessionStart`. The script detects Cursor via `CURSOR_PLUGIN_ROOT` and emits the snake_case shape Cursor consumes (`{"additional_context": "..."}`). Installing the Cursor plugin is the opt-in; skip the plugin's hook entry if you don't want it. See [`../../hooks/README.md`](../../hooks/README.md).
