from pathlib import Path

import streamlit as st

from components.tier_guide import render_tier_guide
from applications.hr_xai.services.data_loader import (
    DATAFRAME_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY, MAX_UPLOAD_BYTES,
    DatasetValidationError, load_csv,
)
from applications.shared.api_reference import render_api_reference

PREVIEW_ROWS = 10
_SAMPLE_PATH = Path(__file__).resolve().parents[3] / "data" / "hr_attrition_sample.csv"


def render():
    st.header("📤 Upload Dataset")
    render_tier_guide("hr_xai")

    col_sample, col_upload = st.columns(2)

    with col_sample:
        with st.container(border=True):
            st.markdown("#### Use sample dataset")
            st.caption("hr_attrition_sample.csv · 400 rows · 29 columns")
            st.caption("After training, SHAP explains why each employee is flagged.")
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
                label_visibility="collapsed", key="hr_xai_uploader",
            )
            if uploaded_file is not None:
                _process_upload(uploaded_file.name, uploaded_file.getvalue())

    df = st.session_state.get(DATAFRAME_SESSION_KEY)
    if df is not None:
        c1, c2 = st.columns(2)
        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", f"{len(df.columns):,}")
        st.dataframe(df.head(PREVIEW_ROWS), use_container_width=True, hide_index=True)
    else:
        st.caption("No dataset loaded.")

    render_api_reference("hr_xai", "upload")


def _process_upload(filename: str, content: bytes) -> None:
    try:
        ds = load_csv(filename, content)
    except DatasetValidationError as exc:
        st.error(str(exc))
        return

    if ds.fingerprint != st.session_state.get(DATASET_FINGERPRINT_SESSION_KEY):
        st.session_state[DATAFRAME_SESSION_KEY] = ds.dataframe
        st.session_state[DATASET_METADATA_SESSION_KEY] = ds.metadata
        st.session_state[DATASET_FINGERPRINT_SESSION_KEY] = ds.fingerprint

    st.success(f"Loaded **{ds.filename}** — {len(ds.dataframe):,} rows · {len(ds.dataframe.columns):,} columns.")
