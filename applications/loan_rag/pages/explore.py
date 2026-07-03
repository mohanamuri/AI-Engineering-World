"""Explore document chunks — page 2 of the loan RAG workflow."""

from __future__ import annotations

import streamlit as st

from applications.loan_rag.constants import (
    CHUNKS_SESSION_KEY,
    LOAD_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
)


def render() -> None:
    st.header("🔍 Explore Chunks")
    st.caption(
        "Inspect how the policy document was split into chunks. "
        "The retriever will search across these chunks at query time."
    )

    chunks = st.session_state.get(CHUNKS_SESSION_KEY)
    if not chunks:
        _render_empty_state()
        return

    # ---- Stats bar -------------------------------------------------------
    sizes = [len(c.page_content) for c in chunks]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total chunks", len(chunks))
    m2.metric("Avg size (chars)", f"{sum(sizes) // len(sizes):,}")
    m3.metric("Smallest", f"{min(sizes):,}")
    m4.metric("Largest", f"{max(sizes):,}")

    st.divider()

    # ---- Search bar ------------------------------------------------------
    query = st.text_input(
        "Filter chunks",
        placeholder="Type a keyword to highlight matching chunks…",
    )
    query_lower = query.strip().lower()

    # ---- Chunk cards -----------------------------------------------------
    matching = [
        (i, c) for i, c in enumerate(chunks)
        if not query_lower or query_lower in c.page_content.lower()
    ]

    st.caption(
        f"Showing {len(matching)} of {len(chunks)} chunks"
        + (f' matching "{query}"' if query_lower else "")
    )

    for display_rank, (original_idx, chunk) in enumerate(matching):
        text = chunk.page_content

        # Highlight keyword in preview if search active
        if query_lower:
            preview = _highlight(text[:400], query_lower)
        else:
            preview = text[:400].replace("\n", " ")

        with st.expander(
            f"Chunk {original_idx + 1} · {len(text):,} chars",
            expanded=(display_rank < 3 and not query_lower),
        ):
            st.markdown(preview, unsafe_allow_html=bool(query_lower))
            if len(text) > 400:
                st.caption(f"… {len(text) - 400:,} more characters")

    st.divider()
    st.button(
        "→ Go to Configure RAG",
        type="primary",
        on_click=lambda: st.session_state.update(
            {NAVIGATION_SESSION_KEY: "⚙️ Configure RAG"}
        ),
    )


def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("No document loaded yet.")
        st.write("Load a policy document first to see its chunks here.")
        st.button(
            "← Go to Load Policy",
            type="primary",
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: "📄 Load Policy"}
            ),
        )


def _highlight(text: str, keyword: str) -> str:
    """Wrap keyword occurrences in a yellow highlight span."""
    import re
    escaped = re.escape(keyword)
    return re.sub(
        f"({escaped})",
        r'<mark style="background:#fef08a;border-radius:3px;">\1</mark>',
        text.replace("\n", " "),
        flags=re.IGNORECASE,
    )
