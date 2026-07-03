"""AI Engineering World home dashboard."""

import streamlit as st

from components.application_card import application_card
from core.application_loader import load_applications
from services.platform_stats import dashboard_stats


def render() -> None:
    """Render platform health and featured application workspaces."""
    stats = dashboard_stats()
    _section_header(
        "Platform at a glance",
        "Overview",
        "A growing collection of end-to-end AI engineering work.",
    )
    _render_kpis(stats)

    _section_header(
        "Featured applications",
        "Build portfolio",
        "Open a workspace to inspect the complete engineering workflow.",
    )
    _render_applications()

    _section_header(
        "Engineering principles",
        "How it is built",
        "Every module follows the same production-minded standards.",
    )
    _render_principles()


def _section_header(title: str, kicker: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="aiew-section-head">
            <div>
                <div class="aiew-section-kicker">{kicker}</div>
                <div class="aiew-section-title">{title}</div>
            </div>
            <div class="aiew-section-copy">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_kpis(stats: dict[str, object]) -> None:
    metrics = (
        ("Learning tracks", stats["modules"], "Structured engineering paths"),
        ("Applications", stats["applications"], "Interactive AI workspaces"),
        ("Model families", stats["models"], "ML and deep learning"),
        ("Platform status", stats["status"], "Local environment healthy"),
    )
    columns = st.columns(4)

    for column, (label, value, caption) in zip(columns, metrics, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="aiew-kpi">
                    <div class="aiew-kpi-label">{label}</div>
                    <div class="aiew-kpi-value">{value}</div>
                    <div class="aiew-kpi-caption">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_applications() -> None:
    applications = load_applications()
    columns = st.columns(2)

    for index, app in enumerate(applications):
        with columns[index % len(columns)]:
            application_card(
                app["name"],
                app["category"],
                app["status"],
                app["description"],
                icon=app["icon"],
                difficulty=app["difficulty"],
                version=app["version"],
                key=app["id"],
            )


def _render_principles() -> None:
    principles = (
        (
            "01",
            "Modular by design",
            "Clear boundaries between presentation, business logic, and data services.",
        ),
        (
            "02",
            "Evaluation first",
            "Quality, validation, and measurable outcomes built into every workflow.",
        ),
        (
            "03",
            "Deployment aware",
            "Artifacts and interfaces designed for the path from notebook to production.",
        ),
    )
    columns = st.columns(3)
    for column, (number, title, caption) in zip(columns, principles, strict=True):
        with column:
            with st.container(border=True):
                st.caption(number)
                st.markdown(f"**{title}**")
                st.caption(caption)
