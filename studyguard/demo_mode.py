"""Demo & Presentation modes — run the whole product with seed data, no webcam.

``studyguard demo``     prints a scripted, data-driven walkthrough once.
``studyguard present``   loops the walkthrough for a live pitch.
Both read only from StudyGuardService (Dashboard/API/Desktop use the same path).
"""
from __future__ import annotations

import time

from studyguard.demo import build_demo_service


def run_demo(*, present: bool = False, cycles: int = 1, sleep_s: float = 1.5) -> dict:
    """Run the demo walkthrough; returns the weekly summary (for tests)."""
    service = build_demo_service(days=14)
    summary = service.get_weekly_summary()
    goals = service.get_goals()
    coach = service.get_coach()
    analytics = service.get_analytics()

    banner = "\U0001f3a4 PRESENTATION MODE" if present else "\u25b6\ufe0f  DEMO MODE"
    print("=" * 60)
    print(f"{banner} — StudyGuard AI (seed data, no webcam required)")
    print("=" * 60)
    print("\n\U0001f4dd Weekly AI-Coach summary:")
    for line in summary["narrative"]:
        print(f"   • {line}")
    print(
        f"\n\U0001f3c6 Level {goals['level']} · XP {goals['xp']} · "
        f"Streak {goals['streak_days']}d · Consistency {goals['consistency'] * 100:.0f}%"
    )
    print("\n\U0001f4a1 Top coaching:")
    for message in coach[:3]:
        print(f"   • [{message['confidence']}] {message['title']}: {message['message']}")

    days = analytics.get("days", [])
    total_cycles = cycles if cycles and cycles > 0 else 3
    for step in range(total_cycles):
        if step < len(days):
            day = days[-(step + 1)]
            print(
                f"\n\U0001f4c8 {day['date']}: focus {day['avg_focus']:.0f} · "
                f"posture {day['avg_posture']:.0f} · {day['study_minutes']:.0f} min"
            )
        if present and sleep_s > 0:
            time.sleep(sleep_s)
    print("\n\u2705 Demo complete. Open the dashboard (streamlit) or desktop app for the full UI.")
    return summary
