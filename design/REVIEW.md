# Design Review (multi-team) & Iterations

Reviewed as Apple HIG, Google Material, Microsoft Fluent, Linear, and hackathon
judges. Each iteration fixed real issues.

## Iteration 1 — findings
- **Apple HIG:** camera felt central → implied surveillance. **Fix:** camera is a
  small collapsible PiP with an explicit "processed on device" privacy dot; hero
  is the Study Score + coach.
- **Linear:** too many primary actions per view. **Fix:** one primary per screen;
  Cmd-K for everything else.
- **Material:** color-only status. **Fix:** icon + label on every status/severity.
- **Fluent:** dense settings. **Fix:** grouped settings + sub-nav + search.

## Iteration 2 — findings
- **Judges:** "what is this in 5 seconds?" **Fix:** landing hero + one-line value,
  Demo Mode so it runs with no webcam.
- **A11y:** focus rings weak, motion heavy. **Fix:** 3:1 focus ring token,
  reduced-motion + high-contrast media queries in `tokens.css`.
- **UX Research:** onboarding too long. **Fix:** 3 steps, skippable, ≤3 decisions.

## Iteration 3 — findings
- **Coach clarity:** tips felt like guesses. **Fix:** every coach card shows
  evidence + confidence pill (ties to real backend).
- **Charts:** legend overload. **Fix:** direct labels, max 2 series, data-table
  fallback for SR.
- **Empty states:** blank screens. **Fix:** specified empty/loading/error for
  every surface (STATES.md).

## Residual (tracked, not blocking)
- PDF renderer, icon SVG set, Flutter build, Figma .fig file, per-platform a11y
  audits. All listed with status in the design docs.

## Verdict
Commercially-polished **specification** with tokens applied to the shipping web/
desktop UIs. Remaining work is implementation, clearly labeled.
