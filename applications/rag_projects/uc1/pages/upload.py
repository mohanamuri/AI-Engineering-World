"""
UC1 — Upload Docs page.

Lets the user upload 1–5 PDF or plain-text files, or load the 3 bundled
sample documents in one click for an instant demo.
All loaded documents are chunked together with source metadata so the
vector store can attribute each retrieved chunk to its origin file.
"""

from pathlib import Path

import streamlit as st

from applications.rag_projects.services.document_loader import (
    LoadedDoc,
    chunk_documents,
    load_pdf_bytes,
    load_txt_bytes,
)
from applications.rag_projects.services.vector_store import build_vector_store
from applications.rag_projects.uc1.constants import (
    CHUNKS_SESSION_KEY,
    DOCS_SESSION_KEY,
    VECTOR_STORE_SESSION_KEY,
    RAG_CONFIG_SESSION_KEY,
    CHAT_HISTORY_SESSION_KEY,
)

_MAX_FILES = 5
_MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB per file
_SAMPLE_DIR = Path(__file__).resolve().parents[4] / "data" / "rag_sample_docs"
_SAMPLE_FILES = [
    ("remote_work_policy.txt", "ACME Remote Work Policy"),
    ("employee_benefits_guide.txt", "ACME Employee Benefits Guide"),
    ("code_of_conduct.txt", "ACME Code of Conduct"),
]


def render() -> None:
    st.subheader("📄 Upload Documents")
    st.write(
        "Upload 1–5 PDF or TXT files, or load the 3 bundled sample documents for an instant demo. "
        "All documents are embedded into a single vector store — each chunk carries its source "
        "filename so you can see exactly which document answered your question."
    )

    col_sample, col_upload = st.columns(2)

    # ── Sample documents (one-click demo) ────────────────────────────────────
    with col_sample:
        with st.container(border=True):
            st.markdown("#### Use sample documents")
            st.caption("3 ACME corporate policy documents — great for cross-doc queries")
            for _, label in _SAMPLE_FILES:
                st.caption(f"• {label}")
            samples_available = all((_SAMPLE_DIR / fn).exists() for fn, _ in _SAMPLE_FILES)
            if samples_available:
                if st.button("Load sample documents", use_container_width=True, type="primary"):
                    _load_sample_docs()
            else:
                st.warning("Sample docs not found in data/rag_sample_docs/.")

    # ── Custom upload ─────────────────────────────────────────────────────────
    with col_upload:
        with st.container(border=True):
            st.markdown("#### Upload your own")
            st.caption(f"PDF or TXT · up to {_MAX_FILES} files · max 10 MB each")
            uploaded_files = st.file_uploader(
                "Choose files", type=["pdf", "txt"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )
            if uploaded_files:
                if len(uploaded_files) > _MAX_FILES:
                    st.warning(f"Max {_MAX_FILES} files — using first {_MAX_FILES}.")
                    uploaded_files = uploaded_files[:_MAX_FILES]
                if st.button("Load uploaded files", use_container_width=True):
                    _load_uploaded_files(uploaded_files)

    # ── Current state ─────────────────────────────────────────────────────────
    docs: list[LoadedDoc] | None = st.session_state.get(DOCS_SESSION_KEY)
    if docs:
        st.divider()
        st.subheader("Loaded Documents")
        for doc in docs:
            with st.expander(f"📄 {doc.name}", expanded=False):
                c1, c2, c3 = st.columns(3)
                c1.metric("Pages", doc.pages)
                c2.metric("Words", f"{doc.word_count:,}")
                c3.metric("Characters", f"{doc.char_count:,}")

        vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
        if vs:
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total chunks", vs.chunk_count)
            c2.metric("Documents", vs.doc_count)
            c3.metric("Embedding model", vs.embedding_model)
            st.success("Vector store ready. Go to **Configure** or **Chat**.")
    else:
        st.info("Load sample documents or upload your own to get started.")


def _load_sample_docs() -> None:
    """Load all 3 bundled sample documents and build the vector store."""
    loaded_docs: list[LoadedDoc] = []
    with st.spinner("Loading sample documents…"):
        for filename, _ in _SAMPLE_FILES:
            path = _SAMPLE_DIR / filename
            try:
                doc = load_txt_bytes(path.read_bytes(), filename)
                loaded_docs.append(doc)
            except Exception as exc:
                st.error(f"Could not load {filename}: {exc}")
                return

    _build_and_store(loaded_docs)


def _load_uploaded_files(uploaded_files) -> None:
    """Load user-uploaded files and build the vector store."""
    loaded_docs: list[LoadedDoc] = []
    with st.spinner("Loading documents…"):
        for f in uploaded_files:
            raw = f.read()
            if len(raw) > _MAX_FILE_BYTES:
                st.error(f"{f.name}: exceeds 10 MB limit, skipped.")
                continue
            try:
                doc = load_pdf_bytes(raw, f.name) if f.name.lower().endswith(".pdf") else load_txt_bytes(raw, f.name)
                loaded_docs.append(doc)
            except Exception as exc:
                st.error(f"{f.name}: {exc}")

    if not loaded_docs:
        st.error("No documents could be loaded.")
        return

    _build_and_store(loaded_docs)


def _build_and_store(loaded_docs: list[LoadedDoc]) -> None:
    """Chunk all docs, build vector store, save to session state."""
    with st.spinner("Chunking documents…"):
        chunks = chunk_documents(loaded_docs)

    with st.spinner("Embedding into ChromaDB — may take 30–60 s on first run…"):
        try:
            vs_result = build_vector_store(chunks, doc_count=len(loaded_docs))
        except Exception as exc:
            st.error(f"Failed to build vector store: {exc}")
            return

    st.session_state[DOCS_SESSION_KEY] = loaded_docs
    st.session_state[CHUNKS_SESSION_KEY] = chunks
    st.session_state[VECTOR_STORE_SESSION_KEY] = vs_result
    st.session_state.pop(CHAT_HISTORY_SESSION_KEY, None)
    st.session_state.pop(RAG_CONFIG_SESSION_KEY, None)

    st.success(f"Loaded {len(loaded_docs)} document(s) → {len(chunks)} chunks embedded.")
