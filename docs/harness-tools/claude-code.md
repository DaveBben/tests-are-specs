# Claude Code tool mapping

How spec-monkey's action vocabulary resolves on Claude Code.

| Action the skills name | Claude Code tool |
|---|---|
| Invoke a skill | The `Skill` tool. Installed as a plugin, skills are namespaced: `spec-monkey:running-lifecycle` etc. A user can also type the slash command `/spec-monkey:<skill-name>`. |
| Dispatch a subagent | The `Task` tool with `subagent_type: "general-purpose"`. Pass the model explicitly per `subagent-mode.md`'s "Model selection" — an omitted `model` inherits the session's. For a fresh-context review or audit, the dispatch prompt is just the spec folder path plus the skill to run. |
| Open a new session with an empty context | `/clear`, or start a new conversation. Rarely needed here — Claude Code has subagents, so prefer dispatching one. |
| Run the spec linter | The `Bash` tool: `python3 tools/spec-lint.py docs/specs` (add `--status` for the roll-up). |
| Read / write files, run shell commands | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`. |

## Auto-start

The optional session bootstrap (`hooks/session-start.sh`) injects the `running-lifecycle` router line at session start. Wire it with `hooks/install-hook.sh` (or `--user`); it merges one `SessionStart` entry into your settings.json idempotently. Off by default. See [`../../hooks/README.md`](../../hooks/README.md).

## Notes

- The three dispatch prompts (`implementer-prompt.md`, `reviewer-prompt.md`, `fixer-prompt.md`) map their `Dispatch a subagent:` header to one `Task` call each: the prompt block goes in `prompt`, the `description:` slot in `description`, the `model:` slot in `model`.
- Task tracking in spec-monkey is file-based (`.spec-monkey/progress.md`) and needs no tool mapping; `TodoWrite` is fine for your own session bookkeeping but never replaces the ledger.
