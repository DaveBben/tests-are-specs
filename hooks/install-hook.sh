#!/usr/bin/env bash
# One-command installer for the optional spec-monkey SessionStart hook — the
# Claude Code path. (Other harnesses wire the same session-start.sh through
# their own mechanism: Cursor via .cursor-plugin/plugin.json + hooks-cursor.json;
# see hooks/README.md.)
#
# It merges a single SessionStart entry into a Claude Code settings.json, pointing
# at the shipped session-start.sh (resolved to an absolute path here, so you never
# hand-type one). Idempotent: run it twice and the second run is a no-op. Reversible:
# it prints the exact block to delete to undo it.
#
# This does NOT touch the portable plugin. The plugin stays hook-free; this only
# edits YOUR settings file, which you chose to run.
#
# Usage:
#   hooks/install-hook.sh            # project settings: ./.claude/settings.json
#   hooks/install-hook.sh --user     # user settings:    ~/.claude/settings.json
#   hooks/install-hook.sh --print    # print the settings block, change nothing
#   hooks/install-hook.sh PATH       # a settings.json path you name
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script="$here/session-start.sh"

target=""
print_only=0
for arg in "$@"; do
  case "$arg" in
    --user)  target="$HOME/.claude/settings.json" ;;
    --print) print_only=1 ;;
    -h|--help)
      grep '^#' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)       target="$arg" ;;
  esac
done
[ -n "$target" ] || target="$(pwd)/.claude/settings.json"

if [ ! -f "$script" ]; then
  echo "error: shipped hook not found at $script" >&2; exit 1
fi
chmod +x "$script" 2>/dev/null || true

command -v python3 >/dev/null 2>&1 || { echo "error: python3 is required" >&2; exit 1; }

python3 - "$target" "$script" "$print_only" <<'PY'
import json, os, sys

target, script, print_only = sys.argv[1], sys.argv[2], sys.argv[3] == "1"

entry = {"hooks": [{"type": "command", "command": script}]}
block = {"hooks": {"SessionStart": [entry]}}

if print_only:
    print(json.dumps(block, indent=2))
    sys.exit(0)

if os.path.exists(target):
    with open(target, encoding="utf-8") as f:
        text = f.read().strip()
    settings = json.loads(text) if text else {}
else:
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    settings = {}

hooks = settings.setdefault("hooks", {})
starts = hooks.setdefault("SessionStart", [])

def points_at_script(e):
    return any(
        h.get("type") == "command" and h.get("command") == script
        for h in e.get("hooks", [])
    )

if any(points_at_script(e) for e in starts):
    print(f"already installed in {target} — no change")
    sys.exit(0)

starts.append(entry)
with open(target, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
print(f"installed spec-monkey SessionStart hook in {target}")
print(f"  -> {script}")
print("restart Claude Code (or start a new session) to pick it up.")
print("to undo: remove that SessionStart entry from the file.")
PY
