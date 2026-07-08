"""Preprocess page for the loan eligibility XAI pipeline.
Reuses loan_ml preprocessor service with loan_xai session keys.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from applications.loan_xai.constants import (
    DATAFRAME_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_CONFIG_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    UPLOAD_PAGE_LABEL,
)
from applications.loan_ml.services.exploration import detect_target_column
from applications.loan_ml.services.preprocessor import (
    PreprocessConfig,
    PreprocessResult,
    PreprocessingError,
    preprocess,
)
from applications.shared.api_reference import render_api_reference

CHART_COLOR = "#7c3aed"


def render() -> None:
    st.header("🧹 Preprocess Dataset")
    st.caption("Build the feature engineering pipeline before training the explainable model.")

    dataframe: pd.DataFrame | None = st.session_state.get(DATAFRAME_SESSION_KEY)
    if not isinstance(dataframe, pd.DataFrame):
        with st.container(border=True):
            st.warning("No dataset loaded.")
            st.button("← Go to Upload Dataset", type="primary",
                      on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: UPLOAD_PAGE_LABEL}))
        return

    config = _render_config(dataframe)
    st.divider()

    if st.button("Run Preprocessing", type="primary", use_container_width=True):
        with st.spinner("Building pipeline…"):
            try:
                result = preprocess(dataframe, config)
            except PreprocessingError as exc:
                st.error(f"Preprocessing failed: {exc}")
                return
        st.session_state[PREPROCESS_RESULT_SESSION_KEY] = result
        st.session_state[PREPROCESS_CONFIG_SESSION_KEY] = config
        st.success(
            f"Pipeline fitted — Train: **{len(result.X_train):,}** · "
            f"Test: **{len(result.X_test):,}** · Features: **{len(result.feature_names):,}**"
        )

    result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if result is not None:
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Train rows", f"{len(result.X_train):,}")
        m2.metric("Test rows", f"{len(result.X_test):,}")
        m3.metric("Features", f"{len(result.feature_names):,}")
        m4.metric("Classes", str(len(result.class_labels)))

        train_counts = result.y_train.astype(str).value_counts().rename_axis("Class").reset_index(name="Count")
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.container(border=True):
                st.dataframe(train_counts, hide_index=True)
        with c2:
            fig = px.bar(train_counts, x="Class", y="Count", color_discrete_sequence=[CHART_COLOR], text_auto=True)
            fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.info("Pipeline ready. Proceed to **Train Model** to fit a classifier.", icon="✅")
    render_api_reference("loan_xai", "preprocess")


def _render_config(dataframe: pd.DataFrame) -> PreprocessConfig:
    cols = list(dataframe.columns)
    detected = detect_target_column(dataframe)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### Target column")
            target = st.selectbox("Target", cols,
                                  index=cols.index(detected) if detected in cols else 0,
                                  label_visibility="collapsed", key="loan_xai_target")
    with c2:
        with st.container(border=True):
            st.markdown("#### Columns to drop")
            drop = st.multiselect("Drop", [c for c in cols if c != target],
                                  default=[], label_visibility="collapsed", key="loan_xai_drop")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("**Numeric imputation**")
            num_imp = st.radio("Numeric impute", ["median", "mean", "constant"], index=0,
                               label_visibility="collapsed", key="loan_xai_num_impute")
    with c2:
        with st.container(border=True):
            st.markdown("**Categorical imputation**")
            cat_imp = st.radio("Cat impute", ["most_frequent", "constant"], index=0,
                               label_visibility="collapsed", key="loan_xai_cat_impute")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("**Scaling**")
            scaling = st.radio("Scale", ["standard", "minmax", "none"], index=0,
                               label_visibility="collapsed", key="loan_xai_scaling")
    with c2:
        with st.container(border=True):
            st.markdown("**Encoding**")
            encoding = st.radio("Encode", ["ordinal", "onehot"], index=0,
                                label_visibility="collapsed", key="loan_xai_encoding",
                                help="Ordinal is recommended for tree models used in SHAP TreeExplainer.")

    return PreprocessConfig(
        target_column=target,
        numeric_impute_strategy=num_imp,        # type: ignore[arg-type]
        categorical_impute_strategy=cat_imp,    # type: ignore[arg-type]
        scaling_strategy=scaling,               # type: ignore[arg-type]
        encoding_strategy=encoding,             # type: ignore[arg-type]
        drop_columns=tuple(drop),
    )
