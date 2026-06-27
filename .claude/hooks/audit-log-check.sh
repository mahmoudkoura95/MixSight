#!/usr/bin/env bash
# audit-log-check.sh — Flag patterns that bypass the SQLAlchemy AuditLog hook:
# raw SQL UPDATE/DELETE, bulk operations, direct cursor use.

set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))" 2>/dev/null || echo "")

case "$file_path" in
  *.py) ;;
  *) exit 0 ;;
esac

# Skip migrations (Alembic) and the audit module itself
case "$file_path" in
  *apps/api/alembic/*) exit 0 ;;
  *apps/api/audit/*) exit 0 ;;
  *tests/*) exit 0 ;;
esac

[ -f "$file_path" ] || exit 0

issues=""

# bulk_*_mappings
if grep -nE "bulk_insert_mappings|bulk_save_objects|bulk_update_mappings" "$file_path" >/dev/null 2>&1; then
  issues+="  ⚠ Bulk ORM mapping detected. The audit hook may not fire — write AuditLog rows explicitly. See §7.4.\n"
fi

# Raw SQL statements
if grep -nE "text\([\"']\s*(UPDATE|DELETE|INSERT)" "$file_path" >/dev/null 2>&1; then
  issues+="  ⚠ Raw SQL UPDATE/DELETE/INSERT detected. The audit hook does not fire on raw SQL — write AuditLog rows explicitly. See .claude/skills/audit-log/SKILL.md.\n"
fi

# Direct engine.execute / connection.execute
if grep -nE "engine\.execute|connection\.execute" "$file_path" >/dev/null 2>&1; then
  issues+="  ⚠ Direct engine/connection execute detected. The audit hook does not fire on these paths. See .claude/skills/audit-log/SKILL.md.\n"
fi

if [ -n "$issues" ]; then
  echo "⚠ audit-log-check.sh: potential audit-log bypass in $file_path:"
  printf "%b" "$issues"
  echo "  If the bypass is intentional (e.g., bulk backfill), write AuditLog rows in the same transaction and document in DECISIONS.md."
  exit 2  # advisory
fi

exit 0
