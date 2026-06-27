#!/usr/bin/env bash
# llm-fallback-check.sh — Flag direct Anthropic SDK calls outside the wrapped client,
# and messages.create calls without a documented fallback annotation.

set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))" 2>/dev/null || echo "")

case "$file_path" in
  *.py) ;;
  *) exit 0 ;;
esac

[ -f "$file_path" ] || exit 0

# Allow direct calls only inside apps/api/llm/
case "$file_path" in
  *apps/api/llm/*) exit 0 ;;
esac

# Anything that uses anthropic SDK directly outside apps/api/llm/ is a violation
if grep -nE "from anthropic|import anthropic|AsyncAnthropic\(|Anthropic\(" "$file_path" >/dev/null 2>&1; then
  echo "✗ llm-fallback-check.sh: Direct anthropic SDK usage detected in $file_path."
  echo ""
  echo "  All LLM calls must go through apps/api/llm/client.py (the WrappedLLMClient)."
  echo "  This ensures BYOK resolution, quota counting, retry, and surface-specific fallback are consistent."
  echo ""
  echo "  See SCOPE.md §7.17 and .claude/skills/llm-call/SKILL.md."
  exit 2  # advisory
fi

# messages.create calls without a documented fallback annotation
suspicious=$(grep -nE "messages\.create|\.completions\.create" "$file_path" || true)
if [ -n "$suspicious" ]; then
  # Look for the wrapper or a fallback comment within 5 lines above
  echo "⚠ llm-fallback-check.sh: messages.create detected outside apps/api/llm/:"
  echo "$suspicious"
  echo ""
  echo "  Route through WrappedLLMClient.call instead. See .claude/skills/llm-call/SKILL.md."
  exit 2
fi

exit 0
