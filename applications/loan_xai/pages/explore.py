"""Explore page for the loan eligibility XAI pipeline.
Reuses loan_ml exploration service with loan_xai session keys.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from applications.loan_xai.constants import (
    DATAFRAME_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.loan_ml.services.exploration import (
    DatasetProfile,
    correlation_matrix,
    dataframe_to_csv,
    detect_target_column,
    missing_value_summary,
    numeric_feature,
    profile_dataset,
    statistical_summary,
    target_distribution,
)
from applications.loan_ml.utils.helpers import format_bytes
from applications.shared.api_reference import render_api_reference

CHART_COLOR = "#7c3aed"
PREVIEW_ROW_OPTIONS = (10, 25, 50, 100)


def render() -> None:
    st.header("📊 Explore Dataset")
    st.caption("Inspect data quality and feature distributions before building the pipeline.")

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    if not isinstance(dataframe, pd.DataFrame):
        with st.container(border=True):
            st.warning("No dataset uploaded.")
            st.button("← Go to Upload Dataset", type="primary",
                      on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: UPLOAD_PAGE_LABEL}))
        return

    profile = profile_dataset(dataframe)

    # Summary
    st.subheader("Dataset summary")
    for col, (label, value, help_text) in zip(
        st.columns(5),
        [("Rows", f"{profile.rows:,}", ""), ("Columns", f"{profile.columns:,}", ""),
         ("Missing", f"{profile.missing_values:,}", ""), ("Duplicates", f"{profile.duplicate_rows:,}", ""),
         ("Memory", format_bytes(profile.memory_bytes), "")],
        strict=True,
    ):
        with col:
            with st.container(border=True):
                st.metric(label, value)

    st.divider()

    # Data types
    st.subheader("Data types")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### Numeric")
            st.write(" · ".join(f"`{c}`" for c in profile.numeric_columns) or "None")
    with c2:
        with st.container(border=True):
            st.markdown("#### Categorical")
            st.write(" · ".join(f"`{c}`" for c in profile.categorical_columns) or "None")

    st.divider()

    # Target distribution
    st.subheader("Target distribution")
    target_col = detect_target_column(dataframe)
    if target_col:
        dist = target_distribution(dataframe, target_col)
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.container(border=True):
                st.dataframe(dist, hide_index=True, width="stretch")
        with c2:
            fig = px.bar(dist, x="Value", y="Count", color_discrete_sequence=[CHART_COLOR], text_auto=True)
            fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No recognized target column detected.")

    st.divider()

    # Missing values
    st.subheader("Missing values")
    mv = missing_value_summary(dataframe)
    with st.container(border=True):
        st.dataframe(mv.style.format({"Missing (%)": "{:.2f}%"}), hide_index=True, width="stretch")

    st.divider()

    # Numeric distribution
    st.subheader("Feature distribution")
    if profile.numeric_columns:
        sel = st.selectbox("Select feature", profile.numeric_columns, key="loan_xai_numeric_feature")
        vals = numeric_feature(dataframe, sel)
        fig = px.histogram(x=vals, nbins=40, color_discrete_sequence=[CHART_COLOR], labels={"x": sel})
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Correlation
    st.subheader("Correlation matrix")
    corr = correlation_matrix(dataframe)
    if len(corr.columns) >= 2:
        fig = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale="Purples", zmin=-1, zmax=1, colorbar={"title": "r"},
            hovertemplate="%{y} × %{x}<br>%{z:.3f}<extra></extra>",
        ))
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Download
    st.subheader("Dataset preview & download")
    meta = st.session_state.get(DATASET_METADATA_SESSION_KEY, {})
    c1, c2 = st.columns([1, 2])
    with c1:
        n = st.selectbox("Rows", PREVIEW_ROW_OPTIONS, key="loan_xai_preview_rows")
    with c2:
        st.write("")
        st.download_button("Download CSV", data=dataframe_to_csv(dataframe),
                           file_name=str(meta.get("filename", "data.csv")), mime="text/csv")
    with st.container(border=True):
        st.dataframe(dataframe.head(n), hide_index=True, width="stretch")
    render_api_reference("loan_xai", "explore")
