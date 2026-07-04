import streamlit as st
from components.tier_guide import render_tier_guide
from applications.hr_dl.services.data_loader import (
    DATAFRAME_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY, MAX_UPLOAD_BYTES,
    DatasetValidationError, LoadedDataset, load_csv,
)


def render():
    st.header("📤 Upload Dataset")
    render_tier_guide("hr_dl")
    st.info(
        "Upload an HR Attrition dataset (CSV). "
        "Same dataset as T1, now used to train a neural network."
    )
    uploaded_file = st.file_uploader(
        "Choose CSV File", type=["csv"], accept_multiple_files=False,
        help=f"Maximum {MAX_UPLOAD_BYTES // (1024*1024)} MB.",
        key="hr_dl_csv_uploader",
    )
    if uploaded_file is not None:
        try:
            dataset = load_csv(uploaded_file.name, uploaded_file.getvalue())
        except DatasetValidationError as exc:
            for k in (DATAFRAME_SESSION_KEY, DATASET_METADATA_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY):
                st.session_state.pop(k, None)
            st.error(f"Unable to load: {exc}")
            return
        if dataset.fingerprint != st.session_state.get(DATASET_FINGERPRINT_SESSION_KEY):
            st.session_state[DATAFRAME_SESSION_KEY] = dataset.dataframe
            st.session_state[DATASET_METADATA_SESSION_KEY] = dataset.metadata
            st.session_state[DATASET_FINGERPRINT_SESSION_KEY] = dataset.fingerprint
        st.success(f"Loaded **{dataset.filename}** — {len(dataset.dataframe):,} rows, {len(dataset.dataframe.columns):,} columns.")

    df = st.session_state.get(DATAFRAME_SESSION_KEY)
    meta = st.session_state.get(DATASET_METADATA_SESSION_KEY)
    if df is not None and meta is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{meta['rows']:,}")
        c2.metric("Columns", f"{meta['columns']:,}")
        if "Attrition" in df.columns:
            counts = df["Attrition"].value_counts()
            c3.metric("Attrition rate", f"{counts.get('Yes', 0) / len(df):.1%}")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    else:
        st.caption("No dataset loaded.")
