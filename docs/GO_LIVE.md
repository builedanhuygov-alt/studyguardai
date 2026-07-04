# Go Live — get a real public URL

**Honest note:** I (the AI assistant) cannot expose a public URL from my sandbox
— it has no port-forwarding/hosting tool, and my GitHub access here is
read-only (search/browse only, no push). Everything below is pre-configured so
*you* can go live in minutes with zero build steps.

## Option A — Static marketing site (fastest, ~1 minute)
The `website/` folder is plain HTML/CSS/JS (no build step).

**GitHub Pages (uses your existing repo)**
1. Push this repo to GitHub (already done in earlier sessions).
2. Repo → Settings → Pages → Source: **GitHub Actions**.
3. Push to `main` (or run the workflow manually) — `.github/workflows/pages.yml`
   deploys `website/` automatically.
4. Your site is live at `https://<your-username>.github.io/studyguard-ai/`.

**Netlify Drop (no account changes, no git needed)**
- Go to https://app.netlify.com/drop and drag the `website/` folder in. Live in
  seconds. (`netlify.toml` is already configured if you use `netlify deploy` instead.)

**Vercel**
```bash
npx vercel --prod
```
`vercel.json` already points the output directory at `website/`.

## Option B — Full interactive product online (API + data)
To let people use the **real dashboard/API** (not just the marketing page):

**Render (Blueprint, zero config)**
1. https://dashboard.render.com/blueprints → New Blueprint → connect this repo.
2. Render reads `render.yaml` and deploys the FastAPI service from
   `deploy/Dockerfile.api` automatically — you get a URL like
   `https://studyguard-api.onrender.com` with Swagger at `/docs`.

**Railway**
```bash
railway up            # from the repo root; Railway auto-detects deploy/Dockerfile.api
```

> The hosted API serves the **demo (seed) service** by default (`studyguard.demo`),
> so visitors see a fully populated dashboard without needing a webcam — safe to
> make public. Wire a real per-user backend before accepting real webcam data
> from strangers (see `docs/COMMERCIAL_ARCHITECTURE.md`).

## What's already verified locally (this session)
- `website/` served + screenshotted (light & dark, desktop & mobile) — renders
  correctly, no console errors.
- `desktop/frontend/` SPA served + verified via Chromium DOM dump: KPIs,
  Focus/Energy/Burnout rings, sparkline, and AI Coach card all render with real
  numbers (using the built-in demo-data fallback when no backend is present).
- A real bug (misplaced file from a relative-path write) was caught and fixed
  during this verification — see `CHANGELOG.md`.

Status: ✅ deploy configs generated · ⚠ you must click "connect repo" / drag the
folder once — that step requires your account, not mine · ❌ not deployed by me.
