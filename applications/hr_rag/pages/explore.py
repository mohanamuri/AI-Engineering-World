"""Explore chunks page — page 2 of the HR RAG workflow."""

import streamlit as st
import pandas as pd

from applications.hr_rag.constants import CHUNKS_SESSION_KEY, LOAD_RESULT_SESSION_KEY


def render() -> None:
    st.header("🔍 Explore Chunks")

    chunks = st.session_state.get(CHUNKS_SESSION_KEY)
    load_result = st.session_state.get(LOAD_RESULT_SESSION_KEY)

    if not chunks:
        st.warning("Load a policy document first.")
        return

    st.subheader("Chunking summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total chunks", len(chunks))
    c2.metric("Source", load_result.source_name if load_result else "—")
    avg_len = sum(len(c.page_content) for c in chunks) / len(chunks)
    c3.metric("Avg chunk length", f"{avg_len:.0f} chars")

    st.info(
        "Each chunk is a fragment of your HR policy document. "
        "The RAG pipeline retrieves the most relevant chunks to answer each question."
    )

    st.subheader("Chunk preview")
    rows = [{"#": i + 1, "Length": len(c.page_content), "Preview": c.page_content[:150] + "…"
             if len(c.page_content) > 150 else c.page_content}
            for i, c in enumerate(chunks)]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    chunk_idx = st.slider("View full chunk", 1, len(chunks), 1) - 1
    with st.container(border=True):
        st.markdown(f"**Chunk {chunk_idx + 1} / {len(chunks)}** ({len(chunks[chunk_idx].page_content)} chars)")
        st.text(chunks[chunk_idx].page_content)
