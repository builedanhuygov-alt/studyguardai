"""Reusable Streamlit UI components and theming for the StudyGuard dashboard.

All data must be passed in by the caller (which reads it from StudyGuardService).
Components never touch the domain or a database directly.
"""
from __future__ import annotations

from collections.abc import Iterable

import streamlit as st

_DARK_CSS = """
<style>
:root { --sg-bg:#0e1117; --sg-card:#161b22; --sg-text:#e6edf3; --sg-accent:#3b82f6; }
.sg-card{background:var(--sg-card);border:1px solid #30363d;border-radius:14px;padding:18px 20px;margin-bottom:8px;}
.sg-kpi-value{font-size:28px;font-weight:700;color:var(--sg-text);}
.sg-kpi-label{font-size:13px;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;}
.sg-badge{display:inline-block;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600;}
</style>
"""

_LIGHT_CSS = """
<style>
:root { --sg-bg:#ffffff; --sg-card:#f6f8fa; --sg-text:#1f2328; --sg-accent:#2563eb; }
.sg-card{background:var(--sg-card);border:1px solid #d0d7de;border-radius:14px;padding:18px 20px;margin-bottom:8px;}
.sg-kpi-value{font-size:28px;font-weight:700;color:var(--sg-text);}
.sg-kpi-label{font-size:13px;color:#57606a;text-transform:uppercase;letter-spacing:.06em;}
.sg-badge{display:inline-block;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600;}
</style>
"""

_SEVERITY_COLORS = {
    "low": "#16a34a",
    "elevated": "#d97706",
    "high": "#dc2626",
    "positive": "#16a34a",
    "info": "#2563eb",
    "warning": "#d97706",
}


def inject_theme(theme: str) -> None:
    """Inject dark/light CSS variables."""
    st.markdown(_DARK_CSS if theme == "Dark" else _LIGHT_CSS, unsafe_allow_html=True)


def section(title: str, subtitle: str | None = None) -> None:
    """Render a section header."""
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def kpi(label: str, value: str, help_text: str | None = None) -> None:
    """Render a single KPI metric."""
    st.metric(label=label, value=value, help=help_text)


def kpi_row(items: Iterable[tuple[str, str]]) -> None:
    """Render a row of KPI metrics."""
    items = list(items)
    if not items:
        return
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items, strict=False):
        with column:
            kpi(label, value)


def badge(text: str, severity: str = "info") -> str:
    """Return an HTML badge string."""
    color = _SEVERITY_COLORS.get(severity, "#2563eb")
    return f"<span class='sg-badge' style='background:{color}22;color:{color}'>{text}</span>"


def card(title: str, body_html: str) -> None:
    """Render a titled card."""
    st.markdown(
        f"<div class='sg-card'><div class='sg-kpi-label'>{title}</div>{body_html}</div>",
        unsafe_allow_html=True,
    )
