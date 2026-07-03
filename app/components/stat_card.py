import streamlit as st


def stat_card(title, value, icon):

    st.markdown(
        f"""
        <div style="
            background:#1f2937;
            padding:25px;
            border-radius:18px;
            text-align:center;
            color:white;
            box-shadow:0px 4px 12px rgba(0,0,0,0.2);
            margin-bottom:15px;
        ">
            <div style="font-size:42px;">{icon}</div>

            <h1 style="margin-bottom:0;color:white;">
                {value}
            </h1>

            <h4 style="margin-top:8px;color:#d1d5db;">
                {title}
            </h4>
        </div>
        """,
        unsafe_allow_html=True,
    )