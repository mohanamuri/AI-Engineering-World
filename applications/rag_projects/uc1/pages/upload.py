"""
UC1 — Upload Docs page.

Lets the user upload 1–5 PDF or plain-text files.
All loaded documents are chunked together with source metadata so the
vector store can later attribute each retrieved chunk to its origin file.
"""

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


def render() -> None:
    st.subheader("📄 Upload Documents")
    st.write(
        "Upload 1–5 PDF or TXT files. All documents are embedded into a single "
        "vector store — each chunk carries its source filename so you can see "
        "exactly which document answered your question."
    )

    # --- Upload widget ---
    uploaded_files = st.file_uploader(
        "Choose files (PDF or TXT, max 10 MB each)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help=f"Upload up to {_MAX_FILES} documents.",
    )

    if uploaded_files:
        if len(uploaded_files) > _MAX_FILES:
            st.warning(f"Maximum {_MAX_FILES} files allowed. Only the first {_MAX_FILES} will be used.")
            uploaded_files = uploaded_files[:_MAX_FILES]

        # --- Load documents ---
        col_load, _ = st.columns([2, 4])
        with col_load:
            do_load = st.button("📥 Load & Chunk Documents", use_container_width=True, type="primary")

        if do_load:
            loaded_docs: list[LoadedDoc] = []
            errors: list[str] = []

            with st.spinner("Loading documents…"):
                for f in uploaded_files:
                    raw = f.read()
                    if len(raw) > _MAX_FILE_BYTES:
                        errors.append(f"{f.name}: exceeds 10 MB limit, skipped.")
                        continue
                    try:
                        if f.name.lower().endswith(".pdf"):
                            doc = load_pdf_bytes(raw, f.name)
                        else:
                            doc = load_txt_bytes(raw, f.name)
                        loaded_docs.append(doc)
                    except Exception as exc:
                        errors.append(f"{f.name}: {exc}")

            if errors:
                for err in errors:
                    st.error(err)

            if not loaded_docs:
                st.error("No documents could be loaded. Check the files and try again.")
                return

            # Chunk all documents together
            with st.spinner("Chunking documents…"):
                chunk_size = 512
                chunk_overlap = 64
                chunks = chunk_documents(loaded_docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

            # Build vector store
            with st.spinner("Embedding chunks into ChromaDB — this may take 30–60 s on first run (model download)…"):
                try:
                    vs_result = build_vector_store(chunks, doc_count=len(loaded_docs))
                except Exception as exc:
                    st.error(f"Failed to build vector store: {exc}")
                    return

            # Save to session state
            st.session_state[DOCS_SESSION_KEY] = loaded_docs
            st.session_state[CHUNKS_SESSION_KEY] = chunks
            st.session_state[VECTOR_STORE_SESSION_KEY] = vs_result
            # Reset downstream state on re-load
            st.session_state.pop(CHAT_HISTORY_SESSION_KEY, None)
            st.session_state.pop(RAG_CONFIG_SESSION_KEY, None)

            st.success(f"Loaded {len(loaded_docs)} document(s) → {len(chunks)} chunks embedded.")

    # --- Show current state ---
    docs: list[LoadedDoc] | None = st.session_state.get(DOCS_SESSION_KEY)
    if docs:
        st.divider()
        st.subheader("Loaded Documents")
        for doc in docs:
            with st.expander(f"📄 {doc.name}", expanded=False):
                col1, col2, col3 = st.columns(3)
                col1.metric("Pages", doc.pages)
                col2.metric("Words", f"{doc.word_count:,}")
                col3.metric("Characters", f"{doc.char_count:,}")

        chunks = st.session_state.get(CHUNKS_SESSION_KEY, [])
        vs = st.session_state.get(VECTOR_STORE_SESSION_KEY)
        if vs:
            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total chunks", vs.chunk_count)
            col2.metric("Documents", vs.doc_count)
            col3.metric("Embedding model", vs.embedding_model)
            st.success("Vector store is ready. Go to **Configure** or **Chat**.")
    else:
        st.info("Upload documents above to get started.")
