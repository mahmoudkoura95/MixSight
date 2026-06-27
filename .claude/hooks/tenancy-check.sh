#!/usr/bin/env bash
# tenancy-check.sh — Flag new FastAPI route handlers that take client_id or organization_id
# without enforce_client_access / enforce_organization_access in their dependency chain.
#
# Hook input (stdin, JSON): { "tool_input": { "file_path": "...", ... } }
# Exit 0 = pass; exit 1 = block; exit 2 = warn (advisory).
#
# This is advisory — the authoritative gate is apps/api/tenancy/audit_routes.py
# which runs at app startup and fails boot on violations. The hook catches issues
# at edit-time so you don't have to discover them via failed CI.

set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))" 2>/dev/null || echo "")

# Only check Python files in apps/api/routes/ or apps/api/jobs/
case "$file_path" in
  *apps/api/routes/*.py|*apps/api/jobs/*.py) ;;
  *) exit 0 ;;
esac

[ -f "$file_path" ] || exit 0

# Find route handler functions that take a client_id or organization_id parameter
# but don't have the matching enforce_*_access dependency.
violations=$(python3 - "$file_path" <<'PY'
import ast, sys

path = sys.argv[1]
with open(path) as f:
    src = f.read()
try:
    tree = ast.parse(src)
except SyntaxError:
    sys.exit(0)

violations = []
for node in ast.walk(tree):
    if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        continue

    is_route = any(
        (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in {"get","post","put","patch","delete"})
        or (isinstance(d, ast.Attribute) and d.attr in {"get","post","put","patch","delete"})
        for d in node.decorator_list
    )
    if not is_route:
        continue

    args = [a.arg for a in node.args.args]
    defaults_src = ast.unparse(node)

    needs_client_check = "client_id" in args
    needs_org_check = "organization_id" in args

    has_client_check = "enforce_client_access" in defaults_src
    has_org_check = "enforce_organization_access" in defaults_src

    if needs_client_check and not has_client_check:
        violations.append(f"{path}:{node.lineno} `{node.name}` takes client_id but no enforce_client_access dependency")
    if needs_org_check and not has_org_check:
        violations.append(f"{path}:{node.lineno} `{node.name}` takes organization_id but no enforce_organization_access dependency")

for v in violations:
    print(v)
PY
)

if [ -n "$violations" ]; then
  echo "⚠ tenancy-check.sh: potential tenancy enforcement gaps detected:"
  echo "$violations"
  echo ""
  echo "Resolve by adding the appropriate Depends() in the function signature, then run:"
  echo "  cd apps/api && python -m tenancy.audit_routes"
  echo ""
  echo "See .claude/skills/tenancy/SKILL.md for the pattern."
  exit 2  # advisory — does not block
fi

exit 0
