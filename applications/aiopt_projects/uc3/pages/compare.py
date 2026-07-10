"""UC3 — Compare: Side-by-side view of all three memory strategies."""

import streamlit as st

from applications.aiopt_projects.uc3.constants import (
    BUFFER_HISTORY_KEY,
    ENTITY_HISTORY_KEY,
    ENTITY_STATE_KEY,
    SUMMARY_HISTORY_KEY,
    SUMMARY_STATE_KEY,
)


def render() -> None:
    st.subheader("⚖️ Compare — Memory Strategies")

    st.markdown(
        "This page shows what context each memory strategy would send to the LLM "
        "based on your conversation history from the Playground. "
        "Run a few turns there first, then return here."
    )

    buf_history = st.session_state.get(BUFFER_HISTORY_KEY, [])
    sum_history = st.session_state.get(SUMMARY_HISTORY_KEY, [])
    ent_history = st.session_state.get(ENTITY_HISTORY_KEY, [])
    summary     = st.session_state.get(SUMMARY_STATE_KEY, "")
    entities    = st.session_state.get(ENTITY_STATE_KEY, {})

    if not any([buf_history, sum_history, ent_history]):
        st.info("No conversation history yet. Go to the Playground tab and have a few turns of conversation, then return here.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📦 Buffer Memory")
        WINDOW = 6
        recent = buf_history[-WINDOW:] if len(buf_history) > WINDOW else buf_history
        st.metric("Full history", f"{len(buf_history)} messages")
        st.metric("Sent to LLM", f"{len(recent)} messages")
        st.metric("Dropped", f"{max(0, len(buf_history) - WINDOW)} messages")
        st.markdown("**Context that would be sent:**")
        if recent:
            for m in recent:
                with st.container(border=True):
                    st.caption(m.role.upper())
                    st.write(m.content[:150] + ("…" if len(m.content) > 150 else ""))
        else:
            st.caption("No buffer history. Use Buffer mode in Playground.")

    with col2:
        st.markdown("### 📝 Summary Memory")
        st.metric("Full history", f"{len(sum_history)} messages")
        st.metric("Summary exists?", "Yes" if summary else "No")
        if summary:
            with st.container(border=True):
                st.caption("SUMMARY (injected as user message)")
                st.write(summary[:300] + ("…" if len(summary) > 300 else ""))
        recent_4 = sum_history[-4:] if sum_history else []
        st.metric("Recent msgs sent", len(recent_4))
        for m in recent_4:
            with st.container(border=True):
                st.caption(m.role.upper())
                st.write(m.content[:150] + ("…" if len(m.content) > 150 else ""))
        if not sum_history:
            st.caption("No summary history. Use Summary mode in Playground.")

    with col3:
        st.markdown("### 🧠 Entity Memory")
        st.metric("Full history", f"{len(ent_history)} messages")
        entity_count = sum(len(v) for v in entities.values())
        st.metric("Entities extracted", entity_count)
        if any(entities.values()):
            with st.container(border=True):
                st.caption("ENTITY STORE (injected into system prompt)")
                for k, vs in entities.items():
                    if vs:
                        st.markdown(f"**{k.capitalize()}:** {', '.join(vs)}")
        else:
            st.caption("No entity history. Use Entity mode in Playground.")

    st.divider()
    st.markdown("### Token Cost Comparison (estimated)")
    st.table({
        "Strategy": ["Buffer", "Summary", "Entity"],
        "Context tokens (approx)": [
            f"~{len(buf_history[-6:]) * 40} (last 6 msgs × ~40 tok each)",
            f"~{len(summary.split()) * 1.3:.0f} (summary) + ~{len(sum_history[-4:]) * 40} (recent)",
            f"~{entity_count * 8} (entities) + full history",
        ],
        "Extra LLM calls": ["None", "1 per summary trigger", "1 per turn (extraction)"],
    })
