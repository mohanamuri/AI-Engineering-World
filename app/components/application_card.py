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
    stack: list[str] | None = None,
    key: str,
) -> None:
    """Render a descriptive application card with stack chips and launch action."""
    is_live = status.casefold() == "live"
    status_label = "Available" if is_live else status

    stack_html = ""
    if stack:
        chips = "".join(
            f'<span class="aiew-stack-chip">{escape(s)}</span>'
            for s in stack
        )
        stack_html = f'<div class="aiew-stack-row">{chips}</div>'

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
            {stack_html}
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Open workspace →",
            key=f"launch_{key}",
            use_container_width=True,
            type="primary",
            disabled=not is_live,
        ):
            launch(key)
            st.rerun()
