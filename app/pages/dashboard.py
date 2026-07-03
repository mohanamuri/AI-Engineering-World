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
    for i, project in enumerate(load_projects()):
        with st.container(border=True):
            _render_project_header(project)
            with st.expander("View capabilities & progression", expanded=(i == 0)):
                st.divider()
                _render_capability_ladder(project)
                st.divider()
                _render_project_progression(project)


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

            if is_live:
                if st.button(
                    "open",
                    key=f"open_{app['id']}",
                    use_container_width=True,
                    help=f"Open {app['capability']} workspace",
                ):
                    launch(app["id"])
                    st.rerun()


def _render_project_progression(project: dict) -> None:
    """Collapsible tier progression story — one expander per project."""
    apps = project["apps"]

    # Only render if at least one app has progression text
    if not any("what" in app for app in apps):
        return

    with st.expander("📖 How this project progresses — tier by tier", expanded=False):
        for i, app in enumerate(apps):
            what = app.get("what", "")
            why_next = app.get("why_next", "")
            is_live = app["status"] == "live"
            is_last = i == len(apps) - 1
            badge_color = "#059669" if is_live else "#94a3b8"
            badge_bg = "#ecfdf5" if is_live else "#f8fafc"
            badge_border = "#a7f3d0" if is_live else "#e2e8f0"
            badge = "✅ Live" if is_live else "⏳ Coming soon"

            st.markdown(
                f"""
                <div style="display:grid;grid-template-columns:auto 1fr;gap:.6rem 1rem;
                            padding:.75rem 0;{'border-bottom:1px solid #f1f5f9;' if not is_last else ''}">
                    <div style="display:flex;flex-direction:column;align-items:center;gap:.25rem;">
                        <div style="width:2rem;height:2rem;border-radius:.5rem;
                                    background:{'#eef2ff' if is_live else '#f8fafc'};
                                    border:1px solid {'#c7d2fe' if is_live else '#e2e8f0'};
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:.62rem;font-weight:800;
                                    color:{'#4f46e5' if is_live else '#94a3b8'};">
                            T{app['tier']}
                        </div>
                        {'<div style="width:1px;flex:1;background:#e2e8f0;min-height:.75rem;"></div>' if not is_last else ''}
                    </div>
                    <div style="padding-bottom:.25rem;">
                        <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;">
                            <span style="font-size:.85rem;font-weight:750;color:#0f172a;">
                                T{app['tier']} · {escape(app['capability'])}
                            </span>
                            <span style="font-size:.62rem;font-weight:700;color:{badge_color};
                                         background:{badge_bg};border:1px solid {badge_border};
                                         padding:.1rem .4rem;border-radius:999px;">{badge}</span>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.4rem 1.2rem;">
                            <div>
                                <div style="font-size:.65rem;font-weight:800;color:#4f46e5;
                                            letter-spacing:.08em;text-transform:uppercase;margin-bottom:.15rem;">
                                    What happened
                                </div>
                                <div style="font-size:.8rem;color:#475569;line-height:1.55;">
                                    {escape(what)}
                                </div>
                            </div>
                            <div>
                                <div style="font-size:.65rem;font-weight:800;color:#0891b2;
                                            letter-spacing:.08em;text-transform:uppercase;margin-bottom:.15rem;">
                                    {'Why move to T' + str(app['tier'] + 1) if not is_last else 'Why this is the final tier'}
                                </div>
                                <div style="font-size:.8rem;color:#475569;line-height:1.55;">
                                    {escape(why_next)}
                                </div>
                            </div>
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
