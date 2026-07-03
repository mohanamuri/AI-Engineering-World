"""Preprocessing configuration page for the loan eligibility ML pipeline.

The user selects a target column, columns to drop, and imputation/scaling/
encoding strategies. On submit the preprocessor service builds a fitted
sklearn Pipeline and stores train/test splits in session state.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from applications.loan_ml.constants import (
    NAVIGATION_SESSION_KEY,
    PREPROCESS_CONFIG_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.loan_ml.services.data_loader import DATAFRAME_SESSION_KEY
from applications.loan_ml.services.exploration import detect_target_column
from applications.loan_ml.services.preprocessor import (
    PreprocessConfig,
    PreprocessResult,
    PreprocessingError,
    preprocess,
)

CHART_COLOR = "#2563EB"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    st.header("🧹 Preprocess Dataset")
    st.caption(
        "Configure the preprocessing pipeline: target selection, imputation, "
        "scaling, and encoding. The fitted pipeline is packaged with the model "
        "at export time to prevent training-serving skew."
    )

    dataframe: pd.DataFrame | None = st.session_state.get(DATAFRAME_SESSION_KEY)
    if not isinstance(dataframe, pd.DataFrame):
        _render_empty_state()
        return

    config = _render_config_panel(dataframe)

    st.divider()

    if st.button("Run Preprocessing", type="primary", use_container_width=True):
        _run_preprocessing(dataframe, config)

    result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if result is not None:
        st.divider()
        _render_results(result)


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("No dataset loaded.")
        st.write("Upload and validate a CSV dataset before configuring the preprocessing pipeline.")
        st.button(
            "← Go to Upload Dataset",
            type="primary",
            on_click=_navigate_to_upload,
        )


def _navigate_to_upload() -> None:
    st.session_state[NAVIGATION_SESSION_KEY] = UPLOAD_PAGE_LABEL


# ---------------------------------------------------------------------------
# Configuration panel
# ---------------------------------------------------------------------------

def _render_config_panel(dataframe: pd.DataFrame) -> PreprocessConfig:
    all_columns = list(dataframe.columns)
    detected_target = detect_target_column(dataframe)

    st.subheader("Pipeline configuration")

    col_target, col_drop = st.columns(2)

    with col_target:
        with st.container(border=True):
            st.markdown("#### Target column")
            st.caption("The column your model will learn to predict.")
            target_column = st.selectbox(
                "Target column",
                options=all_columns,
                index=all_columns.index(detected_target) if detected_target in all_columns else 0,
                label_visibility="collapsed",
                key="loan_ml_preprocess_target",
            )

    with col_drop:
        with st.container(border=True):
            st.markdown("#### Columns to drop")
            st.caption("Remove ID columns or features that would leak the target.")
            drop_columns = st.multiselect(
                "Columns to drop",
                options=[c for c in all_columns if c != target_column],
                default=[],
                label_visibility="collapsed",
                key="loan_ml_preprocess_drop",
            )

    st.markdown("#### Imputation strategy")
    impute_col_num, impute_col_cat = st.columns(2)

    with impute_col_num:
        with st.container(border=True):
            st.markdown("**Numeric columns**")
            numeric_impute = st.radio(
                "Numeric imputation",
                options=["median", "mean", "constant"],
                index=0,
                label_visibility="collapsed",
                key="loan_ml_impute_numeric",
                help="Median is robust to outliers. Mean is sensitive to them.",
            )

    with impute_col_cat:
        with st.container(border=True):
            st.markdown("**Categorical columns**")
            categorical_impute = st.radio(
                "Categorical imputation",
                options=["most_frequent", "constant"],
                index=0,
                label_visibility="collapsed",
                key="loan_ml_impute_categorical",
                help="Most frequent fills gaps with the mode value.",
            )

    st.markdown("#### Scaling & encoding")
    scale_col, encode_col = st.columns(2)

    with scale_col:
        with st.container(border=True):
            st.markdown("**Numeric scaling**")
            scaling = st.radio(
                "Scaling",
                options=["standard", "minmax", "none"],
                index=0,
                label_visibility="collapsed",
                key="loan_ml_scaling",
                help=(
                    "Standard: zero mean, unit variance. "
                    "MinMax: scales to [0, 1]. "
                    "None: pass raw values."
                ),
            )

    with encode_col:
        with st.container(border=True):
            st.markdown("**Categorical encoding**")
            encoding = st.radio(
                "Encoding",
                options=["ordinal", "onehot"],
                index=0,
                label_visibility="collapsed",
                key="loan_ml_encoding",
                help=(
                    "Ordinal: assigns an integer per category — compact, tree-friendly. "
                    "OneHot: creates a binary column per category — required for linear models."
                ),
            )

    return PreprocessConfig(
        target_column=target_column,
        numeric_impute_strategy=numeric_impute,          # type: ignore[arg-type]
        categorical_impute_strategy=categorical_impute,  # type: ignore[arg-type]
        scaling_strategy=scaling,                        # type: ignore[arg-type]
        encoding_strategy=encoding,                      # type: ignore[arg-type]
        drop_columns=tuple(drop_columns),
    )


# ---------------------------------------------------------------------------
# Run & store
# ---------------------------------------------------------------------------

def _run_preprocessing(dataframe: pd.DataFrame, config: PreprocessConfig) -> None:
    with st.spinner("Building preprocessing pipeline…"):
        try:
            result = preprocess(dataframe, config)
        except PreprocessingError as exc:
            st.error(f"Preprocessing failed: {exc}")
            return

    st.session_state[PREPROCESS_RESULT_SESSION_KEY] = result
    st.session_state[PREPROCESS_CONFIG_SESSION_KEY] = config
    st.success(
        f"Pipeline fitted successfully. "
        f"Train: **{len(result.X_train):,} rows** · "
        f"Test: **{len(result.X_test):,} rows** · "
        f"Features: **{len(result.feature_names):,}**"
    )


# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------

def _render_results(result: PreprocessResult) -> None:
    st.subheader("Preprocessing results")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Train rows", f"{len(result.X_train):,}")
    m2.metric("Test rows", f"{len(result.X_test):,}")
    m3.metric("Features", f"{len(result.feature_names):,}")
    m4.metric("Classes", str(len(result.class_labels)))

    st.divider()

    st.markdown("#### Target distribution — train split")
    train_counts = (
        result.y_train
        .astype(str)
        .value_counts()
        .rename_axis("Class")
        .reset_index(name="Count")
    )

    dist_table, dist_chart = st.columns([1, 2])
    with dist_table:
        with st.container(border=True):
            st.dataframe(train_counts, hide_index=True, width="stretch")

    with dist_chart:
        figure = px.bar(
            train_counts,
            x="Class",
            y="Count",
            color_discrete_sequence=[CHART_COLOR],
            text_auto=True,
        )
        figure.update_layout(
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
        )
        st.plotly_chart(figure, use_container_width=True)

    st.divider()

    st.markdown("#### Output feature names")
    st.caption(f"{len(result.feature_names)} features after encoding")
    with st.container(border=True):
        st.write(" · ".join(f"`{f}`" for f in result.feature_names))

    st.info(
        "The preprocessing pipeline is fitted. "
        "Proceed to **Train Model** to select and train a classifier.",
        icon="✅",
    )
