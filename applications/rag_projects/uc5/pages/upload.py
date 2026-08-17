"""UC5 — Upload Docs page. Build ChromaDB vector store then build the Knowledge Graph."""

from pathlib import Path

import streamlit as st

from applications.rag_projects.services.document_loader import (
    LoadedDoc, chunk_documents, load_pdf_bytes, load_txt_bytes,
)
from applications.rag_projects.services.graph_rag import GraphRAGConfig, build_knowledge_graph
from applications.rag_projects.services.vector_store import build_vector_store
from applications.shared.groq_models import get_available_chat_models
from applications.rag_projects.uc5.constants import (
    CHAT_HISTORY_SESSION_KEY, CHUNKS_SESSION_KEY, DOCS_SESSION_KEY,
    KNOWLEDGE_GRAPH_SESSION_KEY, RAG_CONFIG_SESSION_KEY, VECTOR_STORE_SESSION_KEY,
)

_MAX_FILES = 5
_MAX_FILE_BYTES = 10 * 1024 * 1024
_SAMPLE_DIR = Path(__file__).resolve().parents[4] / "data" / "rag_sample_docs"
_SAMPLE_FILES = [
    ("remote_work_policy.txt", "ACME Remote Work Policy"),
    ("employee_benefits_guide.txt", "ACME Employee Benefits Guide"),
    ("code_of_conduct.txt", "ACME Code of Conduct"),
]


def render() -> None:
    st.subheader("📄 Upload Documents")
    st.write(
        "Upload 1–5 PDF or TXT files (or load the 3 sample documents). "
        "After loading, click **Build Knowledge Graph** — the LLM will extract "
        "entities and relationships from your documents automatically."
    )

    col_sample, col_upload = st.columns(2)

    with col_sample:
        with st.container(border=True):
            st.markdown("#### Use sample documents")
            st.caption("3 ACME corporate policy documents")
            for _, label in _SAMPLE_FILES:
                st.caption(f"• {label}")
            if all((_SAMPLE_DIR / fn).exists() for fn, _ in _SAMPLE_FILES):
                if st.button("Load sample documents", use_container_width=True, type="primary"):
                    _load_sample_docs()
            else:
                st.warning("Sample docs not found in data/rag_sample_docs/.")

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
                    uploaded_files = uploaded_files[:_MAX_FILES]
                if st.button("Load uploaded files", use_container_width=True):
                    _load_uploaded_files(uploaded_files)

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
            c1, c2, c3 = st.columns(3)
            c1.metric("Total chunks", vs.chunk_count)
            c2.metric("Documents", vs.doc_count)
            c3.metric("Embedding model", vs.embedding_model)

        st.divider()
        st.subheader("🕸️ Build Knowledge Graph")
        st.write(
            "Click below to extract entities and relationships from your documents. "
            "This runs one LLM call per chunk — for 30 chunks it takes roughly 30–60 seconds."
        )

        config: GraphRAGConfig = st.session_state.get(RAG_CONFIG_SESSION_KEY, GraphRAGConfig())
        chunks = st.session_state.get(CHUNKS_SESSION_KEY, [])

        # Let user pick the model right here — fetches available models from Groq
        if "_groq_models_cache" not in st.session_state:
            st.session_state["_groq_models_cache"] = get_available_chat_models()
        available = st.session_state["_groq_models_cache"]
        current_model = config.llm_model if config.llm_model in available else available[0]
        selected_model = st.selectbox(
            "LLM model for entity extraction",
            available,
            index=available.index(current_model),
            help="This model reads each chunk and extracts entity–relation triples.",
            key="uc5_upload_model",
        )
        config = GraphRAGConfig(
            llm_model=selected_model,
            top_k=config.top_k,
            temperature=config.temperature,
            max_hops=config.max_hops,
            max_chunks_for_graph=config.max_chunks_for_graph,
        )

        if st.button("Build Knowledge Graph", type="primary", use_container_width=True):
            _build_graph(chunks, config)

        kg = st.session_state.get(KNOWLEDGE_GRAPH_SESSION_KEY)
        if kg:
            st.success(
                f"Knowledge Graph ready: **{len(kg.all_entities)} entities**, "
                f"**{kg.edge_count} relationships** across {min(len(chunks), config.max_chunks_for_graph)} chunks. "
                "Go to **Configure** or **Chat**."
            )
    else:
        st.info("Load sample documents or upload your own to get started.")


def _load_sample_docs() -> None:
    loaded: list[LoadedDoc] = []
    with st.spinner("Loading sample documents…"):
        for filename, _ in _SAMPLE_FILES:
            path = _SAMPLE_DIR / filename
            try:
                loaded.append(load_txt_bytes(path.read_bytes(), filename))
            except Exception as exc:
                st.error(f"Could not load {filename}: {exc}")
                return
    _build_and_store(loaded)


def _load_uploaded_files(uploaded_files) -> None:
    loaded: list[LoadedDoc] = []
    with st.spinner("Loading documents…"):
        for f in uploaded_files:
            raw = f.read()
            if len(raw) > _MAX_FILE_BYTES:
                st.error(f"{f.name}: exceeds 10 MB, skipped.")
                continue
            try:
                doc = (load_pdf_bytes(raw, f.name) if f.name.lower().endswith(".pdf")
                       else load_txt_bytes(raw, f.name))
                loaded.append(doc)
            except Exception as exc:
                st.error(f"{f.name}: {exc}")
    if not loaded:
        st.error("No documents could be loaded.")
        return
    _build_and_store(loaded)


def _build_and_store(loaded_docs: list[LoadedDoc]) -> None:
    with st.spinner("Chunking documents…"):
        chunks = chunk_documents(loaded_docs)
    with st.spinner("Embedding into ChromaDB…"):
        try:
            vs = build_vector_store(chunks, doc_count=len(loaded_docs), collection_name="rag_uc5")
        except Exception as exc:
            st.error(f"Failed to build vector store: {exc}")
            return
    st.session_state[DOCS_SESSION_KEY] = loaded_docs
    st.session_state[CHUNKS_SESSION_KEY] = chunks
    st.session_state[VECTOR_STORE_SESSION_KEY] = vs
    st.session_state.pop(CHAT_HISTORY_SESSION_KEY, None)
    st.session_state.pop(KNOWLEDGE_GRAPH_SESSION_KEY, None)
    st.success(f"Loaded {len(loaded_docs)} document(s) → {len(chunks)} chunks. Now build the Knowledge Graph.")


def _build_graph(chunks, config: GraphRAGConfig) -> None:
    total = min(len(chunks), config.max_chunks_for_graph)
    progress_bar = st.progress(0, text=f"Extracting entities from chunk 0 / {total}…")

    def update_progress(done: int, total: int) -> None:
        progress_bar.progress(done / total, text=f"Extracting entities from chunk {done} / {total}…")

    with st.spinner("Building knowledge graph — this may take 30–90 seconds…"):
        try:
            kg = build_knowledge_graph(chunks, config, progress_cb=update_progress)
        except Exception as exc:
            st.error(f"Graph build failed: {exc}")
            return
    st.session_state[KNOWLEDGE_GRAPH_SESSION_KEY] = kg
    progress_bar.empty()
    st.rerun()
