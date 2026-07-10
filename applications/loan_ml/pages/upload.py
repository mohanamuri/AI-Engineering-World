from pathlib import Path

import streamlit as st

from components.tier_guide import render_tier_guide
from applications.loan_ml.services.data_loader import (
    DATAFRAME_SESSION_KEY,
    DATASET_FINGERPRINT_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY,
    MAX_UPLOAD_BYTES,
    DatasetValidationError,
    LoadedDataset,
    load_csv,
)
from applications.loan_ml.utils.helpers import format_bytes
from applications.loan_ml.utils.api_reference import render_api_reference

PREVIEW_ROWS = 10
_SAMPLE_PATH = Path(__file__).resolve().parents[3] / "data" / "loan_docs" / "loan_eligibility_sample.csv"


def render():
    st.header("📤 Upload Dataset")
    render_tier_guide("loan_ml")

    col_sample, col_upload = st.columns(2)

    with col_sample:
        with st.container(border=True):
            st.markdown("#### Use sample dataset")
            st.caption("loan_eligibility_sample.csv · 500 rows · 13 columns")
            st.caption("Age, Income, LoanAmount, CreditScore, EmploymentStatus …")
            if _SAMPLE_PATH.exists():
                if st.button("Load sample dataset", use_container_width=True, type="primary"):
                    _process_upload("loan_eligibility_sample.csv", _SAMPLE_PATH.read_bytes())
            else:
                st.warning("Sample file not found in data/.")

    with col_upload:
        with st.container(border=True):
            st.markdown("#### Upload your own")
            st.caption(f"Supported: CSV · Max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
            uploaded_file = st.file_uploader(
                "Choose CSV File", type=["csv"], accept_multiple_files=False,
                label_visibility="collapsed", key="loan_ml_csv_uploader",
            )
            if uploaded_file is not None:
                _process_upload(uploaded_file.name, uploaded_file.getvalue())

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    metadata = st.session_state.get(DATASET_METADATA_SESSION_KEY)

    if dataframe is not None and metadata is not None:
        _render_dataset_summary(dataframe, metadata)
    else:
        st.caption("No validated dataset is currently loaded.")

    render_api_reference("upload")


def _process_upload(filename: str, content: bytes) -> None:
    try:
        dataset = load_csv(filename, content)
    except DatasetValidationError as exc:
        _clear_dataset()
        st.error(f"Unable to load dataset: {exc}")
        return

    if dataset.fingerprint != st.session_state.get(DATASET_FINGERPRINT_SESSION_KEY):
        _store_dataset(dataset)

    st.success(
        f"Loaded **{dataset.filename}** — "
        f"{len(dataset.dataframe):,} rows · {len(dataset.dataframe.columns):,} columns."
    )


def _store_dataset(dataset: LoadedDataset) -> None:
    st.session_state[DATAFRAME_SESSION_KEY] = dataset.dataframe
    st.session_state[DATASET_METADATA_SESSION_KEY] = dataset.metadata
    st.session_state[DATASET_FINGERPRINT_SESSION_KEY] = dataset.fingerprint


def _clear_dataset() -> None:
    for key in (DATAFRAME_SESSION_KEY, DATASET_METADATA_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY):
        st.session_state.pop(key, None)


def _render_dataset_summary(dataframe, metadata: dict) -> None:
    st.subheader("Dataset overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{metadata['rows']:,}")
    c2.metric("Columns", f"{metadata['columns']:,}")
    c3.metric("File size", format_bytes(int(metadata["size_bytes"])))
    st.markdown(f"**Source:** `{metadata['filename']}`")
    st.markdown(f"**Preview:** first {min(PREVIEW_ROWS, len(dataframe)):,} rows")
    st.dataframe(dataframe.head(PREVIEW_ROWS), use_container_width=True, hide_index=True)
