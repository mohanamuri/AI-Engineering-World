"""Home-page hero for AI Engineering World."""

import streamlit as st

from config.platform import AUTHOR, AUTHOR_TITLE, GITHUB_URL, LINKEDIN_URL


def show_header() -> None:
    """Render the platform hero section."""
    st.markdown(
        f"""
        <section class="aiew-hero">
            <div class="aiew-eyebrow">◈ One Platform &nbsp;·&nbsp; Learn &nbsp;·&nbsp; Build &nbsp;·&nbsp; Deploy &nbsp;·&nbsp; Showcase</div>

            <div class="aiew-hero-title">
                AI Engineering
                <span style="background:linear-gradient(90deg,#818cf8 0%,#22d3ee 100%);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                             display:inline;">World</span>
            </div>

            <details class="aiew-agenda">
                <summary class="aiew-agenda-toggle">About this platform</summary>
                <p class="aiew-hero-copy">
                    A hands-on portfolio of production-minded machine learning,
                    deep learning, and generative AI systems — from data and
                    experimentation to evaluation and deployment. Six progressive
                    capability tiers, one real-world problem.
                </p>
            </details>

            <div class="aiew-chip-row">
                <span class="aiew-chip">🤖 ML · T1</span>
                <span class="aiew-chip">🧠 Deep Learning · T2</span>
                <span class="aiew-chip">🔍 XAI · T3</span>
                <span class="aiew-chip">📄 RAG · T4</span>
                <span class="aiew-chip">🕵 AI Agent · T5</span>
                <span class="aiew-chip">⚙️ Multi-Agent · T6</span>
            </div>

            <div class="aiew-hero-author">
                <div class="aiew-hero-avatar">MRA</div>
                <div>
                    <div class="aiew-hero-author-name">{AUTHOR}</div>
                    <div class="aiew-hero-author-title">{AUTHOR_TITLE}</div>
                    <div class="aiew-hero-author-links">
                        <a href="{LINKEDIN_URL}" target="_blank" rel="noopener" class="aiew-byline-link">LinkedIn ↗</a>
                        &nbsp;·&nbsp;
                        <a href="{GITHUB_URL}" target="_blank" rel="noopener" class="aiew-byline-link">GitHub ↗</a>
                    </div>
                </div>
                <div style="margin-left:auto;text-align:right;">
                    <span class="aiew-live-dot"></span>
                    <span style="font-size:.72rem;color:#34d399;font-weight:700;">6 tiers live</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
