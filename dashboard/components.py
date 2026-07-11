"""UI components for the dashboard."""

from __future__ import annotations

import streamlit as st


def section(title: str, subtitle: str = "") -> None:
    """Display a section header."""
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def kpi_row(kpis: list[tuple[str, str]]) -> None:
    """Display KPI metrics in a row."""
    cols = st.columns(len(kpis))
    for col, (label, value) in zip(cols, kpis):
        with col:
            st.metric(label, value)


def card(title: str, content: str) -> None:
    """Display a card with content."""
    with st.container():
        st.markdown(f"### {title}")
        st.markdown(content, unsafe_allow_html=True)


def badge(text: str, value: float) -> str:
    """Create a badge HTML."""
    return f'<span style="background-color: #eee; padding: 2px 6px; border-radius: 3px;">{text}</span>'


def inject_theme(theme: str) -> None:
    """Inject theme CSS."""
    pass
