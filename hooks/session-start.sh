#!/usr/bin/env bash
# Optional multi-harness session-start bootstrap for spec-monkey.
#
# It injects one router line so an agent recognizes a build request and reaches
# for `running-lifecycle` instead of jumping straight to code. Opt-in and off by
# default; the portable plugin depends on nothing here. See this directory's README.
#
# The same script serves every shell-hook harness by sniffing environment
# variables and emitting the JSON shape that harness consumes (the pattern
# superpowers' hooks/session-start established). The shapes differ, and a
# harness that reads more than one field can double-inject, so emit exactly one:
#
#   Cursor            {"additional_context": "..."}                     (snake_case, top-level)
#   Claude Code       {"hookSpecificOutput": {"hookEventName":
#                       "SessionStart", "additionalContext": "..."}}    (nested)
#   SDK standard      {"additionalContext": "..."}                      (Copilot CLI and others)
#
# Detection notes:
# - Cursor sets CURSOR_PLUGIN_ROOT (and may also set CLAUDE_PLUGIN_ROOT), so
#   its branch comes first.
# - Claude Code sets CLAUDE_PLUGIN_ROOT for plugin-registered hooks, but this
#   hook is usually wired through settings.json (see install-hook.sh), where
#   Claude Code sets CLAUDE_PROJECT_DIR instead. Check both.
# - Copilot CLI sets COPILOT_CLI=1 and takes the SDK-standard shape, as does
#   any unrecognized harness.
set -euo pipefail

router='If the user is starting to build a project or feature, invoke the running-lifecycle skill to drive the full spec-monkey flow (ground, shape, review-design, write, review-spec, implement, audit), pausing at every human approval gate. For a single phase, invoke that phase skill directly.'

if [ -n "${CURSOR_PLUGIN_ROOT:-}" ]; then
  printf '{"additional_context":"%s"}\n' "$router"
elif { [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || [ -n "${CLAUDE_PROJECT_DIR:-}" ]; } && [ -z "${COPILOT_CLI:-}" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$router"
else
  printf '{"additionalContext":"%s"}\n' "$router"
fi

exit 0
