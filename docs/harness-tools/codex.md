# Codex tool mapping

How spec-monkey's action vocabulary resolves on OpenAI Codex.

| Action the skills name | Codex tool |
|---|---|
| Invoke a skill | Codex surfaces installed skills natively; invoke the skill by name. If no skill tool is exposed, read the skill's `SKILL.md` directly with the file-read tool — on a harness without a skill tool, that *is* the sanctioned mechanism, not a violation of anything. |
| Dispatch a subagent | `spawn_agent` / `wait_agent` / `close_agent`, gated behind multi-agent support (see below). Always `close_agent` an implementer, reviewer, or fixer when it has finished all its work. |
| Open a new session with an empty context | Start a new Codex session (`/new`, or a fresh `codex` invocation) pointed at the spec path. |
| Run the spec linter | The shell tool: `python3 tools/spec-lint.py docs/specs`. |
| Read / write files, run shell commands | Codex's native file and shell tools (`apply_patch`-style edits, shell execution). |

## Enabling subagents

Subagent dispatch requires multi-agent support in your Codex config (`~/.codex/config.toml`):

```toml
[features]
multi_agent = true
```

Without it, the dispatch tools don't exist: run `implementing-specs`' single-agent workflow, and use a new session for fresh-context reviews. Never fabricate a `spawn_agent` call.

## Auto-start

Codex runs no session-start hook, and the `.codex-plugin/plugin.json` manifest declares an empty `hooks` object to keep it that way. Auto-start therefore has no Codex glue: begin the flow by invoking `running-lifecycle` by name.
