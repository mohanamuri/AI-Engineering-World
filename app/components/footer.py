"""Platform footer rendered at the bottom of every page."""

import streamlit as st

from config.platform import APP_NAME, AUTHOR, DESCRIPTION, GITHUB_URL, LINKEDIN_URL, VERSION


def render_footer() -> None:
    """Render a clean footer with a rainbow gradient accent line."""
    st.markdown(
        f"""
        <div class="aiew-footer">
            <div class="aiew-footer-inner">
                <div>
                    <span class="aiew-footer-brand">◈ {APP_NAME}</span>
                    <span class="aiew-footer-sep">·</span>
                    <span class="aiew-footer-desc">{DESCRIPTION}</span>
                </div>
                <div>
                    <span class="aiew-footer-meta">v{VERSION}</span>
                    <span class="aiew-footer-sep">·</span>
                    <span class="aiew-footer-meta">Built by <strong>{AUTHOR}</strong></span>
                    <span class="aiew-footer-sep">·</span>
                    <a class="aiew-footer-link" href="{LINKEDIN_URL}" target="_blank" rel="noopener">LinkedIn ↗</a>
                    <span class="aiew-footer-sep">·</span>
                    <a class="aiew-footer-link" href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub ↗</a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
