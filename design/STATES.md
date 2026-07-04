# States: Empty, Loading, Error, Success, Failure

Every data surface must define all five. Never show a blank screen.

## Empty states (first-run / no data)
- Friendly line illustration + one-line explanation + single primary action.
- Dashboard: "No sessions yet — start your first study session" + Start / Try Demo.
- Analytics: "Not enough data for trends yet" + "Study 3 days to unlock trends."
- Coach: "Your coach is warming up" + Start session / Demo.
- Achievements: locked cards visible (aspirational), progress hints.

## Loading
- **Skeletons** matching final layout (cards/rows/rings), shimmer 1.2s.
- Charts: skeleton axes + shimmering plot area. Never a bare spinner for content.
- Inline button loading: spinner + disabled + preserved width.

## Error
- Non-blocking banner or card with icon + plain cause + recovery action + link to
  Troubleshooting. Never raw stack traces to users.
- Camera error: "Camera unavailable" + Retry / Use Demo Mode / Help.
- Data/API error: "Could not load analytics" + Retry; keep last-good data if any.

## Success
- Snackbar (polite) + subtle checkmark; score/goal updates animate in place.
- Session saved: "Session saved · Focus 82" with View summary action.

## Failure (destructive/critical)
- Modal for data loss risk (e.g., delete data): confirm + consequence text.
- Gentle shake on invalid input + inline error tied via aria-describedby.

Status: ✅ fully specified for all surfaces · ⚠ implement per platform.
