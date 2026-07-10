"""Shared platform identity and navigation displayed in the Streamlit sidebar."""

import streamlit as st

from config.platform import APP_NAME, AUTHOR, AUTHOR_TITLE, GITHUB_URL, LINKEDIN_URL, VERSION
from core.application_loader import load_projects
from core.launcher import current_app, go_home, launch

_TIER_ICONS = {
    "live": "✅",
    "coming_soon": "⏳",
}


def render_sidebar() -> None:
    """Render platform identity and grouped project navigation."""
    with st.sidebar:
        # --- Brand ---
        st.markdown(f"### ◈ {APP_NAME}")
        st.caption("Production AI engineering portfolio")
        st.markdown(f"`v{VERSION}` &nbsp;·&nbsp; 🟢 Online", unsafe_allow_html=True)
        st.divider()

        # --- Platform ---
        st.markdown('<div class="aiew-side-label">Platform</div>', unsafe_allow_html=True)
        _nav_button(
            label="⊞  Dashboard",
            active=current_app() == "dashboard",
            on_click=go_home,
            disabled=False,
        )
        _nav_button(
            label="📖  Documentation",
            active=current_app() == "documentation",
            on_click=lambda: launch("documentation"),
            disabled=False,
        )

        st.divider()

        # --- Projects grouped by section (from registry — no hardcoding) ---
        projects = load_projects()

        # Collect unique sections in order of first appearance
        seen_sections: list[str] = []
        for project in projects:
            s = project.get("section", "Projects")
            if s not in seen_sections:
                seen_sections.append(s)

        for section in seen_sections:
            st.markdown(f'<div class="aiew-side-label">{section}</div>', unsafe_allow_html=True)
            for project in projects:
                if project.get("section", "Projects") != section:
                    continue
                live_count = sum(1 for a in project["apps"] if a["status"] == "live")
                total_count = len(project["apps"])

                with st.expander(
                    f"{project['icon']}  {project['short_name']}  `{live_count}/{total_count}`",
                    expanded=_project_is_active(project),
                ):
                    for app in project["apps"]:
                        is_live = app["status"] == "live"
                        tier_icon = _TIER_ICONS[app["status"]]
                        tier_prefix = app.get("tier_label", "T")
                        label = f"{tier_icon} {tier_prefix}{app['tier']} · {app['capability']}"

                        _nav_button(
                            label=label,
                            active=current_app() == app["id"],
                            on_click=lambda aid=app["id"]: launch(aid),
                            disabled=not is_live,
                            key=app["id"],
                        )

        st.divider()
        st.caption("More projects coming soon.")


def render_sidebar_footer() -> None:
    """Render the author card at the bottom of the sidebar (call after route())."""
    with st.sidebar:
        st.divider()
        st.markdown(
            f"""
            <div class="aiew-author-card">
                <div class="aiew-author-avatar">MRA</div>
                <div class="aiew-author-info">
                    <div class="aiew-author-name">{AUTHOR}</div>
                    <div class="aiew-author-title">{AUTHOR_TITLE}</div>
                    <div class="aiew-author-links">
                        <a href="{LINKEDIN_URL}" target="_blank" rel="noopener" class="aiew-author-link">LinkedIn ↗</a>
                        <span class="aiew-author-sep">·</span>
                        <a href="{GITHUB_URL}" target="_blank" rel="noopener" class="aiew-author-link">GitHub ↗</a>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _project_is_active(project: dict) -> bool:
    """Expand the project group that contains the currently active app."""
    return any(app["id"] == current_app() for app in project["apps"])


def _nav_button(label: str, active: bool, on_click, disabled: bool = False, key: str = None) -> None:
    active_class = "aiew-nav-btn aiew-nav-btn--active" if active else "aiew-nav-btn"
    st.markdown(f'<div class="{active_class}">', unsafe_allow_html=True)
    st.button(
        label,
        on_click=on_click,
        use_container_width=True,
        disabled=disabled,
        key=key or f"nav_{label}",
    )
    st.markdown("</div>", unsafe_allow_html=True)
