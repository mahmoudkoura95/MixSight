# Marketing site (apps/site)

Static Next.js 16 export deployed to **mixsight.ai**. **Not the app** — the app is `apps/web/` → app.mixsight.ai.

## Purpose

Pre-Phase-1a infrastructure supporting SCOPE.md §5 pre-build dependencies:
- Meta, Google, TikTok API approvals require a live privacy policy URL.
- Design partner outreach (§5.7) needs a credible public web presence.

This site is **outside the pnpm workspace** (see `pnpm-workspace.yaml` `!apps/site` exclusion). Managed by `npm` directly. See DECISIONS.md for why.

## Stack

- Next.js 16.2.6 (App Router, static export via `output: "export"`)
- React 19
- Tailwind CSS 4 (with `@theme inline` design tokens in `globals.css`)
- TypeScript strict
- lucide-react for icons
- Inter font via `next/font/google`

## Routes

- `/` — Landing page
- `/pricing/` — Tier table from SCOPE.md §4
- `/contact/` — Contact form (`ContactForm` Client Component, posts to Web3Forms or mailto fallback)
- `/privacy/` — Privacy policy (Meta Platform Terms + Google API Services User Data Policy references)
- `/terms/` — Terms of service
- `/pitch/` — **Private** design-partner pitch (noindex, gated, see "Pitch route" below)

## Pitch route (`/pitch/`)

A private, password-gated pitch page used to recruit the Phase 1a design partner (per SCOPE.md §5.7). Covers Phase 1 through Phase 4 with animated mockups. Not publicly linked; URL is shared out-of-band.

### Gate model

Client-side gate (the site is `output: "export"`, so middleware-based HTTP Basic Auth is unavailable). On submit, the form hashes `username:password` with SHA-256 and compares against `NEXT_PUBLIC_PITCH_PASSWORD_HASH` (build-time inlined). On success, sessionStorage flag is set and content renders.

Not cryptographic security. Defense-in-depth against discovery:
1. `public/robots.txt` `Disallow: /pitch/`
2. `metadata.robots = { index: false, follow: false }` on the route layout
3. No internal links anywhere on the site
4. URL shared only via email/DM

### Generating the password hash

```
cd apps/site
node scripts/generate-pitch-hash.mjs <username> <password>
```

Copy the hex digest into `NEXT_PUBLIC_PITCH_PASSWORD_HASH` in `apps/site/.env.local`. If unset, the gate rejects all attempts.

### Layout

- `src/app/pitch/page.tsx` — composes section components
- `src/app/pitch/layout.tsx` — sets noindex metadata, wraps in `<PasswordGate>`
- `src/app/pitch/_components/` — section + chrome + mockup components
- `src/app/pitch/_lib/content.ts` — all copy with `// §X.Y` SCOPE citations
- `src/app/pitch/_lib/mockData.ts` — fake "Lumen Studios" agency data
- `src/app/pitch/_lib/gate.ts` — hash check helper

Animations use the `motion` package (Framer Motion v11+ rename, React 19 compatible). All animations respect `prefers-reduced-motion`.

## Contact form

The `/contact/` form is wired to **Web3Forms** as the primary submission backend, with a **mailto: fallback** when no API key is configured.

**Setup:**
1. Visit https://web3forms.com/, enter `hello@mixsight.ai`, verify via the email they send.
2. Copy the access key.
3. `cp .env.local.example .env.local`
4. Paste the key into `NEXT_PUBLIC_WEB3FORMS_KEY=...`
5. Restart `npm run dev`.

**Behavior when no key is set:** the form opens the user's email client with a pre-filled subject and body. Works fine, but requires the visitor to have a desktop mail handler. Set the key before launching.

**CTA topic pre-fill:** every in-app CTA links to `/contact/?topic=<slug>` to pre-select the inquiry type. Supported slugs: `early-access`, `design-partner`, `pricing-starter`, `pricing-growth`, `pricing-agency`, `enterprise`, `general`.

`useSearchParams()` requires a Suspense boundary in Next.js 15+; the form is wrapped at the page level.

## Dev

```
cd apps/site
npm run dev       # http://localhost:3001
npm run build     # outputs to apps/site/out/
npm run lint
npm run typecheck
```

Deploy `out/` to Vercel, Cloudflare Pages, or any static host. Point mixsight.ai DNS at it.

## Brand

Logo at `public/logo.png`. Brand colors derived from the wordmark:
- Navy (`Mix` in logo): `#0f1e3d` (CSS var `--color-brand-navy`)
- Teal (`Sight` in logo): `#0d9488` (Tailwind `teal-600`, CSS var `--color-brand-teal`)

Accent throughout the UI uses `teal-600` for CTAs, `teal-50/100` for soft backgrounds.

## Content updates

- **Pricing**: edit the `tiers` array in `src/app/pricing/page.tsx`.
- **Privacy / Terms**: edit those pages directly. Update "Last updated" date.
- **Landing copy**: `src/app/page.tsx`. Feature list is in the `features` array.

## Contact inboxes referenced

Before launch, set these up at mixsight.ai:
- `hello@mixsight.ai` — early access, general
- `privacy@mixsight.ai` — GDPR/privacy requests (required by policy)
- `security@mixsight.ai` — security issues
- `legal@mixsight.ai` — terms questions

## Out of scope for this directory

- App features — those go in `apps/web/`.
- Server-side logic / API routes — static export only.
- Real auth flows — Clerk is `apps/web/` only. (The `/pitch/` gate is a client-side hash check, not cryptographic auth; see Pitch route above.)
- pnpm workspace integration — see DECISIONS.md ADR.
