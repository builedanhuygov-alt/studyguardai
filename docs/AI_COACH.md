# AI Study Coach, Goals & Export

StudyGuard AI is a coach, not just an alerter. Every coaching message is
**explainable** and every number is derived from the learner's own data.

## Coach messages
`studyguard/coach/` turns analytics + raw metric points into `CoachMessage`s.
Each message carries:

| Field | Meaning |
| --- | --- |
| `title` / `message` | Human-readable coaching |
| `evidence` | The facts that justify it |
| `supporting_metrics` | The exact numbers behind it |
| `confidence` | low / medium / high (scales with data) |
| `category` | focus / posture / habit / wellbeing |

Examples produced today (data permitting):
- "You focused better than the previous study day (+20 points)." (evidence: today vs previous avg)
- "You tend to focus best in the evening." (evidence: highest avg focus by hour-of-day)
- "You're on a 3-day study streak."
- "Signs of study fatigue are building up; consider a rest day." (evidence: burnout risk)

The coach **never invents numbers** — if the data does not support a claim, the
message is not shown.

## Goals & gamification
`studyguard/goals/` computes, deterministically:
- **XP** (study minutes + focus), **Level**, and XP-to-next-level.
- **Study streak** and **consistency** (share of recent days studied).
- **Achievements**: first session, 3/7-day streaks, focus master, marathon.
- **Goal progress**: daily and weekly study-time targets.

## Export (Strategy + plugin)
`studyguard/export/` provides `json`, `csv`, and `markdown` exporters via a
registry. Add a format with `@register_exporter("fmt")` — no caller changes.
PDF export is a documented extension point (optional `reportlab` extra).

## API
The service exposes: `get_coach()`, `get_goals()`, `export(fmt, kind=...)`,
`export_formats()`. See `docs/API_HTTP.md`.

## Status (honest)
Coach/goals/export logic is implemented and covered by automated checks. The
*quality* of coaching advice (like burnout/recommendations) is an **Experiment**
until validated with real learners.
