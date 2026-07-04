# Figma-Ready Specification

How to rebuild this system in Figma 1:1. Uses Figma Variables + Auto Layout.

## File & page structure
```
StudyGuard AI (file)
├─ 0. Cover
├─ 1. Foundations (color, type, spacing, radius, shadow, motion)
├─ 2. Components (buttons, cards, charts, nav, coach, ...)
├─ 3. Patterns (empty/loading/error/success)
├─ 4. Desktop (all screens)
├─ 5. Web (all screens)
├─ 6. Mobile (all screens)
└─ 7. Prototypes (flows)
```

## Variables (map to tokens.json)
- Collections: `color` (modes: Light, Dark, HighContrast), `space`, `radius`,
  `type`, `motion`.
- Example: `color/brand/600 = #4F46E5`; bind component fills to variables so mode
  switch = theme switch. Numeric tokens as Number variables (space/radius).

## Naming conventions
- Components: `Category/Name/Variant` e.g. `Button/Primary/md`, `Card/Coach`,
  `Chart/Line`. Props: `size`, `state`, `tone`, `icon?`.
- Frames (screens): `Platform / Section / Screen` e.g. `Desktop / Core / Dashboard`.
- Layers: PascalCase, no "Frame 123". Icons: `icon/name` at 24.

## Auto Layout & constraints
- Cards: vertical Auto Layout, padding 16–20, gap 12, fill container width,
  hug height. Nav rail: vertical, fixed width, top-aligned.
- Grids: 12-col (web) / 8-col (tablet) / 4-col (mobile), 24 gutter, 24 margin.
- Constraints: content Left+Right; right rail Right+Top; top bar Top+L+R.
- Text: fixed width, hug height; use max-width for reading columns.

## Component variants matrix
Button: {size: sm|md|lg} x {tone: primary|secondary|ghost|danger|coach} x
{state: default|hover|active|focus|disabled|loading}. Cards: {type} x {elevation}.
Charts: {type} x {theme}. All states as variants (not detached copies).

## Prototyping
Smart Animate for score ring + page transitions (base 220ms, standard easing).
Overlays for command palette + dialogs. Flow starts per `IA_NAVIGATION.md`.

Status: ✅ complete spec to author the Figma library · ⚠ the .fig file itself is
built in Figma (tokens JSON importable via Tokens Studio plugin).
