import streamlit as st
from applications.hr_dl.constants import (
    PREPROCESS_RESULT_SESSION_KEY, PREPROCESS_CONFIG_SESSION_KEY,
    TARGET_COLUMN, RECOMMENDED_DROP_COLUMNS,
)
from applications.hr_dl.services.data_loader import DATAFRAME_SESSION_KEY
from applications.hr_ml.services.preprocessor import PreprocessConfig, PreprocessingError, preprocess
from applications.shared.api_reference import render_api_reference


def render():
    st.header("🧹 Preprocess")
    df = st.session_state.get(DATAFRAME_SESSION_KEY)
    if df is None:
        st.warning("Upload a dataset first.")
        return

    st.info("Pipeline fits on training data only. Neural networks need StandardScaler — keep the default.")

    with st.form("hr_dl_preprocess_form"):
        available = list(df.columns)
        target_col = st.selectbox("Target column", available,
                                  index=available.index(TARGET_COLUMN) if TARGET_COLUMN in available else 0)
        default_drops = [c for c in RECOMMENDED_DROP_COLUMNS if c in available]
        drop_cols = st.multiselect("Columns to drop", [c for c in available if c != target_col], default=default_drops)

        col1, col2 = st.columns(2)
        with col1:
            scaling = st.selectbox("Scaling", ["standard", "minmax", "none"], index=0,
                                   help="StandardScaler is recommended for neural networks.")
            encoding = st.selectbox("Categorical encoding", ["ordinal", "onehot"], index=0)
        with col2:
            test_size = st.slider("Test set size", 0.1, 0.4, 0.2, 0.05)

        submitted = st.form_submit_button("Run Preprocessing", use_container_width=True)

    if submitted:
        config = PreprocessConfig(
            target_column=target_col, scaling_strategy=scaling,
            encoding_strategy=encoding, drop_columns=tuple(drop_cols),
            test_size=test_size,
        )
        with st.spinner("Preprocessing…"):
            try:
                result = preprocess(df, config)
            except PreprocessingError as exc:
                st.error(f"Preprocessing failed: {exc}")
                return
        st.session_state[PREPROCESS_RESULT_SESSION_KEY] = result
        st.session_state[PREPROCESS_CONFIG_SESSION_KEY] = config
        st.success("Preprocessing complete.")

    result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if result is None:
        st.caption("Run preprocessing to see output.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Train rows", f"{len(result.X_train):,}")
    c2.metric("Test rows", f"{len(result.X_test):,}")
    c3.metric("Features", f"{len(result.feature_names):,}")
    c4.metric("Classes", str(list(result.class_labels)))
    render_api_reference("hr_dl", "preprocess")
