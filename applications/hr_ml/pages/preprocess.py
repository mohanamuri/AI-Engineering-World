import streamlit as st

from applications.hr_ml.constants import (
    PREPROCESS_RESULT_SESSION_KEY,
    PREPROCESS_CONFIG_SESSION_KEY,
    TARGET_COLUMN,
    RECOMMENDED_DROP_COLUMNS,
)
from applications.hr_ml.services.data_loader import DATAFRAME_SESSION_KEY
from applications.hr_ml.services.preprocessor import (
    PreprocessConfig,
    PreprocessingError,
    preprocess,
)


def render():
    st.header("🧹 Preprocess")

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    if dataframe is None:
        st.warning("Upload a dataset first.")
        return

    st.info(
        "The pipeline fits on training data only — no data leakage. "
        "**Recommended:** keep default settings for the HR Attrition dataset."
    )

    with st.form("hr_ml_preprocess_form"):
        st.subheader("Configuration")

        available_cols = list(dataframe.columns)

        target_col = st.selectbox(
            "Target column",
            available_cols,
            index=available_cols.index(TARGET_COLUMN) if TARGET_COLUMN in available_cols else 0,
            help="The column to predict. For IBM HR dataset, this is 'Attrition'.",
        )

        default_drops = [c for c in RECOMMENDED_DROP_COLUMNS if c in available_cols]
        drop_cols = st.multiselect(
            "Columns to drop",
            [c for c in available_cols if c != target_col],
            default=default_drops,
            help="EmployeeCount, Over18, StandardHours are constant — no predictive value. EmployeeNumber is an ID.",
        )

        col1, col2 = st.columns(2)
        with col1:
            scaling = st.selectbox("Scaling", ["standard", "minmax", "none"], index=0)
            encoding = st.selectbox("Categorical encoding", ["ordinal", "onehot"], index=0)
        with col2:
            test_size = st.slider("Test set size", 0.1, 0.4, 0.2, 0.05)
            num_impute = st.selectbox("Numeric imputation", ["median", "mean", "most_frequent"], index=0)

        submitted = st.form_submit_button("Run Preprocessing", use_container_width=True)

    if submitted:
        config = PreprocessConfig(
            target_column=target_col,
            scaling_strategy=scaling,
            encoding_strategy=encoding,
            drop_columns=tuple(drop_cols),
            test_size=test_size,
            numeric_impute_strategy=num_impute,
        )
        with st.spinner("Preprocessing…"):
            try:
                result = preprocess(dataframe, config)
            except PreprocessingError as exc:
                st.error(f"Preprocessing failed: {exc}")
                return

        st.session_state[PREPROCESS_RESULT_SESSION_KEY] = result
        st.session_state[PREPROCESS_CONFIG_SESSION_KEY] = config
        st.success("Preprocessing complete.")

    result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if result is None:
        st.caption("Run preprocessing to see the output.")
        return

    st.subheader("Output")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Train rows", f"{len(result.X_train):,}")
    c2.metric("Test rows", f"{len(result.X_test):,}")
    c3.metric("Features", f"{len(result.feature_names):,}")
    c4.metric("Classes", str(list(result.class_labels)))

    # Class balance in train set
    train_counts = result.y_train.value_counts()
    st.markdown("**Train set class distribution:**")
    st.dataframe(
        train_counts.reset_index().rename(columns={"index": "Attrition", "count": "Count"}),
        use_container_width=False,
        hide_index=True,
    )

    with st.expander("Feature names after encoding"):
        st.write(result.feature_names)

    with st.expander("Sample transformed train rows"):
        st.dataframe(result.X_train.head(5), use_container_width=True, hide_index=True)
