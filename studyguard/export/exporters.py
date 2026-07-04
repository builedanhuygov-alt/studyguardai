"""Built-in exporters: JSON, CSV, Markdown (standard library only)."""
from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping

from studyguard.export.base import register_exporter


@register_exporter("json")
class JsonExporter:
    """Pretty-printed JSON of the whole payload."""

    format = "json"

    def export(self, payload: Mapping[str, object]) -> str:
        return json.dumps(payload, indent=2, default=str, ensure_ascii=False)


@register_exporter("csv")
class CsvExporter:
    """CSV of the per-day rows under ``payload['days']`` (empty-safe)."""

    format = "csv"

    def export(self, payload: Mapping[str, object]) -> str:
        days = payload.get("days") or []
        buffer = io.StringIO()
        fieldnames = list(days[0].keys()) if days else ["date", "study_minutes", "avg_focus", "avg_posture"]
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for row in days:
            writer.writerow(row)
        return buffer.getvalue()


@register_exporter("markdown")
class MarkdownExporter:
    """Markdown summary. Uses ``payload['markdown']`` when present."""

    format = "markdown"

    def export(self, payload: Mapping[str, object]) -> str:
        if isinstance(payload.get("markdown"), str):
            return str(payload["markdown"])
        lines = ["# StudyGuard export", ""]
        streak = payload.get("streak")
        if streak is not None:
            lines.append(f"- Streak: {streak} day(s)")
        days = payload.get("days") or []
        if days:
            lines.append("")
            lines.append("| Date | Minutes | Focus | Posture |")
            lines.append("| --- | --- | --- | --- |")
            for row in days:
                lines.append(
                    f"| {row.get('date', '')} | {row.get('study_minutes', '')} "
                    f"| {row.get('avg_focus', '')} | {row.get('avg_posture', '')} |"
                )
        return "\n".join(lines).strip() + "\n"
