"""AI Engineering World home dashboard."""

from html import escape

import streamlit as st

from core.application_loader import load_applications, load_projects
from core.launcher import launch
from services.platform_stats import dashboard_stats


def render() -> None:
    _section_header("Platform at a glance", "Overview", "A growing collection of end-to-end AI engineering work.")
    _render_kpis()

    _section_header(
        "Projects",
        "Build portfolio",
        "One real-world problem, solved with progressively more powerful AI techniques.",
    )
    _render_projects()

    _section_header("How the tiers connect", "Progression", "Same problem · same data · each tier adds a new capability on top of the previous.")
    _render_tier_progression()

    _section_header("Engineering principles", "How it is built", "Every module follows the same production-minded standards.")
    _render_principles()


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------

def _section_header(title: str, kicker: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="aiew-section-head">
            <div>
                <div class="aiew-section-kicker">{escape(kicker)}</div>
                <div class="aiew-section-title">{escape(title)}</div>
            </div>
            <div class="aiew-section-copy">{escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

def _render_kpis() -> None:
    stats = dashboard_stats()
    metrics = (
        ("Projects", stats["projects"], "Domain problem areas"),
        ("Capabilities", stats["capabilities"], "Techniques per project"),
        ("Live apps", stats["live"], "Ready to explore"),
        ("Platform status", stats["status"], "Local environment healthy"),
    )
    columns = st.columns(4)
    for column, (label, value, caption) in zip(columns, metrics, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="aiew-kpi">
                    <div class="aiew-kpi-label">{escape(label)}</div>
                    <div class="aiew-kpi-value">{escape(str(value))}</div>
                    <div class="aiew-kpi-caption">{escape(caption)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def _render_projects() -> None:
    for project in load_projects():
        with st.container(border=True):
            _render_project_header(project)
            st.divider()
            _render_capability_ladder(project)


def _render_project_header(project: dict) -> None:
    left, right = st.columns([3, 1])
    with left:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.4rem;">
                <span style="font-size:1.6rem;">{project['icon']}</span>
                <div>
                    <div style="font-size:1.1rem;font-weight:750;color:#0f172a;letter-spacing:-.02em;">
                        {escape(project['name'])}
                    </div>
                    <div style="font-size:.75rem;color:#64748b;margin-top:.1rem;">
                        {escape(project['category'])}
                    </div>
                </div>
            </div>
            <p style="font-size:.84rem;color:#475569;line-height:1.6;margin:0;">
                {escape(project['description'])}
            </p>
            """,
            unsafe_allow_html=True,
        )
    with right:
        live = sum(1 for a in project["apps"] if a["status"] == "live")
        total = len(project["apps"])
        st.markdown(
            f"""
            <div style="text-align:right;padding-top:.3rem;">
                <div style="font-size:1.4rem;font-weight:760;color:#0f172a;">{live}/{total}</div>
                <div style="font-size:.72rem;color:#64748b;">capabilities live</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_capability_ladder(project: dict) -> None:
    apps = project["apps"]
    cols = st.columns(len(apps))

    for col, app in zip(cols, apps):
        is_live = app["status"] == "live"
        border_color = "#4f46e5" if is_live else "#e2e8f0"
        bg_color = "#eef2ff" if is_live else "#f8fafc"
        text_color = "#3730a3" if is_live else "#94a3b8"
        badge = "✅ Live" if is_live else "⏳ Soon"
        badge_color = "#059669" if is_live else "#94a3b8"
        cursor = "pointer" if is_live else "default"

        stack_chips = "".join(
            f'<span style="font-size:.6rem;padding:.15rem .4rem;border-radius:999px;'
            f'background:#f1f5f9;color:#64748b;border:1px solid #e2e8f0;margin-right:.2rem;">'
            f'{escape(s)}</span>'
            for s in app["stack"][:3]
        )

        with col:
            # Wrap label + card in a div so CSS can target the button overlay
            live_class = "aiew-tier-live" if is_live else "aiew-tier-soon"
            st.markdown(
                f"""
                <div class="aiew-tier-card {live_class}"
                     style="border:1px solid {border_color};border-radius:.85rem;
                            background:{bg_color};padding:.7rem .75rem;
                            text-align:center;cursor:{cursor};position:relative;">
                    <div style="font-size:.62rem;font-weight:700;color:{badge_color};
                                letter-spacing:.06em;text-transform:uppercase;margin-bottom:.25rem;">
                        T{app['tier']}
                    </div>
                    <div style="font-size:.78rem;font-weight:700;color:{text_color};
                                line-height:1.3;margin-bottom:.35rem;">
                        {escape(app['capability'])}
                    </div>
                    <div style="font-size:.65rem;color:{badge_color};margin-bottom:.4rem;">
                        {badge}
                    </div>
                    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.15rem;">
                        {stack_chips}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Invisible overlay button for live tiers — captures the click,
            # CSS makes it transparent and positioned over the card above
            if is_live:
                if st.button(
                    "open",
                    key=f"open_{app['id']}",
                    use_container_width=True,
                    help=f"Open {app['capability']} workspace",
                ):
                    launch(app["id"])
                    st.rerun()


# ---------------------------------------------------------------------------
# Tier progression
# ---------------------------------------------------------------------------

def _render_tier_progression() -> None:
    tiers = (
        (
            "T1 · Machine Learning",
            "🤖",
            "#4f46e5",
            "#eef2ff",
            "What happened?",
            "We uploaded a loan dataset, cleaned it, and trained 4 classical models (Logistic Regression, Decision Tree, Random Forest, XGBoost) to predict approval.",
            "Why move to T2?",
            "Classical models treat every pattern as a weighted rule. A neural network can learn complex, non-linear combinations of features automatically — potentially uncovering patterns rules miss.",
            "live",
        ),
        (
            "T2 · Deep Learning",
            "🧠",
            "#0891b2",
            "#ecfeff",
            "What happened?",
            "We replaced the classical model with a Multi-Layer Perceptron (MLP). The network trained over multiple epochs and we watched the loss curve drop as it learned.",
            "Why move to T3?",
            "The neural network is now a black box — it predicts well but can't tell us *why*. In finance, regulators and customers demand a reason for every decision.",
            "live",
        ),
        (
            "T3 · Explainability",
            "🔍",
            "#7c3aed",
            "#f5f3ff",
            "What happened?",
            "We used SHAP and LIME to open the black box. SHAP shows which features pushed each prediction up or down. LIME fits a simple local explanation around any single decision.",
            "Why move to T4?",
            "Explanations answer 'why this prediction?' but a loan officer still reads static rules. What if they could ask the system questions in plain English using actual policy documents?",
            "live",
        ),
        (
            "T4 · RAG",
            "📚",
            "#059669",
            "#ecfdf5",
            "What happened?",
            "We store loan policy documents in a vector database. A language model retrieves the relevant policy chunks and grounds its answer — no hallucination, just facts from the document.",
            "Why move to T5?",
            "RAG answers questions but still needs a human to ask them. An autonomous agent can read an application, run checks, consult the policy, and produce a reasoned decision on its own.",
            "coming_soon",
        ),
        (
            "T5 · AI Agent",
            "🕵",
            "#d97706",
            "#fffbeb",
            "What happened?",
            "A single LLM-powered agent uses tools (data validator, risk scorer, policy lookup) to autonomously process a loan application end-to-end and write a structured decision report.",
            "Why move to T6?",
            "One agent handles everything sequentially. Splitting responsibilities across specialist agents — each an expert in one area — is faster, more auditable, and easier to improve.",
            "coming_soon",
        ),
        (
            "T6 · Multi-Agent",
            "🏗",
            "#dc2626",
            "#fef2f2",
            "What happened?",
            "Three specialist agents — Underwriter, Fraud Detector, and Compliance Officer — collaborate through a shared message bus. Each contributes its verdict; a Supervisor synthesises the final decision.",
            "Why is this the top tier?",
            "This mirrors how real loan decisions work in banks — multiple teams, each an expert, reaching a consensus. It is the closest AI approximation of a production credit workflow.",
            "coming_soon",
        ),
    )

    for tier in tiers:
        title, icon, accent, bg, q1, a1, q2, a2, status = tier
        is_live = status == "live"
        badge = "✅ Live" if is_live else "⏳ Coming soon"
        badge_color = "#059669" if is_live else "#94a3b8"

        with st.container(border=True):
            col_icon, col_content = st.columns([1, 11])

            with col_icon:
                st.markdown(
                    f'<div style="font-size:1.8rem;text-align:center;padding-top:.3rem;">{icon}</div>',
                    unsafe_allow_html=True,
                )

            with col_content:
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem;">
                        <span style="font-size:.95rem;font-weight:750;color:#0f172a;">{escape(title)}</span>
                        <span style="font-size:.65rem;font-weight:700;color:{badge_color};
                                     background:{'#ecfdf5' if is_live else '#f8fafc'};
                                     border:1px solid {'#a7f3d0' if is_live else '#e2e8f0'};
                                     padding:.1rem .45rem;border-radius:999px;">{badge}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem 1.5rem;">
                        <div>
                            <div style="font-size:.68rem;font-weight:800;color:{accent};
                                        letter-spacing:.08em;text-transform:uppercase;margin-bottom:.2rem;">
                                {escape(q1)}
                            </div>
                            <div style="font-size:.82rem;color:#475569;line-height:1.55;">
                                {escape(a1)}
                            </div>
                        </div>
                        <div>
                            <div style="font-size:.68rem;font-weight:800;color:{accent};
                                        letter-spacing:.08em;text-transform:uppercase;margin-bottom:.2rem;">
                                {escape(q2)}
                            </div>
                            <div style="font-size:.82rem;color:#475569;line-height:1.55;">
                                {escape(a2)}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Principles
# ---------------------------------------------------------------------------

def _render_principles() -> None:
    principles = (
        ("01", "Modular by design", "Clear boundaries between presentation, business logic, and data services."),
        ("02", "Evaluation first", "Quality, validation, and measurable outcomes built into every workflow."),
        ("03", "Deployment aware", "Artifacts and interfaces designed for the path from notebook to production."),
    )
    columns = st.columns(3)
    for column, (number, title, caption) in zip(columns, principles, strict=True):
        with column:
            with st.container(border=True):
                st.caption(number)
                st.markdown(f"**{title}**")
                st.caption(caption)
