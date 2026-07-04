"""Seed a database with demo metrics via the existing Repository (no ORM needed).

Usage: python migrations/seed.py [db_path]
"""
from __future__ import annotations

import sys

from studyguard.core import Snapshot
from studyguard.storage import SQLiteRepository


def seed(db_path: str = "studyguard.db", rows: int = 200) -> int:
    repo = SQLiteRepository(db_path)
    for i in range(rows):
        repo.save(
            Snapshot(i, True, 80.0, 88.0, "FOCUSED", "seed", 30.0, float(i), 0)
        )
    repo.close()
    return rows


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "studyguard.db"
    print("seeded", seed(path), "rows into", path)
