// tenancy-check.mjs — Flag FastAPI route handlers that take client_id /
// organization_id without enforce_client_access / enforce_organization_access
// in their signature. Advisory (exit 2); the authoritative gate is the
// startup audit in apps/api/src/mixsight/tenancy/audit.py.
//
// PostToolUse on Edit|Write|MultiEdit. Node, not python (python3 isn't on the
// hook PATH here). Regex-based, not AST — good enough for an edit-time nudge.

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
if (!/apps[/\\]api[/\\]src[/\\]/.test(fp)) allow();
if (/[/\\]tests[/\\]|__pycache__/.test(fp)) allow();

let src;
try {
  src = fs.readFileSync(fp, "utf8");
} catch {
  allow();
}

const ROUTE_DEC = /@[\w.]+\.(get|post|put|patch|delete)\s*\(/;
const lines = src.split(/\r?\n/);
const violations = [];

for (let i = 0; i < lines.length; i++) {
  if (!ROUTE_DEC.test(lines[i])) continue;

  // Find the handler def within a few lines (skip stacked decorators).
  let j = i + 1;
  while (j < lines.length && j < i + 8 && !/^\s*(async\s+def|def)\s+\w+\s*\(/.test(lines[j])) j++;
  if (j >= lines.length || !/^\s*(async\s+def|def)\s+\w+\s*\(/.test(lines[j])) continue;

  const fnName = (lines[j].match(/(?:async\s+def|def)\s+(\w+)\s*\(/) || [])[1] || "?";

  // Capture the signature by balancing parens from the def's first '('.
  const tail = lines.slice(j).join("\n");
  const start = tail.indexOf("(");
  let depth = 0;
  let end = -1;
  for (let k = start; k < tail.length; k++) {
    if (tail[k] === "(") depth++;
    else if (tail[k] === ")") {
      depth--;
      if (depth === 0) {
        end = k;
        break;
      }
    }
  }
  const sig = end >= 0 ? tail.slice(start, end + 1) : tail.slice(start, start + 2000);

  if (/\bclient_id\b/.test(sig) && !/enforce_client_access/.test(sig)) {
    violations.push(`${fp}:${j + 1} \`${fnName}\` takes client_id but no enforce_client_access dependency`);
  }
  if (/\borganization_id\b/.test(sig) && !/enforce_organization_access/.test(sig)) {
    violations.push(
      `${fp}:${j + 1} \`${fnName}\` takes organization_id but no enforce_organization_access dependency`,
    );
  }
}

if (violations.length) {
  process.stderr.write(
    [
      "⚠ tenancy-check: potential tenancy enforcement gaps:",
      ...violations.map((v) => "  " + v),
      "",
      "Add the matching Depends(enforce_*_access) to the signature.",
      "Authoritative gate: apps/api/src/mixsight/tenancy/audit.py (fails app boot).",
      "See .claude/skills/tenancy/SKILL.md.",
    ].join("\n") + "\n",
  );
  process.exit(2);
}
allow();
