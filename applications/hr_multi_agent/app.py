import streamlit as st
from core.launcher import go_home

from applications.hr_multi_agent.constants import NAVIGATION_SESSION_KEY
from applications.hr_multi_agent.pages import application, panel, consensus, history, download


PAGES = {
    "👤 Employee Profile": application.render,
    "👥 Panel": panel.render,
    "🤝 Consensus": consensus.render,
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
        <section class="aiew-tier-banner aiew-tb--t6">
            <div class="aiew-tier-banner-inner">
                <div class="aiew-tier-badge-lg">T6</div>
                <div>
                    <div class="aiew-tb-cap">Multi-Agent System · Tier 6 of 6</div>
                    <div class="aiew-tb-title">HR Analytics — Expert Panel</div>
                    <div class="aiew-tb-desc">
                        Three independent specialist agents — HR Manager, Performance Evaluator,
                        and Risk Assessor — each analyse the employee from their domain.
                        The HR Director synthesises a consensus attrition risk decision,
                        resolving any disagreements between specialists.
                    </div>
                    <div class="aiew-tb-flow">👤 Profile → 👥 Panel → 🤝 Consensus → 📋 Director Decision → ⬇ Export</div>
                    <div>
                        <span class="aiew-tech-pill">LangGraph</span>
                        <span class="aiew-tech-pill">Groq</span>
                        <span class="aiew-tech-pill">Multi-Agent</span>
                        <span class="aiew-tech-pill">llama-3.1-8b</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="aiew-side-label">HR Analytics · T6 workflow</div>', unsafe_allow_html=True)
        if "hr_ma_nav_pending" in st.session_state:
            st.session_state[NAVIGATION_SESSION_KEY] = st.session_state.pop("hr_ma_nav_pending")
        page = st.radio("Navigation", list(PAGES.keys()), key=NAVIGATION_SESSION_KEY)
        st.caption("Profile → 3 Specialists → Director → Export")

    PAGES[page]()
