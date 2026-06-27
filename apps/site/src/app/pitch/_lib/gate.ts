// Client-side password gate helper.
// Hashes `${username}:${password}` with SHA-256 and compares against
// NEXT_PUBLIC_PITCH_PASSWORD_HASH (build-time inlined).
// Not cryptographic security — combined with robots.txt + noindex + no
// inbound links, it keeps the pitch URL out of public reach.

export async function hashCredentials(username: string, password: string): Promise<string> {
  const input = `${username.trim()}:${password}`;
  const buf = new TextEncoder().encode(input);
  const digest = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function getExpectedHash(): string {
  return (process.env.NEXT_PUBLIC_PITCH_PASSWORD_HASH ?? "").toLowerCase();
}

export const SESSION_KEY = "pitch.authed.v1";
