"""Home-page hero for AI Engineering World."""

import streamlit as st

from config.platform import AUTHOR, AUTHOR_TITLE, GITHUB_URL, LINKEDIN_URL


def show_header() -> None:
    """Render the platform hero section."""
    st.markdown(
        f"""<div class="aiew-hero">
<div style="text-align:center;margin-bottom:1.1rem;"><div class="aiew-eyebrow">◈ One Platform &nbsp;·&nbsp; Learn &nbsp;·&nbsp; Build &nbsp;·&nbsp; Deploy &nbsp;·&nbsp; Showcase</div></div>
<div style="display:flex;align-items:flex-end;gap:2rem;">
<div style="flex:1;"><div class="aiew-hero-title">AI Engineering <span class="aiew-gradient-word">World</span></div><div style="font-size:.8rem;color:#94a3b8;letter-spacing:.04em;margin:.35rem 0 .1rem;font-style:italic;">From Data to Decisions. From Models to Autonomous AI Systems.</div><div class="aiew-hero-copy">Building production-grade AI systems—from Machine Learning and Deep Learning to Generative AI and Autonomous AI Agents.</div><div class="aiew-chip-row"><span class="aiew-chip">🤖 Machine Learning</span><span class="aiew-chip">🧠 Deep Learning</span><span class="aiew-chip">🔍 Explainability</span><span class="aiew-chip">📄 RAG</span><span class="aiew-chip">🕵 AI Agent</span><span class="aiew-chip">⚙️ Multi-Agent</span></div></div>
<div style="flex-shrink:0;"><div class="aiew-hero-author"><div class="aiew-hero-avatar">MRA</div><div><div class="aiew-hero-author-name">{AUTHOR}</div><div class="aiew-hero-author-title">{AUTHOR_TITLE}</div><div class="aiew-hero-author-links"><a href="{LINKEDIN_URL}" target="_blank" rel="noopener" class="aiew-byline-link">LinkedIn ↗</a>&nbsp;·&nbsp;<a href="{GITHUB_URL}" target="_blank" rel="noopener" class="aiew-byline-link">GitHub ↗</a></div></div></div></div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
