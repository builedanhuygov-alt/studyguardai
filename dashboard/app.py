"""StudyGuard AI — SaaS-style analytics dashboard (Streamlit).

Architecture: Dashboard -> StudyGuardService -> Domain. The dashboard NEVER
reads a database directly. Seed data is provided only by the demo data source
(via ``build_demo_service``).

Run locally:
    pip install -e ".[dashboard]"
    streamlit run dashboard/app.py
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard import components as ui
from studyguard import __version__
from studyguard.api import StudyGuardService
from studyguard.demo import build_demo_service

PAGES = [
    "Overview",
    "Today's Study",
    "Session Timeline",
    "Analytics",
    "AI Coach",
    "Goals & Achievements",
    "Reports",
    "Settings",
    "Plugins",
    "About",
]


@st.cache_resource
def get_service() -> StudyGuardService:
    """Build the (cached) demo-backed service. Swap for a real service in prod."""
    return build_demo_service(days=14)


def _analytics_df(service: StudyGuardService) -> pd.DataFrame:
    days = service.get_analytics().get("days", [])
    if not days:
        return pd.DataFrame(columns=["date", "study_minutes", "avg_focus", "avg_posture"])
    frame = pd.DataFrame(days)
    frame["date"] = pd.to_datetime(frame["date"])
    return frame


def page_overview(service: StudyGuardService) -> None:
    ui.section("Overview", "Your study intelligence at a glance")
    analytics = service.get_analytics()
    goals = service.get_goals()
    days = analytics.get("days", [])
    latest = days[-1] if days else {"avg_focus": 0, "avg_posture": 0, "study_minutes": 0}
    study_score = round((latest["avg_focus"] + latest["avg_posture"]) / 2, 1)
    ui.kpi_row(
        [
            ("Study Score", f"{study_score:.0f}"),
            ("Focus Score", f"{latest['avg_focus']:.0f}"),
            ("Posture Score", f"{latest['avg_posture']:.0f}"),
            ("Streak", f"{goals['streak_days']} d"),
        ]
    )
    ui.kpi_row(
        [
            ("Level", str(goals["level"])),
            ("XP", str(goals["xp"])),
            ("Consistency", f"{goals['consistency'] * 100:.0f}%"),
            ("Daily goal", f"{goals['daily_goal']['progress'] * 100:.0f}%"),
        ]
    )

    frame = _analytics_df(service)
    if not frame.empty:
        left, right = st.columns([2, 1])
        with left:
            ui.section("Weekly trend")
            st.line_chart(frame.set_index("date")[["avg_focus", "avg_posture"]])
        with right:
            ui.section("Balance")
            radar = go.Figure()
            radar.add_trace(
                go.Scatterpolar(
                    r=[
                        latest["avg_focus"],
                        latest["avg_posture"],
                        goals["consistency"] * 100,
                        goals["daily_goal"]["progress"] * 100,
                        min(goals["streak_days"] * 10, 100),
                    ],
                    theta=["Focus", "Posture", "Consistency", "Goal", "Streak"],
                    fill="toself",
                )
            )
            radar.update_layout(polar={"radialaxis": {"range": [0, 100]}}, showlegend=False, height=280)
            st.plotly_chart(radar, use_container_width=True)

    coach = service.get_coach()
    if coach:
        top = coach[0]
        ui.card(
            "Coach recommendation",
            f"<div class='sg-kpi-value'>{top['title']}</div><p>{top['message']}</p>"
            f"{ui.badge(top['confidence'], top['confidence'])}",
        )


def page_today(service: StudyGuardService) -> None:
    ui.section("Today's Study", "Current session and goal progress")
    analytics = service.get_analytics()
    goals = service.get_goals()
    days = analytics.get("days", [])
    latest = days[-1] if days else {"avg_focus": 0, "avg_posture": 0, "study_minutes": 0}
    ui.kpi_row(
        [
            ("Current status", "Focused" if latest["avg_focus"] >= 60 else "Needs focus"),
            ("Session minutes", f"{latest['study_minutes']:.0f}"),
            ("Focus", f"{latest['avg_focus']:.0f}"),
            ("Posture", f"{latest['avg_posture']:.0f}"),
        ]
    )
    daily = goals["daily_goal"]
    st.progress(min(daily["progress"], 1.0), text=f"Daily goal: {daily['actual_minutes']:.0f}/{daily['target_minutes']:.0f} min")
    weekly = goals["weekly_goal"]
    st.progress(min(weekly["progress"], 1.0), text=f"Weekly goal: {weekly['actual_minutes']:.0f}/{weekly['target_minutes']:.0f} min")

    hourly = service.get_hourly()
    if hourly:
        ui.section("Hourly productivity", "Average focus by hour of day")
        hf = pd.DataFrame({"hour": [int(h) for h in hourly], "focus": list(hourly.values())}).sort_values("hour")
        st.bar_chart(hf.set_index("hour"))


def page_timeline(service: StudyGuardService) -> None:
    ui.section("Session Timeline", "Study sessions over time")
    sessions = service.get_sessions()
    if not sessions:
        st.info("No sessions yet.")
        return
    frame = pd.DataFrame(sessions)
    st.dataframe(frame, use_container_width=True)
    frame["date"] = pd.to_datetime(frame["date"])
    fig = px.scatter(
        frame, x="date", y="study_minutes", size="study_minutes", color="avg_focus",
        color_continuous_scale="Blues", height=320,
    )
    st.plotly_chart(fig, use_container_width=True)


def page_analytics(service: StudyGuardService) -> None:
    ui.section("Analytics", "Trends, distributions, and heatmaps")
    frame = _analytics_df(service)
    if frame.empty:
        st.info("No analytics yet.")
        return
    tab_trend, tab_area, tab_heat = st.tabs(["Trend", "Study time", "Heatmap"])
    with tab_trend:
        st.line_chart(frame.set_index("date")[["avg_focus", "avg_posture"]])
    with tab_area:
        st.area_chart(frame.set_index("date")[["study_minutes"]])
    with tab_heat:
        heat = frame.copy()
        heat["weekday"] = heat["date"].dt.day_name()
        heat["week"] = heat["date"].dt.isocalendar().week.astype(int)
        pivot = heat.pivot_table(index="weekday", columns="week", values="study_minutes", aggfunc="sum").fillna(0)
        fig = px.imshow(pivot, color_continuous_scale="Greens", aspect="auto", height=320)
        st.plotly_chart(fig, use_container_width=True)

    planned = service.get_planned_vs_actual()
    if planned:
        ui.section("Planned vs actual")
        st.bar_chart(pd.DataFrame(planned).set_index("date")[["planned", "actual"]])


def page_coach(service: StudyGuardService) -> None:
    ui.section("AI Coach", "Explainable, evidence-backed coaching")
    for message in service.get_coach():
        with st.container():
            st.markdown(
                f"**{message['title']}** {ui.badge(message['confidence'], message['confidence'])}",
                unsafe_allow_html=True,
            )
            st.write(message["message"])
            if message["evidence"]:
                st.caption("Evidence: " + "; ".join(message["evidence"]))


def page_goals(service: StudyGuardService) -> None:
    ui.section("Goals & Achievements")
    goals = service.get_goals()
    ui.kpi_row(
        [
            ("Level", str(goals["level"])),
            ("XP", str(goals["xp"])),
            ("To next level", str(goals["xp_to_next_level"])),
            ("Streak", f"{goals['streak_days']} d"),
        ]
    )
    for achievement in goals["achievements"]:
        icon = "\U0001f3c6" if achievement["unlocked"] else "\U0001f512"
        st.write(f"{icon} **{achievement['title']}** — {achievement['description']}")


def page_reports(service: StudyGuardService) -> None:
    ui.section("Reports")
    period = st.selectbox("Period", ["week", "month"])
    audience = st.selectbox("Audience", ["student", "parent", "teacher", "personal"])
    report = service.get_report(period=period, audience=audience)
    st.markdown(report["markdown"])
    fmt = st.selectbox("Export format", service.export_formats())
    st.download_button(
        "Download export",
        data=service.export(fmt, kind="analytics")["content"],
        file_name=f"studyguard-analytics.{fmt}",
    )


def page_settings(service: StudyGuardService) -> None:
    ui.section("Settings")
    st.selectbox("Theme", ["Dark", "Light"], key="theme")
    st.select_slider("Focus alert threshold", options=list(range(0, 101, 5)), value=50)
    st.select_slider("Posture alert threshold", options=list(range(0, 101, 5)), value=55)
    st.toggle("Enable AI coach", value=True)
    st.toggle("Store metrics", value=True)
    st.caption("Settings are illustrative in the demo; wire to Config in production.")


def page_plugins(service: StudyGuardService) -> None:
    ui.section("Plugins & Data Sources")
    st.dataframe(pd.DataFrame(service.list_sources()), use_container_width=True)
    health = service.get_health()
    st.json(health)


def page_about(service: StudyGuardService) -> None:
    ui.section("About", f"StudyGuard AI v{__version__}")
    st.write(
        "Privacy-first, on-device AI study coach. The camera is one of many data "
        "sources; analytics, coaching, goals, and reports run over a common domain."
    )
    st.caption("Dashboard -> Service -> Domain. No raw frames are ever stored.")


_ROUTER = {
    "Overview": page_overview,
    "Today's Study": page_today,
    "Session Timeline": page_timeline,
    "Analytics": page_analytics,
    "AI Coach": page_coach,
    "Goals & Achievements": page_goals,
    "Reports": page_reports,
    "Settings": page_settings,
    "Plugins": page_plugins,
    "About": page_about,
}


def main() -> None:
    st.set_page_config(page_title="StudyGuard AI", page_icon="\U0001f4da", layout="wide")
    theme = st.session_state.get("theme", "Dark")
    ui.inject_theme(theme)
    st.sidebar.title("\U0001f4da StudyGuard AI")
    st.sidebar.caption("AI Study Coach Platform")
    page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")
    st.sidebar.selectbox("Theme", ["Dark", "Light"], key="theme")
    service = get_service()
    _ROUTER[page](service)


if __name__ == "__main__":
    main()
