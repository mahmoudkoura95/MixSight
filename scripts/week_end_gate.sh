#!/usr/bin/env bash
# week_end_gate.sh — Mechanical quality gate for the /week-end ritual.
#
# Runs the full non-destructive quality bar (api: ruff + mypy + pytest;
# web: typecheck + lint + build). On a FULL pass it writes the sentinel
# .claude/.week-end-pass recording the week, timestamp, and git HEAD. The
# week-close hook (.claude/hooks/week-end-gate.sh) refuses to let
# CURRENT_PHASE.md flip a week to "(complete)" unless that sentinel matches.
#
# Usage:  bash scripts/week_end_gate.sh <week-number>
#
# Pre-req: Postgres up (make up) — pytest needs it. The destructive Alembic
# down/up round-trip is NOT run here (it wipes the dev DB); run it separately
# against a disposable DB per the ritual, and CI runs it on every push.

set -euo pipefail

WEEK="${1:-}"
if [ -z "$WEEK" ]; then
  echo "usage: bash scripts/week_end_gate.sh <week-number>" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== week-end gate: API (ruff / mypy / pytest) =="
(
  cd apps/api
  uv run ruff check src tests scripts
  uv run ruff format --check src tests scripts
  uv run mypy src
  uv run pytest -q
)

echo "== week-end gate: web (typecheck / lint / build) =="
pnpm --filter @mixsight/web typecheck
pnpm --filter @mixsight/web lint
pnpm --filter @mixsight/web build

# All gates passed — record the sentinel the week-close hook checks for.
mkdir -p .claude
{
  echo "WEEK=$WEEK"
  echo "PASSED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "HEAD=$(git rev-parse HEAD 2>/dev/null || echo nogit)"
} > .claude/.week-end-pass

echo ""
echo "✓ week-end mechanical gate PASSED for week $WEEK"
echo "  Sentinel written: .claude/.week-end-pass"
echo "  Still required before flipping CURRENT_PHASE.md to (complete):"
echo "    - /code-review --effort high  (findings fixed or deferred-with-reason)"
echo "    - /simplify on the week's diff (refactor applied or deferred-with-reason)"
echo "    - every new feature names its contract test"
echo "    - SHIPPED.md updated with the Week $WEEK close-ritual record"
