"""Dataset exploration dashboard for the loan eligibility DL pipeline.

Reuses the loan_ml exploration service directly — the service is pure Python
and dataset-agnostic. Widget keys are prefixed loan_dl_ to avoid conflicts
when both apps are open in the same session.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from applications.loan_dl.constants import (
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


PREVIEW_ROW_OPTIONS = (10, 25, 50, 100)
CHART_COLOR = "#0891b2"
HEATMAP_COLORS = "Blues"


def render() -> None:
    st.header("📊 Explore Dataset")
    st.caption(
        "Inspect data quality, feature distributions, and relationships before "
        "building the preprocessing pipeline."
    )

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    if not isinstance(dataframe, pd.DataFrame):
        _render_empty_state()
        return

    profile = profile_dataset(dataframe)
    _render_dataset_summary(profile)
    st.divider()
    _render_data_types(profile)
    st.divider()
    _render_statistical_summary(dataframe)
    st.divider()
    _render_missing_values(dataframe, profile)
    st.divider()
    _render_target_distribution(dataframe)
    st.divider()
    _render_numeric_distribution(dataframe, profile)
    st.divider()
    _render_correlation_matrix(dataframe)
    st.divider()
    _render_preview_and_download(dataframe)
    render_api_reference("loan_dl", "explore")


def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("No dataset uploaded.")
        st.write("Upload and validate a CSV dataset before opening the exploration dashboard.")
        st.button(
            "← Go to Upload Dataset",
            type="primary",
            on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: UPLOAD_PAGE_LABEL}),
        )


def _render_dataset_summary(profile: DatasetProfile) -> None:
    st.subheader("Dataset summary")
    metrics = (
        ("Rows", f"{profile.rows:,}", "Records available"),
        ("Columns", f"{profile.columns:,}", "Dataset features"),
        ("Missing values", f"{profile.missing_values:,}", "Empty cells"),
        ("Duplicate rows", f"{profile.duplicate_rows:,}", "Repeated records"),
        ("Memory usage", format_bytes(profile.memory_bytes), "In-memory size"),
    )
    for column, (label, value, help_text) in zip(st.columns(len(metrics)), metrics, strict=True):
        with column:
            with st.container(border=True):
                st.metric(label, value, help=help_text)


def _render_data_types(profile: DatasetProfile) -> None:
    st.subheader("Data types")
    numeric_container, categorical_container = st.columns(2)
    with numeric_container:
        with st.container(border=True):
            st.markdown("#### Numeric columns")
            st.caption(f"{len(profile.numeric_columns):,} detected")
            _render_column_list(profile.numeric_columns)
    with categorical_container:
        with st.container(border=True):
            st.markdown("#### Categorical columns")
            st.caption(f"{len(profile.categorical_columns):,} detected")
            _render_column_list(profile.categorical_columns)


def _render_column_list(columns: tuple[str, ...]) -> None:
    if columns:
        st.write(" · ".join(f"`{c}`" for c in columns))
    else:
        st.caption("None detected")


def _render_statistical_summary(dataframe: pd.DataFrame) -> None:
    st.subheader("Statistical summary")
    include_categorical = st.checkbox(
        "Include categorical columns",
        value=False,
        key="loan_dl_include_categorical_summary",
    )
    summary = statistical_summary(dataframe, include_categorical=include_categorical)
    if summary.empty:
        st.info("No numeric columns are available for statistical analysis.")
        return
    with st.container(border=True):
        st.dataframe(summary, width="stretch")


def _render_missing_values(dataframe: pd.DataFrame, profile: DatasetProfile) -> None:
    st.subheader("Missing value analysis")
    missing_summary = missing_value_summary(dataframe)
    total_column, detail_column = st.columns([1, 4])
    with total_column:
        with st.container(border=True):
            st.metric("Total missing", f"{profile.missing_values:,}")
            populated_cells = profile.rows * profile.columns
            missing_rate = profile.missing_values / populated_cells * 100 if populated_cells else 0
            st.caption(f"{missing_rate:.2f}% of all cells")
    with detail_column:
        styled = missing_summary.style.apply(_highlight_missing_row, axis=1).format({"Missing (%)": "{:.2f}%"})
        st.dataframe(styled, width="stretch", hide_index=True)


def _highlight_missing_row(row: pd.Series) -> list[str]:
    style = "background-color: rgba(239, 68, 68, 0.14);" if int(row["Missing Values"]) > 0 else ""
    return [style] * len(row)


def _render_target_distribution(dataframe: pd.DataFrame) -> None:
    st.subheader("Target distribution")
    target_column = detect_target_column(dataframe)
    if target_column is None:
        st.info("No recognized target column was detected. Expected a column such as `LoanApproved` or `Loan_Status`.")
        return
    distribution = target_distribution(dataframe, target_column)
    st.caption(f"Detected target: `{target_column}`")
    counts_column, chart_column = st.columns([1, 2])
    with counts_column:
        with st.container(border=True):
            st.markdown("#### Value counts")
            st.dataframe(distribution, width="stretch", hide_index=True)
    with chart_column:
        figure = px.bar(distribution, x="Value", y="Count", color_discrete_sequence=[CHART_COLOR], text_auto=True)
        figure.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False, xaxis_title=target_column)
        st.plotly_chart(figure, width="stretch")


def _render_numeric_distribution(dataframe: pd.DataFrame, profile: DatasetProfile) -> None:
    st.subheader("Numeric feature distribution")
    if not profile.numeric_columns:
        st.info("No numeric columns are available for distribution analysis.")
        return
    selected_column = st.selectbox("Select numeric feature", options=profile.numeric_columns, key="loan_dl_numeric_feature")
    values = numeric_feature(dataframe, selected_column)
    if values.empty:
        st.info(f"`{selected_column}` contains no populated numeric values.")
        return
    figure = px.histogram(
        x=values,
        nbins=min(40, max(10, int(len(values) ** 0.5))),
        color_discrete_sequence=[CHART_COLOR],
        labels={"x": selected_column, "count": "Frequency"},
    )
    figure.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False, yaxis_title="Frequency")
    st.plotly_chart(figure, width="stretch")


def _render_correlation_matrix(dataframe: pd.DataFrame) -> None:
    st.subheader("Correlation matrix")
    correlations = correlation_matrix(dataframe)
    if len(correlations.columns) < 2:
        st.info("At least two numeric columns are required for correlation analysis.")
        return
    figure = go.Figure(data=go.Heatmap(
        z=correlations.values, x=correlations.columns, y=correlations.index,
        colorscale=HEATMAP_COLORS, zmin=-1, zmax=1,
        colorbar={"title": "Correlation"},
        hovertemplate="%{y} × %{x}<br>%{z:.3f}<extra></extra>",
    ))
    figure.update_layout(margin=dict(l=10, r=10, t=20, b=10), xaxis_side="bottom")
    st.plotly_chart(figure, width="stretch")


def _render_preview_and_download(dataframe: pd.DataFrame) -> None:
    st.subheader("Dataset preview")
    controls_column, download_column = st.columns([1, 2])
    with controls_column:
        preview_rows = st.selectbox("Rows to display", options=PREVIEW_ROW_OPTIONS, index=0, key="loan_dl_preview_rows")
    metadata = st.session_state.get(DATASET_METADATA_SESSION_KEY, {})
    filename = str(metadata.get("filename", "loan_dataset.csv"))
    with download_column:
        st.write("")
        st.download_button(
            "Download current dataset",
            data=dataframe_to_csv(dataframe),
            file_name=filename,
            mime="text/csv",
            width="stretch",
        )
    with st.container(border=True):
        st.dataframe(dataframe.head(preview_rows), width="stretch", hide_index=True)
        st.caption(f"Showing {min(preview_rows, len(dataframe)):,} of {len(dataframe):,} rows.")
