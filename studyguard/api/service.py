"""Stable service API — the single entry point a frontend or HTTP layer uses.

Returns plain, JSON-serializable dicts (never internal objects) so the transport
(REST, CLI, notebook) is decoupled from the domain. Endpoint mapping is in
``docs/API_HTTP.md``.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import asdict

from studyguard.analytics.engine import daily_stats, metric_trend, study_streak
from studyguard.analytics.models import DailyStats, MetricPoint
from studyguard.analytics.planned import planned_vs_actual
from studyguard.coach.engine import coach_messages, focus_by_hour
from studyguard.coach.summary import weekly_summary
from studyguard.export import available_formats, create_exporter
from studyguard.goals.engine import compute_gamification, goal_progress
from studyguard.insight.engine import generate
from studyguard.reports.weekly import build_report, render_markdown
from studyguard.sources.base import (
    DataSource,
    available_source_keys,
    create_source,
    source_info,
)
from studyguard.sources.consent import ConsentStore, DataRights

logger = logging.getLogger(__name__)


class StudyGuardService:
    """Facade over sources, analytics, insights, and reports."""

    def __init__(
        self,
        *,
        db_path: str = "studyguard.db",
        consent: ConsentStore | None = None,
        sample_period_s: float = 1.0,
    ) -> None:
        self._db_path = db_path
        self._consent = consent or ConsentStore()
        self._sample_period_s = sample_period_s
        self._rights = DataRights(db_path)
        self._connected: dict[str, DataSource] = {}

    # -- consent ------------------------------------------------------------

    def grant_consent(self, key: str) -> dict:
        self._consent.grant(key)
        return {"source": key, "consent": True}

    def revoke_consent(self, key: str) -> dict:
        self._consent.revoke(key)
        if key in self._connected:
            self.disconnect_source(key)
        return {"source": key, "consent": False}

    # -- sources ------------------------------------------------------------

    def list_sources(self) -> list[dict]:
        """GET /sources — all registered sources with status."""
        result = []
        for key in available_source_keys():
            info = source_info(key)
            source = self._connected.get(key)
            health = source.health_check().status.value if source is not None else "disconnected"
            result.append(
                {
                    "key": info.key,
                    "title": info.title,
                    "category": info.category,
                    "requires_consent": info.requires_consent,
                    "consent": self._consent.has_consent(key),
                    "connected": key in self._connected,
                    "health": health,
                }
            )
        return result

    def connect_source(self, key: str, **config: object) -> dict:
        """POST /sources/{key} — connect after consent; idempotent."""
        self._consent.require(key)
        if key == "camera" and "db_path" not in config:
            config["db_path"] = self._db_path
        source = create_source(key, **config)
        if not source.validate():
            raise ValueError(f"Source {key!r} failed validation")
        source.connect()
        self._connected[key] = source
        return {"source": key, "connected": True, "health": source.health_check().status.value}

    def disconnect_source(self, key: str) -> dict:
        """DELETE /sources/{key} — disconnect and forget the instance."""
        source = self._connected.pop(key, None)
        if source is not None:
            source.disconnect()
        return {"source": key, "connected": False}

    # -- data ---------------------------------------------------------------

    def _metric_points(self) -> list[MetricPoint]:
        points: list[MetricPoint] = []
        for key, source in self._connected.items():
            try:
                points.extend(source.collect())
            except Exception:  # a failing source must not break the API
                logger.exception("Source %r failed to collect", key)
        return points

    def _daily(self) -> list[DailyStats]:
        return daily_stats(self._metric_points(), sample_period_s=self._sample_period_s)

    def get_timeline(self) -> list[dict]:
        """GET /timeline — per-day metric points."""
        return [self._daily_to_dict(day) for day in self._daily()]

    def get_sessions(self) -> list[dict]:
        """GET /sessions — one summary per study day (approximate)."""
        return [
            {
                "date": day.day.isoformat(),
                "study_minutes": day.study_minutes,
                "avg_focus": day.avg_focus,
                "avg_posture": day.avg_posture,
            }
            for day in self._daily()
        ]

    def get_analytics(self) -> dict:
        """GET /analytics — daily stats, trends, and streak."""
        daily = self._daily()
        focus = metric_trend(daily, "avg_focus") if daily else None
        posture = metric_trend(daily, "avg_posture") if daily else None
        return {
            "days": [self._daily_to_dict(day) for day in daily],
            "streak": study_streak(daily) if daily else 0,
            "trends": {
                "focus": asdict(focus) if focus else None,
                "posture": asdict(posture) if posture else None,
            },
        }

    def get_insights(self) -> dict:
        """GET /insights — combined multi-source insight."""
        insight = generate(self._daily())
        return {
            "observations": [asdict(observation) for observation in insight.observations],
            "inference": self._inference_to_dict(insight.inference),
            "recommendations": [self._rec_to_dict(rec) for rec in insight.recommendations],
        }

    def get_recommendations(self) -> list[dict]:
        """GET /recommendations — actionable coach suggestions."""
        return [self._rec_to_dict(rec) for rec in generate(self._daily()).recommendations]

    def get_report(self, *, period: str = "week", audience: str = "student") -> dict:
        """GET /reports — structured report + rendered Markdown."""
        report = build_report(self._daily(), period=period, audience=audience)
        return {
            "title": report.title,
            "audience": report.audience,
            "period": report.period,
            "confidence": report.confidence,
            "sections": [{"heading": s.heading, "body": s.body} for s in report.sections],
            "markdown": render_markdown(report),
        }

    # -- coach & gamification ----------------------------------------------

    def get_coach(self) -> list[dict]:
        """GET /coach — explainable, evidence-backed coaching messages."""
        messages = coach_messages(self._daily(), self._metric_points())
        return [self._coach_to_dict(message) for message in messages]

    def get_goals(self) -> dict:
        """GET /goals — XP, level, streak, consistency, achievements, targets."""
        daily = self._daily()
        state = compute_gamification(daily)
        return {
            "xp": state.xp,
            "level": state.level,
            "xp_into_level": state.xp_into_level,
            "xp_to_next_level": state.xp_to_next_level,
            "streak_days": state.streak_days,
            "consistency": state.consistency,
            "achievements": [
                {"key": a.key, "title": a.title, "description": a.description, "unlocked": a.unlocked}
                for a in state.achievements
            ],
            "daily_goal": self._goal_to_dict(goal_progress(daily, period="daily")),
            "weekly_goal": self._goal_to_dict(goal_progress(daily, period="weekly")),
        }

    def get_hourly(self) -> dict:
        """GET /hourly — average focus by hour-of-day (string keys for JSON)."""
        return {str(hour): value for hour, value in focus_by_hour(self._metric_points()).items()}

    def get_planned_vs_actual(self) -> list[dict]:
        """GET /planned-vs-actual — planned vs actual study minutes per day."""
        return planned_vs_actual(self._metric_points(), self._daily())

    def get_weekly_summary(self) -> dict:
        """GET /coach/weekly — explainable weekly narrative summary."""
        return weekly_summary(self._daily(), self._metric_points())

    # -- export -------------------------------------------------------------

    def export_formats(self) -> list[str]:
        """GET /export/formats — available export formats."""
        return list(available_formats())

    def export(self, fmt: str, *, kind: str = "analytics") -> dict:
        """GET /export?format=&kind= — serialize analytics or a report."""
        if kind == "report":
            payload: dict = self.get_report()
        elif kind == "analytics":
            payload = self.get_analytics()
        else:
            raise ValueError("kind must be 'analytics' or 'report'")
        return {"format": fmt, "kind": kind, "content": create_exporter(fmt).export(payload)}

    @staticmethod
    def _coach_to_dict(message) -> dict:
        return {
            "key": message.key,
            "category": message.category,
            "title": message.title,
            "message": message.message,
            "evidence": list(message.evidence),
            "supporting_metrics": dict(message.supporting_metrics),
            "confidence": message.confidence.value,
        }

    @staticmethod
    def _goal_to_dict(goal) -> dict:
        return {
            "period": goal.period,
            "target_minutes": goal.target_minutes,
            "actual_minutes": goal.actual_minutes,
            "progress": goal.progress,
            "achieved": goal.achieved,
        }

    # -- data rights --------------------------------------------------------

    def export_data(self) -> list[dict]:
        """GET /data/export — all stored samples as dicts."""
        return self._rights.export()

    def delete_data(self) -> dict:
        """DELETE /data — erase all stored samples."""
        return {"deleted": self._rights.delete_all()}

    # -- observability ------------------------------------------------------

    def get_health(self) -> dict:
        """GET /health — API, plugin, source, and storage health."""
        source_health = {}
        for key, source in self._connected.items():
            health = source.health_check()
            source_health[key] = {"status": health.status.value, "detail": health.detail}
        return {
            "api": "ok",
            "plugins": {
                "registered": list(available_source_keys()),
                "connected": sorted(self._connected),
            },
            "sources": source_health,
            "storage": self._storage_health(),
        }

    def _storage_health(self) -> dict:
        import os
        import sqlite3

        if not os.path.exists(self._db_path):
            return {"status": "empty", "detail": "no database yet"}
        try:
            connection = sqlite3.connect(self._db_path)
            try:
                count = connection.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
            finally:
                connection.close()
        except sqlite3.Error as exc:
            return {"status": "error", "detail": str(exc)}
        return {"status": "ok", "detail": f"{count} samples"}

    # -- serialization helpers ---------------------------------------------

    @staticmethod
    def _daily_to_dict(day: DailyStats) -> dict:
        return {
            "date": day.day.isoformat(),
            "study_minutes": day.study_minutes,
            "avg_focus": day.avg_focus,
            "avg_posture": day.avg_posture,
            "sample_count": day.sample_count,
        }

    @staticmethod
    def _inference_to_dict(inference) -> dict | None:
        if inference is None:
            return None
        return {
            "statement": inference.statement,
            "confidence": inference.confidence.value,
            "based_on": list(inference.based_on),
        }

    @staticmethod
    def _rec_to_dict(rec) -> dict:
        return {
            "key": rec.key,
            "message": rec.message,
            "rationale": rec.rationale,
            "confidence": rec.confidence.value,
        }
