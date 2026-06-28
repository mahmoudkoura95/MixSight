// audit-log-check.mjs — Flag patterns that bypass the SQLAlchemy AuditLog hook:
// bulk ORM mappings, raw SQL UPDATE/DELETE/INSERT, direct engine/connection
// execute. Advisory (exit 2). Node, not python (python3 not on hook PATH).
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
// Skip Alembic migrations, the audit module itself, and tests.
if (/[/\\]migrations[/\\]|[/\\]mixsight[/\\]audit[/\\]|[/\\]tests[/\\]/.test(fp)) allow();

let src;
try {
  src = fs.readFileSync(fp, "utf8");
} catch {
  allow();
}

const issues = [];
if (/bulk_insert_mappings|bulk_save_objects|bulk_update_mappings/.test(src)) {
  issues.push("Bulk ORM mapping detected — the audit hook may not fire; write AuditLog rows explicitly.");
}
if (/text\(\s*["'`]\s*(UPDATE|DELETE|INSERT)/i.test(src)) {
  issues.push("Raw SQL UPDATE/DELETE/INSERT detected — the audit hook does not fire on raw SQL.");
}
if (/engine\.execute|connection\.execute/.test(src)) {
  issues.push("Direct engine/connection execute detected — the audit hook does not fire on these paths.");
}

if (issues.length) {
  process.stderr.write(
    [
      `⚠ audit-log-check: potential audit-log bypass in ${fp}:`,
      ...issues.map((s) => "  " + s),
      "  If intentional (e.g. bulk backfill), write AuditLog rows in the same transaction and",
      "  document in DECISIONS.md. See .claude/skills/audit-log/SKILL.md (§7.4).",
    ].join("\n") + "\n",
  );
  process.exit(2);
}
allow();
