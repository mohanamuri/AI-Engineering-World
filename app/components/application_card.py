"""Reusable application card for the platform catalog."""

from html import escape

import streamlit as st

from core.launcher import launch


def application_card(
    name: str,
    category: str,
    status: str,
    description: str,
    *,
    icon: str = "AI",
    difficulty: str = "Intermediate",
    version: str = "1.0.0",
    key: str,
) -> None:
    """Render a descriptive application card and launch action."""
    is_live = status.casefold() == "live"
    status_label = "Available" if is_live else status

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="aiew-app-head">
                <div class="aiew-app-icon">{escape(icon)}</div>
                <div>
                    <div class="aiew-app-title">{escape(name)}</div>
                    <div class="aiew-app-category">{escape(category)}</div>
                </div>
            </div>
            <div class="aiew-app-copy">{escape(description)}</div>
            <div class="aiew-card-meta">
                <span class="aiew-badge">
                    <span class="aiew-dot"></span>{escape(status_label)}
                </span>
                <span class="aiew-meta-text">
                    {escape(difficulty)} · v{escape(version)}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open workspace →",
            key=f"launch_{key}",
            width="stretch",
            type="primary",
            disabled=not is_live,
        ):
            launch(key)
            st.rerun()
