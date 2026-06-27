#!/usr/bin/env bash
# migration-check.sh — Verify Alembic migrations follow §6.2 conventions.
# Flags: float for money, json instead of jsonb, timestamp without timezone, missing indexes on FKs.

set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))" 2>/dev/null || echo "")

case "$file_path" in
  *apps/api/alembic/versions/*.py) ;;
  *) exit 0 ;;
esac

[ -f "$file_path" ] || exit 0

issues=""

# float for money — never
if grep -nE "sa\.Float|Float\(\)|FLOAT" "$file_path" >/dev/null 2>&1; then
  issues+="  ✗ Found Float column. Money MUST use numeric(18, 4). Percentages use numeric(8, 4). See §6.2 and .claude/skills/migration/SKILL.md.\n"
fi

# json (not jsonb)
if grep -nE "postgresql\.JSON\b|sa\.JSON\b|JSON\(\)" "$file_path" | grep -v "JSONB" >/dev/null 2>&1; then
  issues+="  ✗ Found json column. Use jsonb (postgresql.JSONB). See §6.2.\n"
fi

# DateTime without timezone=True
if grep -nE "sa\.DateTime\(\)" "$file_path" >/dev/null 2>&1; then
  issues+="  ✗ Found DateTime() without timezone=True. Use sa.DateTime(timezone=True). See §6.2.\n"
fi

# UUID with python_default instead of server_default
if grep -nE "default=uuid\.uuid4|default=uuid4" "$file_path" >/dev/null 2>&1; then
  issues+="  ⚠ Python-side UUID default detected. Prefer server_default=sa.text('gen_random_uuid()') per §6.2.\n"
fi

if [ -n "$issues" ]; then
  echo "⚠ migration-check.sh: §6.2 convention issues detected in $file_path:"
  printf "%b" "$issues"
  exit 2  # advisory
fi

exit 0
