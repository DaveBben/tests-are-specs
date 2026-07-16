# Per-harness tool mappings

spec-monkey's skills name **actions, never tools**: "dispatch a subagent," "open a new session with an empty context," "invoke a skill," "run the spec linter." That is what keeps one skill body portable across harnesses. Each file here translates that action vocabulary into one harness's real tool names, the same way superpowers keeps `*-tools.md` references per harness.

These mappings live outside `plugins/spec-monkey/skills/` on purpose. A skill body never names a harness tool; when an agent needs to resolve an action on its harness, the mapping here is where the answer lives. Adding a harness means adding a file here, never editing a skill (see [`../porting-to-a-new-harness.md`](../porting-to-a-new-harness.md)).

## The action vocabulary

Every mapping file covers these actions, in this order:

| Action (as the skills say it) | Where the skills say it |
|---|---|
| **Invoke a skill** | every `## Next step`; `running-lifecycle` throughout |
| **Dispatch a subagent** (fresh agent, isolated context, result read back) | the fresh-context reviews and audit; `implementing-specs`' opt-in orchestrated build and its three dispatch prompts |
| **Open a new session with an empty context** (the no-subagent fallback for fresh context) | `running-lifecycle` "Running a phase in fresh context"; `shaping-specs` and `writing-specs` "Next step" |
| **Run the spec linter** (optional) | `reviewing-specs` "How to review" |
| **Read / write files, run shell commands** | everywhere; specs are files and verification is commands |

Two of these degrade by design. No subagent tool → do the work inline and fall back to a new session for fresh context; never fabricate a dispatch call. No linter (no `python3`, or the repo doesn't ship `tools/spec-lint.py`) → do the mechanical checks by hand under the rubric. The skills already carry that fallback wording; the mapping's job is only to point at the real tool when one exists.

## Current mappings

- [`claude-code.md`](claude-code.md)
- [`codex.md`](codex.md)
- [`cursor.md`](cursor.md)
