// llm-fallback-check.mjs — Flag direct Anthropic SDK usage outside the wrapped
// client (apps/api/src/mixsight/llm/), and messages.create calls that should
// route through it. Advisory (exit 2). Node, not python.
//
// PostToolUse on Edit|Write|MultiEdit.

import fs from "node:fs";

const allow = () => process.exit(0);

let data;
try {
  data = JSON.parse(fs.readFileSync(0, "utf8"));
} catch {
  allow();
}
const fp = (data && data.tool_input && data.tool_input.file_path) || "";

if (!/\.py$/.test(fp)) allow();
// Direct SDK use is allowed only inside the wrapped LLM client module.
if (/[/\\]mixsight[/\\]llm[/\\]/.test(fp)) allow();

let src;
try {
  src = fs.readFileSync(fp, "utf8");
} catch {
  allow();
}

if (/from anthropic|import anthropic|AsyncAnthropic\(|Anthropic\(/.test(src)) {
  process.stderr.write(
    [
      `✗ llm-fallback-check: direct anthropic SDK usage in ${fp}.`,
      "  All LLM calls must go through apps/api/src/mixsight/llm/client.py (WrappedLLMClient):",
      "  BYOK resolution, quota counting, retry, and surface-specific fallback live there.",
      "  See SCOPE.md §7.17 and .claude/skills/llm-call/SKILL.md.",
    ].join("\n") + "\n",
  );
  process.exit(2);
}

const suspicious = src
  .split(/\r?\n/)
  .map((ln, idx) => ({ ln, n: idx + 1 }))
  .filter((x) => /messages\.create|\.completions\.create/.test(x.ln));

if (suspicious.length) {
  process.stderr.write(
    [
      `⚠ llm-fallback-check: messages.create outside the wrapped client in ${fp}:`,
      ...suspicious.map((x) => `  ${fp}:${x.n}`),
      "  Route through WrappedLLMClient.call instead. See .claude/skills/llm-call/SKILL.md (§7.17).",
    ].join("\n") + "\n",
  );
  process.exit(2);
}
allow();
