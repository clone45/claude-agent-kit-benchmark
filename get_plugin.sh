#!/usr/bin/env bash
# Fetch the plugin under test at the exact commit used, and apply the one-line change we made
# (docs/deviations.md): the SessionStart hook also fires for forked sessions.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
COMMIT=c8dfca76f0085ea2406fd30db6ff33dc53923489
if [ ! -d "$HERE/plugin/.git" ]; then
  git clone --quiet https://github.com/FlaviusBurghila/claude-agent-kit "$HERE/plugin"
fi
git -C "$HERE/plugin" checkout --quiet "$COMMIT"
git -C "$HERE/plugin" apply --check "$HERE/plugin.patch" 2>/dev/null && git -C "$HERE/plugin" apply "$HERE/plugin.patch"
echo "plugin at $(git -C "$HERE/plugin" rev-parse --short HEAD) with plugin.patch applied:"
grep -n '"matcher"' "$HERE/plugin/hooks/hooks.json"
