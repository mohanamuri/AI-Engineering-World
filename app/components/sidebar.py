"""Shared platform identity and navigation displayed in the Streamlit sidebar."""

import streamlit as st

from config.platform import APP_NAME, VERSION
from core.application_loader import load_applications
from core.launcher import current_app, go_home, launch


def render_sidebar() -> None:
    """Render platform identity and dynamic application navigation."""
    with st.sidebar:
        # --- Brand ---
        st.markdown(f"### ◈ {APP_NAME}")
        st.caption("Production AI engineering portfolio")
        st.markdown(
            f"`v{VERSION}` &nbsp;·&nbsp; 🟢 Online",
            unsafe_allow_html=True,
        )
        st.divider()

        # --- Platform navigation ---
        st.markdown(
            '<div class="aiew-side-label">Platform</div>',
            unsafe_allow_html=True,
        )
        _nav_button(
            label="⊞  Dashboard",
            active=current_app() == "dashboard",
            on_click=go_home,
        )

        st.divider()

        # --- Applications (built from registry — no hardcoding) ---
        st.markdown(
            '<div class="aiew-side-label">Applications</div>',
            unsafe_allow_html=True,
        )
        for app in load_applications():
            app_id = app["id"]
            icon = app.get("icon", "▸")
            name = app["name"]
            subtitle = app.get("subtitle", "")
            label = f"{icon}  {name}"
            if subtitle:
                label += f"\n{subtitle}"

            _nav_button(
                label=label,
                active=current_app() == app_id,
                on_click=lambda aid=app_id: launch(aid),
            )


def _nav_button(label: str, active: bool, on_click) -> None:
    """Render a sidebar navigation button with active-state styling."""
    # Inject active class via a wrapper so CSS can target it
    active_class = "aiew-nav-btn aiew-nav-btn--active" if active else "aiew-nav-btn"
    st.markdown(
        f'<div class="{active_class}">',
        unsafe_allow_html=True,
    )
    st.button(
        label,
        on_click=on_click,
        use_container_width=True,
        type="primary" if active else "secondary",
    )
    st.markdown("</div>", unsafe_allow_html=True)
