#!/usr/bin/env node
// Generate SHA-256 hash of `username:password` for NEXT_PUBLIC_PITCH_PASSWORD_HASH.
// Usage: node scripts/generate-pitch-hash.mjs <username> <password>

const [, , username, password] = process.argv;

if (!username || !password) {
  console.error("Usage: node scripts/generate-pitch-hash.mjs <username> <password>");
  process.exit(1);
}

const input = `${username.trim()}:${password}`;
const buf = new TextEncoder().encode(input);
const digest = await crypto.subtle.digest("SHA-256", buf);
const hex = Array.from(new Uint8Array(digest))
  .map((b) => b.toString(16).padStart(2, "0"))
  .join("");

console.log(hex);
console.error(`\nSet NEXT_PUBLIC_PITCH_PASSWORD_HASH=${hex} in apps/site/.env.local`);
