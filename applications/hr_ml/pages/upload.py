import streamlit as st

from components.tier_guide import render_tier_guide
from applications.hr_ml.services.data_loader import (
    DATAFRAME_SESSION_KEY,
    DATASET_FINGERPRINT_SESSION_KEY,
    DATASET_METADATA_SESSION_KEY,
    MAX_UPLOAD_BYTES,
    DatasetValidationError,
    LoadedDataset,
    load_csv,
)
from applications.hr_ml.utils.helpers import format_bytes
from applications.shared.api_reference import render_api_reference


PREVIEW_ROWS = 10


def render():
    st.header("📤 Upload Dataset")
    render_tier_guide("hr_ml")

    st.info(
        "Upload an HR Attrition dataset (CSV). The file should include employee "
        "features and an **Attrition** column (Yes/No). "
        "The validated dataset persists as you move between pages."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"],
        accept_multiple_files=False,
        help=(
            f"Maximum size: {MAX_UPLOAD_BYTES // (1024 * 1024)} MB. "
            "The file must contain headers and at least one data row."
        ),
        key="hr_ml_csv_uploader",
    )

    if uploaded_file is not None:
        _process_upload(uploaded_file.name, uploaded_file.getvalue())

    dataframe = st.session_state.get(DATAFRAME_SESSION_KEY)
    metadata = st.session_state.get(DATASET_METADATA_SESSION_KEY)

    if dataframe is not None and metadata is not None:
        _render_dataset_summary(dataframe, metadata)
    else:
        st.caption("No validated dataset is currently loaded.")
    render_api_reference("hr_ml", "upload")


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
        f"{len(dataset.dataframe):,} rows and "
        f"{len(dataset.dataframe.columns):,} columns."
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

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{metadata['rows']:,}")
    col2.metric("Columns", f"{metadata['columns']:,}")
    col3.metric("File size", format_bytes(int(metadata["size_bytes"])))

    st.markdown(f"**Source:** `{metadata['filename']}`")

    if "Attrition" in dataframe.columns:
        attrition_counts = dataframe["Attrition"].value_counts()
        yes_count = attrition_counts.get("Yes", 0)
        no_count = attrition_counts.get("No", 0)
        total = yes_count + no_count
        if total > 0:
            st.info(
                f"**Target distribution** — Stayed: {no_count:,} ({no_count/total:.0%}) · "
                f"Left: {yes_count:,} ({yes_count/total:.0%})"
            )

    st.markdown(f"**Preview:** first {min(PREVIEW_ROWS, len(dataframe)):,} rows")
    st.dataframe(dataframe.head(PREVIEW_ROWS), use_container_width=True, hide_index=True)
