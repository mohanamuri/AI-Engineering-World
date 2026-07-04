import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from applications.hr_ml.services.data_loader import DATAFRAME_SESSION_KEY
from applications.hr_ml.services.exploration import explore


def render():
    st.header("📊 Explore Data")

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    if dataframe is None:
        st.warning("Upload a dataset first.")
        return

    result = explore(dataframe)

    st.subheader("Dataset shape")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{result.shape[0]:,}")
    c2.metric("Columns", f"{result.shape[1]:,}")
    c3.metric("Missing values", f"{int(result.missing.sum()):,}")

    # --- Attrition distribution ---
    if not result.target_distribution.empty:
        st.subheader("Attrition distribution")
        fig = px.pie(
            values=result.target_distribution.values,
            names=result.target_distribution.index,
            color=result.target_distribution.index,
            color_discrete_map={"No": "#4f46e5", "Yes": "#ef4444"},
            hole=0.4,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    # --- Attrition by Department ---
    if result.attrition_by_dept is not None:
        st.subheader("Attrition rate by Department")
        df = result.attrition_by_dept
        yes_col = [c for c in df.columns if "Yes" in c]
        if yes_col:
            fig = px.bar(df, x="Department", y=yes_col[0], text=yes_col[0],
                         color_discrete_sequence=["#ef4444"])
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(yaxis_title="Attrition rate (%)", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # --- Attrition by Age group ---
    if result.attrition_by_age is not None:
        st.subheader("Attrition rate by Age group")
        df = result.attrition_by_age
        yes_col = [c for c in df.columns if "Yes" in c]
        if yes_col:
            fig = px.bar(df, x="AgeGroup", y=yes_col[0], text=yes_col[0],
                         color_discrete_sequence=["#f97316"])
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(yaxis_title="Attrition rate (%)", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # --- Attrition by Overtime ---
    if result.attrition_by_overtime is not None:
        st.subheader("Attrition rate by OverTime")
        df = result.attrition_by_overtime
        yes_col = [c for c in df.columns if "Yes" in c]
        if yes_col:
            fig = px.bar(df, x="OverTime", y=yes_col[0], text=yes_col[0],
                         color_discrete_sequence=["#8b5cf6"])
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(yaxis_title="Attrition rate (%)", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # --- Attrition by Job Role ---
    if result.attrition_by_role is not None:
        st.subheader("Attrition rate by Job Role")
        df = result.attrition_by_role
        yes_col = [c for c in df.columns if "Yes" in c]
        if yes_col:
            fig = px.bar(df.sort_values(yes_col[0], ascending=True),
                         x=yes_col[0], y="JobRole", orientation="h",
                         text=yes_col[0], color_discrete_sequence=["#06b6d4"])
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(xaxis_title="Attrition rate (%)", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # --- Missing values table ---
    missing_cols = result.missing[result.missing > 0]
    if missing_cols.empty:
        st.success("No missing values found — IBM HR dataset is complete.")
    else:
        st.subheader("Missing values")
        st.dataframe(
            missing_cols.reset_index().rename(columns={"index": "Column", 0: "Missing count"}),
            use_container_width=True,
            hide_index=True,
        )

    # --- Numeric stats ---
    with st.expander("Numeric summary statistics"):
        st.dataframe(result.describe, use_container_width=True)
