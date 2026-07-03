"""Shared platform identity displayed in the Streamlit sidebar."""

import streamlit as st

from config.platform import APP_NAME, VERSION


def render_sidebar() -> None:
    """Render a restrained native sidebar header."""
    with st.sidebar:
        st.markdown(f"### ◈ {APP_NAME}")
        st.caption("Production AI engineering portfolio")
        st.markdown(
            f"**Workspace**  \n"
            f"Overview and application workflows  \n\n"
            f"`v{VERSION}` · 🟢 Online"
        )
        st.divider()
