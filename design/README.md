# StudyGuard AI — Design System & UI Kit

A production-grade design system for the AI Study Coach. Single source of truth:
`tokens/tokens.json` → exported to CSS, Tailwind, Flutter, Material.

## Index
- **Foundations:** [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) · [tokens/](tokens/) · [BRAND.md](BRAND.md)
- **Components:** [COMPONENTS.md](COMPONENTS.md) · [MOTION.md](MOTION.md) · [STATES.md](STATES.md)
- **Screens:** [Desktop](SCREENS_DESKTOP.md) · [Web](SCREENS_WEB.md) · [Mobile](SCREENS_MOBILE.md)
- **Structure:** [IA_NAVIGATION.md](IA_NAVIGATION.md) · [HIERARCHIES.md](HIERARCHIES.md) · [FIGMA_SPEC.md](FIGMA_SPEC.md)
- **Reports/A11y:** [REPORT_LAYOUTS.md](REPORT_LAYOUTS.md) · [ACCESSIBILITY.md](ACCESSIBILITY.md)
- **Review:** [REVIEW.md](REVIEW.md)
- **Assets:** [assets/logo.svg](assets/logo.svg) · [assets/logomark.svg](assets/logomark.svg) · [assets/favicon.svg](assets/favicon.svg)

## Tokens → code
| Export | File | Consumed by |
| --- | --- | --- |
| CSS variables | `tokens/tokens.css` | website, desktop SPA, web dashboard |
| Tailwind | `tokens/tailwind.theme.js` | future Next.js web |
| Flutter | `tokens/flutter_theme.dart` | mobile app |
| Material 3 | `tokens/material_theme.json` | mobile / theming tools |
| Figma | import `tokens.json` via Tokens Studio | Figma library |

## Status legend
- ✅ **Fully designed** — spec complete (and, where noted, applied in shipping UI).
- ⚠ **Needs implementation** — designed; not yet built on that platform.
- ❌ **Future roadmap** — e.g., Flutter mobile app, mascot, Account.

## Applied in code today
`tokens/tokens.css` is imported by `website/`, `desktop/frontend/`, and the web
dashboard styling, so the shipping UIs already use this palette/typography.
