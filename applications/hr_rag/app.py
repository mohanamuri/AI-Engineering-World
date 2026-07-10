import streamlit as st
from core.launcher import go_home
from app.components.step_nav import render_page_nav, render_stepper

from applications.hr_rag.constants import NAVIGATION_SESSION_KEY, UPLOAD_PAGE_LABEL
from applications.hr_rag.pages import upload, explore, configure, chat, history, download


PAGES = {
    UPLOAD_PAGE_LABEL: upload.render,
    "🔍 Explore Chunks": explore.render,
    "⚙️ Configure RAG": configure.render,
    "💬 Chat": chat.render,
    "📜 History": history.render,
    "⬇ Download": download.render,
}


def run() -> None:
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        """
        <section class="aiew-tier-banner aiew-tb--t4">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">T4</div>
                <div>
                    <div class="aiew-tb-cap">Retrieval-Augmented Generation · Tier 4 of 6</div>
                    <div class="aiew-tb-title">HR Analytics — Policy Q&amp;A Assistant</div>
                    <div class="aiew-tb-desc">
                        RAG pipeline — upload an HR policy document, chunk and embed it into ChromaDB,
                        then ask natural-language questions grounded in the actual document.
                        Every answer cites its source chunk — no hallucination.
                    </div>
                    <div class="aiew-tb-flow">📄 Load → 🔍 Chunk → 🧮 Embed → 💬 Chat → 📜 History → ⬇ Export</div>
                    <div>
                        <span class="aiew-tech-pill">LangChain</span>
                        <span class="aiew-tech-pill">ChromaDB</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">HuggingFace</span>
                        <span class="aiew-tech-pill">llama-3.1-8b</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">HR Analytics · T4 workflow</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Load → Chunk → Embed → Chat → Export")

    render_stepper(list(PAGES.keys()), page)
    PAGES[page]()
    render_page_nav(list(PAGES.keys()), page, NAVIGATION_SESSION_KEY)
