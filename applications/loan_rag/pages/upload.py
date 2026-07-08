"""Upload / load policy document — page 1 of the loan RAG workflow."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from applications.loan_rag.constants import (
    CHUNKS_SESSION_KEY,
    LOAD_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
)
from applications.loan_rag.services.document_loader import (
    LoadResult,
    chunk_text,
    load_default_policy,
    load_pdf_bytes,
    load_txt_bytes,
)
from applications.loan_rag.services.rag_chain import RAGConfig
from components.tier_guide import render_tier_guide
from applications.shared.api_reference import render_api_reference


def render() -> None:
    st.header("📄 Load Policy Document")
    render_tier_guide("loan_rag")
    st.caption(
        "Load the default FinCorp Bank loan policy or upload your own PDF / TXT. "
        "The document will be chunked and stored in a vector database."
    )

    # ---- Default policy shortcut ----------------------------------------
    default_path = Path(__file__).resolve().parents[4] / "data" / "loan_policy.pdf"
    default_available = default_path.exists()

    col_default, col_upload = st.columns(2)

    with col_default:
        with st.container(border=True):
            st.markdown("#### Use default policy")
            st.caption("FinCorp Bank Loan Eligibility Policy v3.2 (5 pages, Jan 2024)")
            if default_available:
                if st.button("Load loan_policy.pdf", use_container_width=True, type="primary"):
                    _load_and_store(load_default_policy())
            else:
                st.warning(
                    "Default policy PDF not found. "
                    "Run: `python scripts/generate_policy_pdf.py`"
                )

    with col_upload:
        with st.container(border=True):
            st.markdown("#### Upload custom document")
            st.caption("Supported formats: PDF, TXT (max 10 MB)")
            uploaded = st.file_uploader(
                "Drop file here",
                type=["pdf", "txt"],
                label_visibility="collapsed",
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

    # ---- Current document status ----------------------------------------
    load_result: LoadResult | None = st.session_state.get(LOAD_RESULT_SESSION_KEY)
    if load_result is not None:
        st.divider()
        st.subheader("Loaded document")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Source", load_result.source_name)
        m2.metric("Pages", load_result.pages)
        m3.metric("Words", f"{load_result.word_count:,}")
        m4.metric("Characters", f"{load_result.char_count:,}")

        st.success("Document loaded. Click **Explore Chunks** to see how it was split.")

        st.button(
            "→ Go to Explore Chunks",
            type="primary",
            use_container_width=False,
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "🔍 Explore Chunks"}
            ),
        )
    render_api_reference("loan_rag", "upload")


def _load_and_store(load_result: LoadResult) -> None:
    """Store the load result and create default chunks + config."""
    config: RAGConfig = st.session_state.get(
        RAG_CONFIG_SESSION_KEY, RAGConfig()
    )
    chunks = chunk_text(
        load_result,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    st.session_state[LOAD_RESULT_SESSION_KEY] = load_result
    st.session_state[CHUNKS_SESSION_KEY] = chunks
    # Invalidate any stale vector store when document changes.
    st.session_state.pop(VECTOR_STORE_SESSION_KEY, None)
    st.success(f"Loaded **{load_result.source_name}** — {len(chunks)} chunks created.")
