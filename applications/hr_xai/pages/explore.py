import streamlit as st
import plotly.express as px
from applications.hr_xai.services.data_loader import DATAFRAME_SESSION_KEY
from applications.hr_ml.services.exploration import explore
from applications.shared.api_reference import render_api_reference


def render():
    st.header("📊 Explore Data")
    df = st.session_state.get(DATAFRAME_SESSION_KEY)
    if df is None:
        st.warning("Upload a dataset first.")
        return
    result = explore(df)
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{result.shape[0]:,}")
    c2.metric("Columns", f"{result.shape[1]:,}")
    c3.metric("Missing values", f"{int(result.missing.sum()):,}")

    if not result.target_distribution.empty:
        st.subheader("Attrition distribution")
        fig = px.pie(values=result.target_distribution.values,
                     names=result.target_distribution.index,
                     color=result.target_distribution.index,
                     color_discrete_map={"No": "#0d9488", "Yes": "#ef4444"}, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    if result.attrition_by_dept is not None:
        st.subheader("Attrition by Department")
        df2 = result.attrition_by_dept
        yes_col = [c for c in df2.columns if "Yes" in c]
        if yes_col:
            fig = px.bar(df2, x="Department", y=yes_col[0], color_discrete_sequence=["#ef4444"])
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("Summary statistics"):
        st.dataframe(result.describe, use_container_width=True)
    render_api_reference("hr_xai", "explore")
