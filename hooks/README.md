# Optional Claude Code hook: auto-start the lifecycle

This directory is **not part of the portable plugin.** It holds an optional, Claude-Code-only enhancement that auto-starts the `running-lifecycle` skill from the first message of a session. It is opt-in and off by default, so `plugins/spec-monkey/` stays plain, portable Markdown that depends on no hook anywhere.

## Why it lives here, not in the plugin

spec-monkey's skills are portable: they must run in any harness, so they never depend on a hook, a subagent, or context forking. Auto-triggering a skill needs a session hook, which only some harnesses have. The portable pattern (the same one Superpowers uses) keeps a single skills directory as the source of truth and puts each harness's integration in separate files outside the skills. So the skill stays universal, and this hook is the Claude-Code-specific glue you can choose to add.

The `metadata.best-in: claude-code` field on the `running-lifecycle` skill records that this glue exists; the skill itself still runs anywhere without it.

## What it does

On session start, it injects one short router line so an agent recognizes a build request and reaches for `running-lifecycle` instead of jumping to code:

> If the user is starting to build a project or feature, invoke the `running-lifecycle` skill to drive the full spec-monkey flow (ground → shape → write → review → implement → audit), pausing at every human approval gate. For a single phase, invoke that phase's skill directly.

## How to enable it (opt-in)

Add a SessionStart hook to your Claude Code settings that emits that line as `additionalContext`. A minimal example (verify the shape against your Claude Code version):

`hooks.json`
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "./hooks/session-start.sh" } ] }
    ]
  }
}
```

`hooks/session-start.sh`
```bash
#!/usr/bin/env bash
router='If the user is starting to build a project or feature, invoke the running-lifecycle skill to drive the full spec-monkey flow (ground, shape, write, review, implement, audit), pausing at every human approval gate. For a single phase, invoke that phase skill directly.'
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}' "$router"
```

That is the whole enhancement. Remove it and nothing about spec-monkey changes except that you invoke `running-lifecycle` by name instead of it auto-suggesting itself.

## What not to do

- Do not move this into `plugins/spec-monkey/`. A hook auto-discovered inside the plugin would fire for every Claude Code user and break the "portable, no required hooks" contract.
- Do not make any skill depend on this hook. The skills must work with it absent.
