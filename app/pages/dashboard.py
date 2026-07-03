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

        # Stack chips (max 3 shown)
        stack_chips = "".join(
            f'<span style="font-size:.6rem;padding:.15rem .4rem;border-radius:999px;'
            f'background:#f1f5f9;color:#64748b;border:1px solid #e2e8f0;margin-right:.2rem;">'
            f'{escape(s)}</span>'
            for s in app["stack"][:3]
        )

        with col:
            st.markdown(
                f"""
                <div style="border:1px solid {border_color};border-radius:.85rem;
                            background:{bg_color};padding:.7rem .75rem;text-align:center;
                            transition:all .2s ease;">
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

        if is_live:
            if st.button(
                "Open →",
                key=f"launch_{app['id']}",
                use_container_width=True,
                type="primary",
            ):
                launch(app["id"])
                st.rerun()
        else:
            st.button(
                "Coming soon",
                key=f"soon_{app['id']}",
                use_container_width=True,
                disabled=True,
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
