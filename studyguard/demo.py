"""Build a ready-to-use service backed by the demo (seed) data source.

Used by the dashboard and API for offline exploration. Data flows only through
the service (Dashboard/API -> Service -> Domain); nothing reads SQLite directly.
"""
from __future__ import annotations

import os
import tempfile

import studyguard.sources  # noqa: F401  (registers built-in sources incl. demo)
from studyguard.api import StudyGuardService


def build_demo_service(days: int = 14) -> StudyGuardService:
    """Return a StudyGuardService pre-connected to the demo data source."""
    db_path = os.path.join(tempfile.mkdtemp(prefix="studyguard-demo-"), "demo.db")
    service = StudyGuardService(db_path=db_path, sample_period_s=60.0)
    service.grant_consent("demo")
    service.connect_source("demo", days=days)
    return service
