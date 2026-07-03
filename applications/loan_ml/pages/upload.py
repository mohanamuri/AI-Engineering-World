import streamlit as st

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


PREVIEW_ROWS = 10


def render():
    st.header("📤 Upload Dataset")

    st.info(
        "Upload a UTF-8 CSV dataset to begin the machine learning workflow. "
        "The validated dataset remains available as you move between pages."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"],
        accept_multiple_files=False,
        help=(
            f"Maximum size: {MAX_UPLOAD_BYTES // (1024 * 1024)} MB. "
            "The file must contain headers and at least one data row."
        ),
        key="loan_ml_csv_uploader",
    )

    if uploaded_file is not None:
        _process_upload(uploaded_file.name, uploaded_file.getvalue())

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    metadata = st.session_state.get(DATASET_METADATA_SESSION_KEY)

    if dataframe is not None and metadata is not None:
        _render_dataset_summary(dataframe, metadata)
    else:
        st.caption("No validated dataset is currently loaded.")


def _process_upload(filename: str, content: bytes) -> None:
    try:
        dataset = load_csv(filename, content)
    except DatasetValidationError as exc:
        _clear_dataset()
        st.error(f"Unable to load dataset: {exc}")
        return

    if dataset.fingerprint != st.session_state.get(
        DATASET_FINGERPRINT_SESSION_KEY
    ):
        _store_dataset(dataset)

    st.success(
        f"Loaded **{dataset.filename}** successfully — "
        f"{len(dataset.dataframe):,} rows and "
        f"{len(dataset.dataframe.columns):,} columns."
    )


def _store_dataset(dataset: LoadedDataset) -> None:
    st.session_state[DATAFRAME_SESSION_KEY] = dataset.dataframe
    st.session_state[DATASET_METADATA_SESSION_KEY] = dataset.metadata
    st.session_state[DATASET_FINGERPRINT_SESSION_KEY] = dataset.fingerprint


def _clear_dataset() -> None:
    for key in (
        DATAFRAME_SESSION_KEY,
        DATASET_METADATA_SESSION_KEY,
        DATASET_FINGERPRINT_SESSION_KEY,
    ):
        st.session_state.pop(key, None)


def _render_dataset_summary(dataframe, metadata: dict[str, object]) -> None:
    st.subheader("Dataset overview")

    row_metric, column_metric, size_metric = st.columns(3)
    row_metric.metric("Rows", f"{metadata['rows']:,}")
    column_metric.metric("Columns", f"{metadata['columns']:,}")
    size_metric.metric("File size", format_bytes(int(metadata["size_bytes"])))

    st.markdown(f"**Source:** `{metadata['filename']}`")
    st.markdown(f"**Preview:** first {min(PREVIEW_ROWS, len(dataframe)):,} rows")
    st.dataframe(
        dataframe.head(PREVIEW_ROWS),
        width="stretch",
        hide_index=True,
    )
