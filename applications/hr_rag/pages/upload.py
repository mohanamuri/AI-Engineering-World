"""Upload HR policy document — page 1 of the HR RAG workflow."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from components.tier_guide import render_tier_guide
from applications.hr_rag.constants import (
    CHUNKS_SESSION_KEY, LOAD_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY, RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)
from applications.hr_rag.services.document_loader import (
    LoadResult, chunk_text, load_pdf_bytes, load_txt_bytes,
)
from applications.hr_rag.services.rag_chain import RAGConfig
from applications.shared.api_reference import render_api_reference

_DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "hr_docs" / "hr_policy.txt"


def render() -> None:
    st.header("📄 Load HR Policy Document")
    render_tier_guide("hr_rag")
    st.caption(
        "Load the default HR policy or upload your own PDF / TXT. "
        "The document will be chunked and embedded into a vector database."
    )

    col_default, col_upload = st.columns(2)

    with col_default:
        with st.container(border=True):
            st.markdown("#### Use default policy")
            st.caption("hr_policy.txt — HR attrition, retention & performance policy")
            if _DEFAULT_PATH.exists():
                if st.button("Load hr_policy.txt", use_container_width=True, type="primary"):
                    try:
                        result = load_txt_bytes(_DEFAULT_PATH.read_bytes(), "hr_policy.txt")
                        _load_and_store(result)
                    except ValueError as exc:
                        st.error(str(exc))
            else:
                st.warning("Default policy not found in data/.")

    with col_upload:
        with st.container(border=True):
            st.markdown("#### Upload your own")
            st.caption("Supported: PDF, TXT · Max 10 MB")
            uploaded = st.file_uploader(
                "Drop file here", type=["pdf", "txt"],
                label_visibility="collapsed", key="hr_rag_uploader",
            )
            if uploaded is not None:
                if st.button("Load uploaded file", use_container_width=True):
                    file_bytes = uploaded.read()
                    try:
                        if uploaded.name.lower().endswith(".pdf"):
                            result = load_pdf_bytes(file_bytes, uploaded.name)
                        else:
                            result = load_txt_bytes(file_bytes, uploaded.name)
                        _load_and_store(result)
                    except ValueError as exc:
                        st.error(str(exc))

    load_result: LoadResult | None = st.session_state.get(LOAD_RESULT_SESSION_KEY)
    if load_result is not None:
        st.divider()
        st.subheader("Loaded document")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Source", load_result.source_name)
        m2.metric("Pages", load_result.pages)
        m3.metric("Words", f"{load_result.word_count:,}")
        m4.metric("Characters", f"{load_result.char_count:,}")
        st.success("Document loaded. Navigate to **Configure RAG** to continue.")
        st.button(
            "→ Go to Configure RAG", type="primary",
            on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: "⚙️ Configure RAG"}),
        )

    render_api_reference("hr_rag", "upload")


def _load_and_store(load_result: LoadResult) -> None:
    config = st.session_state.get(RAG_CONFIG_SESSION_KEY, RAGConfig())
    chunks = chunk_text(load_result, chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    st.session_state[LOAD_RESULT_SESSION_KEY] = load_result
    st.session_state[CHUNKS_SESSION_KEY] = chunks
    st.session_state.pop(VECTOR_STORE_SESSION_KEY, None)
    st.success(f"Loaded **{load_result.source_name}** — {len(chunks)} chunks created.")
