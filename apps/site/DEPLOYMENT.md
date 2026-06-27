# Deploying mixsight.ai

A practical first-time deployment guide for the marketing site (this directory). The site is a Next.js static export — pure HTML / CSS / JS in `apps/site/out/` after build. That means almost any host works.

---

## TL;DR — recommended path

**Cloudflare Pages, with direct upload via the dashboard.** Free forever at your traffic level, instant SSL, your domain is already at Cloudflare so DNS is one click.

Estimated time end-to-end: **~20 minutes**, including domain DNS.

---

## Cost comparison (free tiers, May 2026)

| Provider | Free tier | Bandwidth cap | Build minutes | Custom domain | Why pick it |
|---|---|---|---|---|---|
| **Cloudflare Pages** | Forever-free | **Unlimited** | 500 builds/month | Free + your DNS lives here | Best cost long-term, native to your stack |
| **Vercel** | Hobby tier | 100GB/month | 6000 minutes/month | Free | Made by the Next.js team, best DX |
| **Netlify** | Free tier | 100GB/month | 300 minutes/month | Free | Solid alternative, simple UI |
| AWS S3 + CloudFront | Pay-per-use (~pennies) | Pennies/GB after free tier | — | Free | Cheapest at scale, complex setup |
| GitHub Pages | Free with public repo | Soft 100GB/month | Limited builds | Free | Skip — needs public repo or paid tier |

**For your stage (pre-launch, low traffic):** all three top options cost $0. Pick Cloudflare Pages — it's free for you forever even at high traffic.

---

## Pre-flight checklist

Do this once, before any deployment.

### 1. Set up Web3Forms (so the contact form works)

1. Go to https://web3forms.com/.
2. In the form on their homepage, enter `hello@mixsight.ai` and click "Create Access Key".
3. They send an email — verify it.
4. Copy the access key shown on the success screen. It looks like `a1b2c3d4-e5f6-7890-abcd-ef1234567890`.

You'll paste this into the deployment platform's environment variables in a few minutes. **Don't put it in `.env.local` if you only plan to deploy** — that file is gitignored. The platform's UI is the source of truth.

### 2. Set up the four contact inboxes at mixsight.ai

Before launch (not blocking for deployment, but blocking for going live):

- `hello@mixsight.ai` — general / early access
- `privacy@mixsight.ai` — GDPR requests (referenced in privacy policy)
- `security@mixsight.ai` — security issues
- `legal@mixsight.ai` — terms questions

Cloudflare Email Routing is free and easy if you already have the domain at Cloudflare:
1. Cloudflare dashboard → mixsight.ai → **Email** → **Email Routing**.
2. Enable Email Routing (adds the MX records automatically).
3. Add destination addresses (your personal email) and verify them.
4. Create catch-all rule: forward `*@mixsight.ai` → your personal email. Or create per-prefix rules for the four addresses above.

### 3. Build the site locally — verify it works

```powershell
cd "E:\Projects\Vibe Engineered\mixsight\apps\site"
npm run build
```

Confirm the build outputs to `apps/site/out/`. You should see `index.html`, `pricing/`, `privacy/`, `terms/`, `contact/`, and a `_next/` folder. If anything fails, fix it before deploying.

---

## Option A — Cloudflare Pages (recommended)

### A.1 — Direct upload (simplest path, no git required)

This is the easiest first-time path. You'll drag your `out/` folder into the dashboard.

1. **Log into the Cloudflare dashboard** at https://dash.cloudflare.com.
2. In the sidebar: **Workers & Pages** → **Create** → **Pages** → **Upload assets**.
3. **Project name:** `mixsight-site` (this becomes `mixsight-site.pages.dev`). Click **Create project**.
4. **Drag the `apps/site/out/` folder** onto the upload zone. Wait for upload to finish (a minute or two depending on connection).
5. Click **Deploy site**. You'll get a URL like `https://mixsight-site.pages.dev`. Confirm it loads correctly.

You now have a working preview. Custom domain comes next.

### A.2 — Connect mixsight.ai (custom domain)

1. In the Cloudflare Pages project → **Custom domains** → **Set up a custom domain**.
2. Enter `mixsight.ai` (the apex). Click **Continue**.
3. Cloudflare auto-detects your existing DNS zone (because the domain is registered with them) and offers to add the right CNAME record. Click **Activate domain**.
4. Repeat for `www.mixsight.ai` if you want both to work.
5. SSL provisions automatically within a minute.

Test by visiting `https://mixsight.ai`. If you set up `www`, both should resolve.

### A.3 — Set the Web3Forms environment variable

The contact form needs `NEXT_PUBLIC_WEB3FORMS_KEY` baked into the build.

1. In the Cloudflare Pages project → **Settings** → **Variables and Secrets** → **Add variable**.
2. **Variable name:** `NEXT_PUBLIC_WEB3FORMS_KEY`
3. **Value:** paste the access key from Web3Forms.
4. **Environment:** Production (and Preview, if you want preview builds to work).
5. Click **Save**.

For this to take effect, you need to rebuild + redeploy. Direct-upload deployments don't pick up env vars automatically — see A.4 for the git-integrated path which does, or A.5 to redeploy manually.

### A.4 — Git integration (optional, recommended for ongoing work)

Once direct upload is working, switch to git integration so updates deploy automatically.

1. Initialize git at the **monorepo root** if you haven't already:
   ```powershell
   cd "E:\Projects\Vibe Engineered\mixsight"
   git init
   git add .
   git commit -m "Initial commit"
   ```
2. Create a private repo on GitHub (or GitLab/Bitbucket — Cloudflare supports all three). Push:
   ```powershell
   git remote add origin git@github.com:YOUR_USER/mixsight.git
   git branch -M main
   git push -u origin main
   ```
3. Cloudflare Pages dashboard → your project → **Settings** → **Builds** → **Configure source** → connect to GitHub → select the repo.
4. **Production branch:** `main`
5. **Build configuration:**
   - **Framework preset:** Next.js (Static HTML Export)
   - **Build command:** `npm run build`
   - **Build output directory:** `out`
   - **Root directory (advanced):** `apps/site`
   - **Node.js version:** set environment variable `NODE_VERSION=22` (or whatever Node version you're using locally — check with `node --version`)
6. Click **Save and Deploy**.

Now every push to `main` triggers a build. Branches and PRs get preview URLs automatically.

### A.5 — Redeploying after env var changes (direct-upload path)

If you're using direct upload and updated `NEXT_PUBLIC_WEB3FORMS_KEY`:

```powershell
cd "E:\Projects\Vibe Engineered\mixsight\apps\site"
# Create a one-off .env.local for the build only (don't commit it)
"NEXT_PUBLIC_WEB3FORMS_KEY=your_actual_key_here" | Out-File -FilePath .env.local -Encoding utf8 -NoNewline
npm run build
# Re-upload via the dashboard, or use Wrangler CLI:
npx wrangler pages deploy out --project-name=mixsight-site
```

---

## Option B — Vercel

Use this if you prefer the Next.js-native experience or want preview deployments on every PR for free.

### B.1 — Set up

1. Go to https://vercel.com and sign in with GitHub.
2. **Add New** → **Project**.
3. Import the repo (create one first if needed — see A.4 step 1).
4. **Root directory:** `apps/site`
5. **Framework preset:** Next.js (auto-detected).
6. **Build command** and **Output directory:** Vercel autodetects them. Leave defaults.
7. **Environment variables:** add `NEXT_PUBLIC_WEB3FORMS_KEY` with your Web3Forms key.
8. Click **Deploy**.

You get `mixsight-site.vercel.app` (or similar). Confirm it works.

### B.2 — Connect mixsight.ai

1. Vercel project → **Settings** → **Domains** → add `mixsight.ai` and `www.mixsight.ai`.
2. Vercel will give you a CNAME record (something like `cname.vercel-dns.com`).
3. Go to Cloudflare dashboard → mixsight.ai → **DNS** → **Records**.
4. Add a CNAME record:
   - Name: `@` (for the apex) or `www`
   - Target: `cname.vercel-dns.com`
   - Proxy status: **DNS only** (the orange cloud OFF — important; Vercel needs to see the request)
5. Verify in Vercel. SSL provisions in a few seconds.

> Trade-off vs Cloudflare Pages: you lose Cloudflare's CDN/WAF on this domain because you're proxying through Vercel directly. For a marketing site, this is fine.

---

## Option C — Netlify

Briefly: works the same as Vercel.

1. Sign in at https://netlify.com.
2. **Add new site** → **Import an existing project** → connect to GitHub.
3. Pick the repo. **Base directory:** `apps/site`. **Build command:** `npm run build`. **Publish directory:** `apps/site/out`.
4. **Environment variables:** `NEXT_PUBLIC_WEB3FORMS_KEY` = your key.
5. Click **Deploy site**.
6. Add `mixsight.ai` under **Domain management**. Netlify gives you a CNAME target to add at Cloudflare (same as Vercel — proxy off).

---

## DNS configuration at Cloudflare

For all options, you need DNS records pointing your domain at the host.

### If you went with Cloudflare Pages (Option A)

DNS is automatic — Cloudflare added the CNAME records for you in step A.2. Verify them:

1. Cloudflare dashboard → mixsight.ai → **DNS** → **Records**.
2. You should see a `CNAME` record for `mixsight.ai` (or `@`) pointing to `mixsight-site.pages.dev`, proxied (orange cloud ON).
3. Same for `www` if you set it up.

### If you went with Vercel or Netlify (Options B / C)

Add the CNAME they give you, with proxy **OFF** (DNS only — the host needs unproxied access).

### Email records — keep these intact

Don't delete the MX records that Email Routing added in pre-flight step 2. They handle `hello@`, `privacy@`, etc.

---

## Post-deployment verification

Once your site is live at `mixsight.ai`, walk through this checklist:

1. **HTTPS works.** `https://mixsight.ai` shows a valid cert. Browser doesn't warn.
2. **All routes load:**
   - `/` → landing page with hero
   - `/pricing/` → 4-tier table
   - `/contact/` → form
   - `/privacy/` → privacy policy
   - `/terms/` → terms
3. **Logo renders** in the header and footer.
4. **Contact form submission works.**
   - Fill out the form on `/contact/`.
   - Submit. You should see the "Message sent — thank you" success screen (not the "Email client opened" fallback — that means your Web3Forms key wasn't set or didn't apply).
   - Check `hello@mixsight.ai`. The submission should arrive within a minute or two. If not, check the Web3Forms dashboard.
5. **Topic pre-fill works.** Visit `https://mixsight.ai/contact/?topic=design-partner` — the inquiry-type dropdown should default to "Design partner inquiry".
6. **Mobile renders.** Open on phone or DevTools mobile view. Nav, hero, tables, form all readable.
7. **Lighthouse score** (optional). Open `mixsight.ai` in Chrome → DevTools → Lighthouse → Run report. You should see 95+ across the board on a static site.

---

## Updating the site

### If you went with git integration

```powershell
cd "E:\Projects\Vibe Engineered\mixsight"
git add .
git commit -m "Update pricing copy"
git push
```

The platform automatically builds and deploys on push.

### If you're using direct upload (Cloudflare Pages, no git)

```powershell
cd "E:\Projects\Vibe Engineered\mixsight\apps\site"
npm run build
npx wrangler pages deploy out --project-name=mixsight-site
```

Or repeat the manual drag-and-drop in the Cloudflare dashboard.

---

## Filing the platform API approvals

Once mixsight.ai is live and the privacy policy URL is accessible at `https://mixsight.ai/privacy/`, you can submit the API approval applications referenced in SCOPE.md §5:

- **Meta Marketing API** — Meta Business Verification + Advanced Access. Approval window 1–3 weeks.
- **Google Ads API** — Developer token. 1–2 weeks for Basic Access.
- **TikTok Marketing API** — Business app review. 1–2 weeks.

The privacy policy specifically references the Google API Services User Data Policy (Limited Use) and Meta Platform Terms in §9 — both reviewers look for that language. You're set on the policy side.

---

## Future — app.mixsight.ai (the actual app)

The marketing site is **not** the app. The app lives at `apps/web/` (frontend, Next.js with auth) and `apps/api/` (FastAPI backend) and will deploy to `app.mixsight.ai` later in Phase 1a.

The app is a stateful application with a Postgres database, so the deployment story is different:
- **Frontend (`apps/web/`):** Vercel or Cloudflare Pages (it's still Next.js, but with Clerk auth and live API calls).
- **Backend (`apps/api/`):** Fly.io, Railway, or Render. These run FastAPI + Postgres + Redis. Expect ~$5–25/month at the start.

Don't worry about this yet — it's Week 2+ of Phase 1a per `CURRENT_PHASE.md`. The marketing site is standalone and stays standalone.

---

## Troubleshooting

**Build fails on Cloudflare Pages with "Cannot find module ..."**
Likely the **Root directory** wasn't set to `apps/site`. Check Settings → Builds.

**Contact form shows "Email client opened" instead of "Message sent"**
`NEXT_PUBLIC_WEB3FORMS_KEY` wasn't set at build time. Set it in the platform's environment variables and trigger a redeploy.

**SSL cert won't provision**
Wait 5–10 minutes. If still failing, check the DNS proxy setting. For Cloudflare Pages: proxy ON. For Vercel/Netlify: proxy OFF.

**Domain shows "DNS_PROBE_FINISHED_NXDOMAIN"**
DNS hasn't propagated yet. Wait 5 minutes, hard refresh. Use https://dnschecker.org to confirm the records are visible globally.

**`npm run build` works locally but fails in CI**
Check that your local `node --version` matches the platform's. Set `NODE_VERSION=22` (or your local) as an env var in the platform.

**Form submissions aren't arriving at hello@mixsight.ai**
1. Check the Web3Forms dashboard — they log all received submissions.
2. Confirm Cloudflare Email Routing is set up and `hello@mixsight.ai` actually forwards to your real inbox (send a test email).
3. Check spam folder.
