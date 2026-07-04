"""Central, idempotent logging configuration (plain or JSON).

JSON logging + rotation are production-friendly; a Sentry hook can be added by
attaching a handler after :func:`setup_logging` (documented in DEPLOYMENT).
"""
from __future__ import annotations

import json
import logging
import logging.handlers
import sys

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
_configured = False


class JsonFormatter(logging.Formatter):
    """Structured JSON log records."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO", log_file: str | None = None, *, json_format: bool = False) -> None:
    """Configure the root logger with a console handler and optional rotating file."""
    global _configured
    if _configured:
        return
    root = logging.getLogger()
    root.setLevel(level.upper())
    formatter: logging.Formatter = JsonFormatter() if json_format else logging.Formatter(_FORMAT)

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    _configured = True
