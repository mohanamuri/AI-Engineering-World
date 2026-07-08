"""Upload page for the loan eligibility XAI pipeline."""

import streamlit as st

from components.tier_guide import render_tier_guide
from applications.loan_xai.constants import (
    DATAFRAME_SESSION_KEY,
    DATASET_FINGERPRINT_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY,
)
from applications.loan_ml.services.data_loader import (
    MAX_UPLOAD_BYTES,
    DatasetValidationError,
    LoadedDataset,
    load_csv,
)
from applications.loan_ml.utils.helpers import format_bytes
from applications.shared.api_reference import render_api_reference

PREVIEW_ROWS = 10


def render() -> None:
    st.header("📤 Upload Dataset")
    render_tier_guide("loan_xai")
    st.info(
        "Upload a UTF-8 CSV dataset to begin the explainability workflow. "
        "The same dataset used in loan_ml/loan_dl works here directly."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"],
        accept_multiple_files=False,
        help=f"Maximum size: {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        key="loan_xai_csv_uploader",
    )

    if uploaded_file is not None:
        _process_upload(uploaded_file.name, uploaded_file.getvalue())

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    metadata = st.session_state.get(DATASET_METADATA_SESSION_KEY)

    if dataframe is not None and metadata is not None:
        _render_summary(dataframe, metadata)
    else:
        st.caption("No validated dataset is currently loaded.")
    render_api_reference("loan_xai", "upload")


def _process_upload(filename: str, content: bytes) -> None:
    try:
        dataset = load_csv(filename, content)
    except DatasetValidationError as exc:
        _clear()
        st.error(f"Unable to load dataset: {exc}")
        return

    if dataset.fingerprint != st.session_state.get(DATASET_FINGERPRINT_SESSION_KEY):
        st.session_state[DATAFRAME_SESSION_KEY] = dataset.dataframe
        st.session_state[DATASET_METADATA_SESSION_KEY] = dataset.metadata
        st.session_state[DATASET_FINGERPRINT_SESSION_KEY] = dataset.fingerprint

    st.success(
        f"Loaded **{dataset.filename}** — "
        f"{len(dataset.dataframe):,} rows · {len(dataset.dataframe.columns):,} columns."
    )


def _clear() -> None:
    for key in (DATAFRAME_SESSION_KEY, DATASET_METADATA_SESSION_KEY, DATASET_FINGERPRINT_SESSION_KEY):
        st.session_state.pop(key, None)


def _render_summary(dataframe, metadata: dict) -> None:
    st.subheader("Dataset overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{metadata['rows']:,}")
    c2.metric("Columns", f"{metadata['columns']:,}")
    c3.metric("File size", format_bytes(int(metadata["size_bytes"])))
    st.dataframe(dataframe.head(PREVIEW_ROWS), width="stretch", hide_index=True)
