import streamlit as st
from components.tier_guide import render_tier_guide
from applications.hr_xai.services.data_loader import (
    DATAFRAME_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY, MAX_UPLOAD_BYTES,
    DatasetValidationError, load_csv,
)


def render():
    st.header("📤 Upload Dataset")
    render_tier_guide("hr_xai")
    st.info(
        "Upload the IBM HR Attrition dataset. "
        "After training, SHAP will explain *why* each employee is flagged as a flight risk."
    )
    f = st.file_uploader("Choose CSV File", type=["csv"], key="hr_xai_uploader",
                          help=f"Max {MAX_UPLOAD_BYTES // (1024*1024)} MB.")
    if f:
        try:
            ds = load_csv(f.name, f.getvalue())
        except DatasetValidationError as exc:
            st.error(str(exc))
            return
        if ds.fingerprint != st.session_state.get(DATASET_FINGERPRINT_SESSION_KEY):
            st.session_state[DATAFRAME_SESSION_KEY] = ds.dataframe
            st.session_state[DATASET_METADATA_SESSION_KEY] = ds.metadata
            st.session_state[DATASET_FINGERPRINT_SESSION_KEY] = ds.fingerprint
        st.success(f"Loaded **{ds.filename}** — {len(ds.dataframe):,} rows.")

    df = st.session_state.get(DATAFRAME_SESSION_KEY)
    if df is not None:
        c1, c2 = st.columns(2)
        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", f"{len(df.columns):,}")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    else:
        st.caption("No dataset loaded.")
