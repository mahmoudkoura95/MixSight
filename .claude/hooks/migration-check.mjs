// migration-check.mjs — Verify Alembic migrations follow §6.2 conventions:
// no Float for money, jsonb not json, timestamptz not naive DateTime,
// server-side UUID default. Advisory (exit 2). Node, not python.
//
// PostToolUse on Edit|Write|MultiEdit. Targets apps/api/migrations/versions/.

import fs from "node:fs";

const allow = () => process.exit(0);

let data;
try {
  data = JSON.parse(fs.readFileSync(0, "utf8"));
} catch {
  allow();
}
const fp = (data && data.tool_input && data.tool_input.file_path) || "";

if (!/[/\\]migrations[/\\]versions[/\\][^/\\]*\.py$/.test(fp)) allow();

let src;
try {
  src = fs.readFileSync(fp, "utf8");
} catch {
  allow();
}

const issues = [];
if (/sa\.Float|Float\(\)|FLOAT/.test(src)) {
  issues.push("✗ Float column — money MUST be numeric(18, 4); percentages numeric(8, 4). §6.2");
}
// json (not jsonb): a line that mentions JSON but not JSONB.
if (
  src
    .split(/\r?\n/)
    .some((ln) => /(postgresql\.JSON\b|sa\.JSON\b|JSON\(\))/.test(ln) && !/JSONB/.test(ln))
) {
  issues.push("✗ json column — use jsonb (postgresql.JSONB). §6.2");
}
if (/sa\.DateTime\(\)/.test(src)) {
  issues.push("✗ DateTime() without timezone=True — use sa.DateTime(timezone=True). §6.2");
}
if (/default=uuid\.uuid4|default=uuid4/.test(src)) {
  issues.push("⚠ Python-side UUID default — prefer server_default=sa.text('gen_random_uuid()'). §6.2");
}

if (issues.length) {
  process.stderr.write(
    [
      `⚠ migration-check: §6.2 convention issues in ${fp}:`,
      ...issues.map((s) => "  " + s),
      "  See .claude/skills/migration/SKILL.md.",
    ].join("\n") + "\n",
  );
  process.exit(2);
}
allow();
