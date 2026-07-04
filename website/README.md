# Marketing website

Static, dependency-free landing page (deployable to Vercel, Netlify, or GitHub
Pages as-is). SEO meta, JSON-LD, OpenGraph, skip-link, and prefers-color-scheme
dark/light are built in.

## Deploy
- **Vercel/Netlify:** point the project at `website/` (framework preset: Other).
- **GitHub Pages:** publish the `website/` folder.

## Next.js migration path (future)
The page is structured as sections (Home/Features/AI Coach/Analytics/Research/
Download/Docs/Blog). Porting to Next.js means one component per section + MDX for
Docs/Blog; no content rewrite needed.

Status: ✅ Generated (valid static HTML). ⚠ Online deploy not performed here.
