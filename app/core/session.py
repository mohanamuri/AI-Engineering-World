import streamlit as st


def initialize():

    defaults = {

        "current_app": "dashboard",

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value