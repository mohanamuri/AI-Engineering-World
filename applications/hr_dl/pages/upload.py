from pathlib import Path

import streamlit as st

from components.tier_guide import render_tier_guide
from applications.hr_dl.services.data_loader import (
    DATAFRAME_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY, MAX_UPLOAD_BYTES,
    DatasetValidationError, LoadedDataset, load_csv,
)
from applications.shared.api_reference import render_api_reference

PREVIEW_ROWS = 10
_SAMPLE_PATH = Path(__file__).resolve().parents[3] / "data" / "hr_attrition_sample.csv"


def render():
    st.header("📤 Upload Dataset")
    render_tier_guide("hr_dl")

    col_sample, col_upload = st.columns(2)

    with col_sample:
        with st.container(border=True):
            st.markdown("#### Use sample dataset")
            st.caption("hr_attrition_sample.csv · 400 rows · 29 columns")
            st.caption("Same dataset as T1 — compare ML vs DL results directly.")
            if _SAMPLE_PATH.exists():
                if st.button("Load sample dataset", use_container_width=True, type="primary"):
                    _process_upload("hr_attrition_sample.csv", _SAMPLE_PATH.read_bytes())
            else:
                st.warning("Sample file not found in data/.")

    with col_upload:
        with st.container(border=True):
            st.markdown("#### Upload your own")
            st.caption(f"Supported: CSV · Max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
            uploaded_file = st.file_uploader(
                "Choose CSV File", type=["csv"], accept_multiple_files=False,
                label_visibility="collapsed", key="hr_dl_csv_uploader",
            )
            if uploaded_file is not None:
                _process_upload(uploaded_file.name, uploaded_file.getvalue())

    df = st.session_state.get(DATAFRAME_SESSION_KEY)
    meta = st.session_state.get(DATASET_METADATA_SESSION_KEY)

    if df is not None and meta is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{meta['rows']:,}")
        c2.metric("Columns", f"{meta['columns']:,}")
        if "Attrition" in df.columns:
            counts = df["Attrition"].value_counts()
            c3.metric("Attrition rate", f"{counts.get('Yes', 0) / len(df):.1%}")
        st.markdown(f"**Source:** `{meta['filename']}`")
        st.dataframe(df.head(PREVIEW_ROWS), use_container_width=True, hide_index=True)
    else:
        st.caption("No dataset loaded.")

    render_api_reference("hr_dl", "upload")


def _process_upload(filename: str, content: bytes) -> None:
    try:
        dataset = load_csv(filename, content)
    except DatasetValidationError as exc:
        for k in (DATAFRAME_SESSION_KEY, DATASET_METADATA_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY):
            st.session_state.pop(k, None)
        st.error(f"Unable to load: {exc}")
        return

    if dataset.fingerprint != st.session_state.get(DATASET_FINGERPRINT_SESSION_KEY):
        st.session_state[DATAFRAME_SESSION_KEY] = dataset.dataframe
        st.session_state[DATASET_METADATA_SESSION_KEY] = dataset.metadata
        st.session_state[DATASET_FINGERPRINT_SESSION_KEY] = dataset.fingerprint

    st.success(
        f"Loaded **{dataset.filename}** — "
        f"{len(dataset.dataframe):,} rows · {len(dataset.dataframe.columns):,} columns."
    )
