// week-end-gate.mjs — Block marking a week "complete" in CURRENT_PHASE.md
// until the /week-end gates have actually run. Prevents the Week-3 situation:
// a week flipped to complete with the code review + refactor deferred, letting
// bugs and un-refactored code roll into the next week.
//
// Wired as a PreToolUse hook on Edit|Write|MultiEdit (see .claude/settings.json).
// Triggers ONLY when an edit newly sets a `WEEK: <n> (complete` line in
// CURRENT_PHASE.md. Written in node (not python) because python3 isn't on the
// hook PATH on this machine; node always is.
//
// Exit 2 = block (message on stderr, surfaced to Claude). Exit 0 = allow.
// Fails OPEN on any parse error — a hook bug must never block real work.

import fs from "node:fs";

function allow() {
  process.exit(0);
}

let data;
try {
  data = JSON.parse(fs.readFileSync(0, "utf8"));
} catch {
  allow();
}

const ti = (data && data.tool_input) || {};
const filePath = ti.file_path || "";
if (!/CURRENT_PHASE\.md$/.test(filePath)) allow();

// Collect the proposed new text across Edit (new_string), Write (content),
// and MultiEdit (edits[].new_string).
const parts = [];
if (ti.new_string) parts.push(ti.new_string);
if (ti.content) parts.push(ti.content);
if (Array.isArray(ti.edits)) {
  for (const e of ti.edits) if (e && e.new_string) parts.push(e.new_string);
}
const newText = parts.join("\n");
if (!newText) allow();

const completePat = /WEEK:\s*(\d+)\s*\(complete/g;
const newWeeks = new Set([...newText.matchAll(completePat)].map((m) => m[1]));
if (newWeeks.size === 0) allow();

let disk = "";
try {
  disk = fs.readFileSync("CURRENT_PHASE.md", "utf8");
} catch {
  allow();
}
const diskWeeks = new Set([...disk.matchAll(completePat)].map((m) => m[1]));

// Weeks this edit *newly* marks complete (not already complete on disk).
const newlyCompleted = [...newWeeks].filter((w) => !diskWeeks.has(w));
if (newlyCompleted.length === 0) allow();

let sentinel = "";
try {
  sentinel = fs.readFileSync(".claude/.week-end-pass", "utf8");
} catch {
  /* missing sentinel → gate 1 fails below */
}
let shipped = "";
try {
  shipped = fs.readFileSync("SHIPPED.md", "utf8");
} catch {
  /* missing SHIPPED → gate 2 fails below */
}

const blocked = [];
for (const w of newlyCompleted) {
  const gateBarOk = new RegExp(`^WEEK=${w}$`, "m").test(sentinel);
  const gateLedgerOk =
    new RegExp(`week\\s+${w}\\b`, "i").test(shipped) && shipped.includes("/code-review");
  if (!gateBarOk || !gateLedgerOk) blocked.push(w);
}
if (blocked.length === 0) allow();

const lines = [
  `✗ week-end-gate: refusing to mark week(s) ${blocked.join(", ")} complete — gates not satisfied.`,
  "",
  "Per .claude/commands/week-end.md, a week is NOT complete until ALL gates pass:",
  "  1. Mechanical bar: run  bash scripts/week_end_gate.sh <week>  (must PASS;",
  "     writes .claude/.week-end-pass). Needs Postgres up (make up).",
  "  2. /code-review --effort high — findings fixed or deferred-with-reason.",
  "  3. /simplify on the week's diff — refactor applied or deferred-with-reason.",
  "  4. Every new feature (endpoint / mutation / surface / algorithm) names its",
  "     contract test (tenancy cross-tenant, audit, happy path, key edges).",
  "  5. SHIPPED.md updated with the Week <week> close-ritual record (incl. the",
  "     /code-review run).",
  "",
  "Complete the gates, then re-apply this CURRENT_PHASE.md edit.",
];
process.stderr.write(lines.join("\n") + "\n");
process.exit(2);
