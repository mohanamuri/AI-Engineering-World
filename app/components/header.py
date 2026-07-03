"""Home-page hero for AI Engineering World."""

import streamlit as st

from config.platform import AUTHOR, AUTHOR_TITLE, GITHUB_URL, LINKEDIN_URL


def show_header() -> None:
    """Render the platform hero section."""
    st.markdown(
        f"""
        <section class="aiew-hero">
            <div class="aiew-eyebrow">◈ One Platform &nbsp;·&nbsp; Learn &nbsp;·&nbsp; Build &nbsp;·&nbsp; Deploy &nbsp;·&nbsp; Showcase</div>
            <h1 class="aiew-hero-title">
                AI Engineering
                <span style="background:linear-gradient(90deg,#818cf8,#22d3ee);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    World
                </span>
            </h1>
            <details class="aiew-agenda">
                <summary class="aiew-agenda-toggle">Agenda</summary>
                <p class="aiew-hero-copy">
                    A hands-on portfolio of production-minded machine learning,
                    deep learning, and generative AI systems — from data and
                    experimentation to evaluation and deployment.
                </p>
            </details>
            <div class="aiew-chip-row" style="margin-top:1rem;">
                <span class="aiew-chip">🤖 Machine Learning</span>
                <span class="aiew-chip">🧠 Deep Learning</span>
                <span class="aiew-chip">✨ Generative AI</span>
                <span class="aiew-chip">🕵 AI Agent</span>
                <span class="aiew-chip">⚙️ Agentic AI</span>
                <span class="aiew-chip">🏗 AI Infrastructure</span>
            </div>
            <div class="aiew-hero-byline">
                ✏ Crafted by
                <a href="{LINKEDIN_URL}" target="_blank" rel="noopener" class="aiew-byline-link">
                    {AUTHOR}
                </a>
                &nbsp;·&nbsp; {AUTHOR_TITLE}
                &nbsp;·&nbsp;
                <a href="{GITHUB_URL}" target="_blank" rel="noopener" class="aiew-byline-link">
                    View on GitHub ↗
                </a>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
