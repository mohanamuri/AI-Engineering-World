import streamlit as st
# Reuse the exploration service from hr_ml — same dataset, same charts
from applications.hr_ml.services.data_loader import DATAFRAME_SESSION_KEY as HR_ML_KEY
from applications.hr_dl.services.data_loader import DATAFRAME_SESSION_KEY
from applications.hr_ml.services.exploration import explore
import plotly.express as px


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
                     color_discrete_map={"No": "#7c3aed", "Yes": "#ef4444"}, hole=0.4)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    if result.attrition_by_dept is not None:
        st.subheader("Attrition by Department")
        df2 = result.attrition_by_dept
        yes_col = [c for c in df2.columns if "Yes" in c]
        if yes_col:
            fig = px.bar(df2, x="Department", y=yes_col[0], color_discrete_sequence=["#ef4444"])
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("Numeric summary"):
        st.dataframe(result.describe, use_container_width=True)
