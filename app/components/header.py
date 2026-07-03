"""Home-page hero for AI Engineering World."""

import streamlit as st

from config.platform import AUTHOR, AUTHOR_TITLE, GITHUB_URL, LINKEDIN_URL


def show_header() -> None:
    """Render the platform hero section."""
    st.markdown(
        f"""<div class="aiew-hero">
<div class="aiew-eyebrow">◈ One Platform &nbsp;·&nbsp; Learn &nbsp;·&nbsp; Build &nbsp;·&nbsp; Deploy &nbsp;·&nbsp; Showcase</div>
<div class="aiew-hero-title">AI Engineering <span class="aiew-gradient-word">World</span></div>
<div class="aiew-hero-copy">A hands-on portfolio of production-minded machine learning, deep learning, and generative AI systems — from data and experimentation to evaluation and deployment. Six progressive capability tiers, one real-world problem.</div>
<div class="aiew-chip-row"><span class="aiew-chip">🤖 Machine Learning</span><span class="aiew-chip">🧠 Deep Learning</span><span class="aiew-chip">🔍 Explainability</span><span class="aiew-chip">📄 RAG</span><span class="aiew-chip">🕵 AI Agent</span><span class="aiew-chip">⚙️ Multi-Agent</span></div>
<div class="aiew-hero-author">
<div class="aiew-hero-avatar">MRA</div>
<div><div class="aiew-hero-author-name">{AUTHOR}</div><div class="aiew-hero-author-title">{AUTHOR_TITLE}</div><div class="aiew-hero-author-links"><a href="{LINKEDIN_URL}" target="_blank" rel="noopener" class="aiew-byline-link">LinkedIn ↗</a>&nbsp;·&nbsp;<a href="{GITHUB_URL}" target="_blank" rel="noopener" class="aiew-byline-link">GitHub ↗</a></div></div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
