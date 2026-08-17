"""UC7 — History page. Full chat history with module attribution."""

import streamlit as st

from applications.rag_projects.services.modular_rag import ModularRAGResult
from applications.rag_projects.uc7.constants import CHAT_HISTORY_SESSION_KEY


def render() -> None:
    st.subheader("📜 Chat History")

    history: list[ModularRAGResult] = st.session_state.get(CHAT_HISTORY_SESSION_KEY, [])

    if not history:
        st.info("No chat history yet. Go to **Chat** to ask questions.")
        return

    st.write(f"**{len(history)} question(s)** in this session.")

    for i, result in enumerate(reversed(history), 1):
        label = f"Q{len(history) - i + 1}: {result.query[:80]}{'…' if len(result.query) > 80 else ''}"
        with st.expander(label, expanded=(i == 1)):
            st.markdown(f"**Question:** {result.query}")
            st.markdown(f"**Modules used:** {' + '.join(result.active_modules)}")
            st.markdown(f"**Answer:**\n\n{result.answer}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Active modules", len(result.active_modules))
            c2.metric("Fused chunks", len(result.fused_chunks))
            c3.metric("Sources", len(result.source_names))

            if result.source_names:
                st.markdown("**Sources:** " + ", ".join(f"`{s}`" for s in result.source_names))

            if result.fused_chunks:
                st.markdown("**Top fused chunks:**")
                for fc in result.fused_chunks[:3]:
                    src = fc.chunk.metadata.get("source", "?")
                    mods = ", ".join(fc.contributing_modules)
                    st.caption(f"  RRF {fc.rrf_score} · [{src}] · {mods}")

            st.caption(f"*{result.timestamp}*")
