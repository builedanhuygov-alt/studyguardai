# Report Layouts (PDF, Weekly Report, Coach Cards, Presentation/Demo)

## PDF export layout (A4/Letter, print-safe)
- **Cover band:** logo mark + "Weekly Study Report" (serif) + date range + name.
- **Summary strip:** Study Score, total hours, streak, consistency (4 KPIs).
- **What happened:** narrative paragraph (from coach weekly summary).
- **Charts:** focus trend (line) + weekday heatmap (grayscale-safe).
- **Why (correlations, not causes):** inference with confidence.
- **Suggestions:** 3 bullets. **Confidence** footer + "metrics only, no video."
- Print rules: 12pt body, 24pt title, 1.5 line-height, black on white, charts use
  patterns + labels (no color reliance), page number + generated timestamp.

## Weekly Report (in-app)
Same content as PDF, interactive: audience selector (Student/Parent/Teacher/
Self), period toggle, Download PDF. Serif title, sectioned cards.

## AI Coach cards
- Violet left accent (4px), sparkle icon, title (semibold), message (base),
  evidence line (muted, sm), confidence pill (low grey / med amber / high green),
  optional actions. Max width 560px for readability. Grouped under "Today" (≤3).

## Presentation Mode UI
Full-screen, dark, large serif headings, one insight per scene, auto-advance
(6s), progress dots, brand gradient accents, big animated numbers. Space=next,
Esc=exit. Seed data; no camera; "Demo data" watermark bottom-left.

## Demo Mode UI
Standard app chrome + persistent "Demo data — using sample sessions" chip in the
top bar with a "Use my camera" CTA. Identical layouts to live, seed-backed.

Status: ✅ layouts specified; in-app weekly report + markdown export implemented
(`studyguard/reports`) · ⚠ PDF renderer (reportlab/pandoc) is an implementation step.
