#!/usr/bin/env bash
# phase-reminder.sh — Inject CURRENT_PHASE.md state into Claude's context at every prompt.
# Keeps phase discipline tight across long sessions where state-recall drifts.

set -euo pipefail

if [ ! -f CURRENT_PHASE.md ]; then
  exit 0
fi

# Read the top of CURRENT_PHASE.md — just the state block, not the full file
phase_block=$(head -n 8 CURRENT_PHASE.md | tail -n +3)

# Emit as additional context. Claude Code recognizes stdout from UserPromptSubmit hooks
# as additional context to attach to the message.
cat <<EOF
[Phase state from CURRENT_PHASE.md]
$phase_block
[end phase state]

Reminder: cite a SCOPE.md section before proposing work. If the request would ship something from a later phase, flag it explicitly. See root CLAUDE.md.
EOF

exit 0
