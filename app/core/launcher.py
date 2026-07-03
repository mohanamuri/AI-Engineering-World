import streamlit as st


def launch(app_id):
    st.session_state.current_app = app_id


def current_app():
    return st.session_state.get(
        "current_app",
        "dashboard",
    )


def go_home():
    st.session_state.current_app = "dashboard"