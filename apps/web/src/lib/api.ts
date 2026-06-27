/**
 * Server-side API client for the FastAPI backend.
 *
 * Resolves the Clerk session JWT via `auth().getToken()` and forwards it
 * as `Authorization: Bearer <jwt>`. The FastAPI `current_user` dependency
 * verifies via JWKS and JIT-provisions an Organization + User row when the
 * webhook hasn't synced yet, so first-time requests succeed without a manual
 * onboarding step.
 *
 * Returns the parsed JSON body when the HTTP status is 2xx; throws
 * `ApiError` with the raw response otherwise so server components can
 * branch on `.status` (404 → cross-tenant or unknown client, 401 →
 * auth issue, 5xx → backend fault).
 */
import { auth } from "@clerk/nextjs/server";

const _DEFAULT_BASE = "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown) {
    super(`API error ${status}`);
    this.status = status;
    this.body = body;
  }
}

function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? _DEFAULT_BASE;
}

async function authHeaders(): Promise<HeadersInit> {
  const { getToken } = await auth();
  const token = await getToken();
  if (!token) {
    throw new ApiError(401, { message: "No Clerk session token" });
  }
  return { Authorization: `Bearer ${token}` };
}

export async function getJson<T>(path: string): Promise<T> {
  const headers = await authHeaders();
  const res = await fetch(`${apiBase()}${path}`, {
    headers,
    // Pacing data updates after CSV uploads; never serve stale.
    cache: "no-store",
  });
  let body: unknown;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  if (!res.ok) {
    throw new ApiError(res.status, body);
  }
  return body as T;
}
