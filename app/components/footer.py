"""Platform footer rendered at the bottom of every page."""

import streamlit as st

from config.platform import APP_NAME, AUTHOR, DESCRIPTION, GITHUB_URL, LINKEDIN_URL, VERSION


def render_footer() -> None:
    """Render a minimal, informative platform footer."""
    st.markdown(
        f"""
        <div class="aiew-footer">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:linear-gradient(90deg,#4f46e5,#7c3aed,#0891b2,#059669);"></div>
            <div class="aiew-footer-left">
                <span class="aiew-footer-brand">◈ {APP_NAME}</span>
                <span class="aiew-footer-sep">·</span>
                <span class="aiew-footer-desc">{DESCRIPTION}</span>
            </div>
            <div class="aiew-footer-right">
                <span class="aiew-footer-meta">v{VERSION}</span>
                <span class="aiew-footer-sep">·</span>
                <span class="aiew-footer-meta">Built by <strong style="color:#e2e8f0;">{AUTHOR}</strong></span>
                <span class="aiew-footer-sep">·</span>
                <a class="aiew-footer-link" href="{LINKEDIN_URL}" target="_blank" rel="noopener">LinkedIn ↗</a>
                <span class="aiew-footer-sep">·</span>
                <a class="aiew-footer-link" href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub ↗</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
