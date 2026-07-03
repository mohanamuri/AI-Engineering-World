"""Platform footer rendered at the bottom of every page."""

import streamlit as st

from config.platform import APP_NAME, AUTHOR, DESCRIPTION, VERSION


def render_footer() -> None:
    """Render a minimal, informative platform footer."""
    st.markdown(
        f"""
        <div class="aiew-footer">
            <div class="aiew-footer-left">
                <span class="aiew-footer-brand">◈ {APP_NAME}</span>
                <span class="aiew-footer-sep">·</span>
                <span class="aiew-footer-desc">{DESCRIPTION}</span>
            </div>
            <div class="aiew-footer-right">
                <span class="aiew-footer-meta">v{VERSION}</span>
                <span class="aiew-footer-sep">·</span>
                <span class="aiew-footer-meta">Built by <strong>{AUTHOR}</strong></span>
                <span class="aiew-footer-sep">·</span>
                <a class="aiew-footer-link"
                   href="https://github.com/mohanamuri/AI-Engineering-World"
                   target="_blank" rel="noopener">
                    GitHub ↗
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
