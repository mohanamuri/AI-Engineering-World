"""
UC2 — History page.

Displays the full chat history with query, answer, source attribution,
and retriever breakdown (Dense / BM25 / Both) for each chunk.
"""

import streamlit as st

from applications.rag_projects.services.hybrid_rag_chain import HybridRAGResult
from applications.rag_projects.uc2.constants import CHAT_HISTORY_SESSION_KEY

_RETRIEVER_BADGE = {
    "dense": "🔵 Dense",
    "bm25": "🟠 BM25",
    "both": "🟢 Both",
}


def render() -> None:
    st.subheader("📜 Chat History")

    history: list[HybridRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No chat history yet. Go to **Chat** to ask questions.")
        return

    st.write(f"**{len(history)} question(s)** in this session.")

    for i, result in enumerate(reversed(history), 1):
        label = f"Q{len(history) - i + 1}: {result.query[:80]}{'…' if len(result.query) > 80 else ''}"
        with st.expander(label, expanded=(i == 1)):
            st.markdown(f"**Question:** {result.query}")
            st.markdown(f"**Answer:**\n\n{result.answer}")

            if result.source_names:
                st.markdown("**Sources used:**")
                for name in result.source_names:
                    st.markdown(f"- `{name}`")

            # Retriever breakdown summary
            if result.hybrid_results:
                counts = {"dense": 0, "bm25": 0, "both": 0}
                for hr in result.hybrid_results:
                    counts[hr.retriever] = counts.get(hr.retriever, 0) + 1
                parts = []
                if counts["both"]:
                    parts.append(f"🟢 Both: {counts['both']}")
                if counts["dense"]:
                    parts.append(f"🔵 Dense-only: {counts['dense']}")
                if counts["bm25"]:
                    parts.append(f"🟠 BM25-only: {counts['bm25']}")
                st.caption("Retriever mix — " + "  ·  ".join(parts))

            st.caption(f"*{result.timestamp}*")

            with st.expander("Retrieved chunks", expanded=False):
                for j, hr in enumerate(result.hybrid_results, 1):
                    badge = _RETRIEVER_BADGE.get(hr.retriever, hr.retriever)
                    src = hr.doc.metadata.get("source", "unknown")
                    st.markdown(f"**Chunk {j}** — `{src}`  {badge}  RRF: `{hr.rrf_score:.4f}`")
                    st.text(hr.doc.page_content[:300] + ("…" if len(hr.doc.page_content) > 300 else ""))
                    if j < len(result.hybrid_results):
                        st.divider()
