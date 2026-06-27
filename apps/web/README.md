# apps/web — MixSight authenticated app

Next.js 16, App Router, TypeScript strict, Tailwind 4, **Clerk Elements** (custom sign-in/sign-up per ADR-004). Deploys to `app.mixsight.ai` (Phase 1c).

## Dev

From repo root:
```sh
make web
```

Or directly:
```sh
cd apps/web
pnpm dev   # http://localhost:3000
```

The dev/build/start scripts load env vars from the repo-root `.env` via `dotenv-cli`, so there is no separate `apps/web/.env.local`. Single source of truth per ADR-004.

## Routes

- `/sign-in/[[...sign-in]]` — Clerk Elements custom sign-in (matches `apps/site` brand)
- `/sign-up/[[...sign-up]]` — Clerk Elements custom sign-up
- `/` — authenticated landing (placeholder; pacing surfaces land Phase 1a Week 3 per §7.3)

## Auth flow

`src/middleware.ts` runs `clerkMiddleware`. Every route except `/sign-in/*` and `/sign-up/*` is gated by `auth.protect()` — unauthenticated traffic is bounced to `/sign-in`.

The FastAPI side (`apps/api`) verifies Clerk JWTs against Clerk JWKS (Day 4, Task #5). The webhook handler (`organizationMembership.*`, `user.*`) syncs `User` + `UserClientAccess` rows (Day 4, alongside the JWT middleware).

## Brand

Matches `apps/site` exactly:
- Navy `#0f1e3d`, Teal `#0d9488`, Inter font via `next/font/google`
- The sign-in/sign-up cards mirror the `PasswordGate` aesthetic from the pitch page
