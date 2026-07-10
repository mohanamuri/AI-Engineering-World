"""UC3 — Playground: Multi-turn chat with selectable memory strategy."""

import streamlit as st

from applications.aiopt_projects.services.memory_patterns import (
    Message,
    chat_buffer,
    chat_entity,
    chat_summary,
)
from applications.aiopt_projects.uc3.constants import (
    BUFFER_HISTORY_KEY,
    ENTITY_HISTORY_KEY,
    ENTITY_STATE_KEY,
    MEMORY_TYPE_KEY,
    SUMMARY_HISTORY_KEY,
    SUMMARY_STATE_KEY,
)


def _init() -> None:
    for key in (BUFFER_HISTORY_KEY, SUMMARY_HISTORY_KEY, ENTITY_HISTORY_KEY):
        if key not in st.session_state:
            st.session_state[key] = []
    if SUMMARY_STATE_KEY not in st.session_state:
        st.session_state[SUMMARY_STATE_KEY] = ""
    if ENTITY_STATE_KEY not in st.session_state:
        st.session_state[ENTITY_STATE_KEY] = {}


def _clear(mem_type: str) -> None:
    if mem_type == "Buffer":
        st.session_state[BUFFER_HISTORY_KEY] = []
    elif mem_type == "Summary":
        st.session_state[SUMMARY_HISTORY_KEY] = []
        st.session_state[SUMMARY_STATE_KEY] = ""
    else:
        st.session_state[ENTITY_HISTORY_KEY] = []
        st.session_state[ENTITY_STATE_KEY] = {}


def render() -> None:
    st.subheader("🧪 Playground — Memory Patterns")
    _init()

    mem_type = st.radio(
        "Memory strategy",
        ["Buffer", "Summary", "Entity"],
        horizontal=True,
        key=MEMORY_TYPE_KEY,
    )

    col_info, col_clr = st.columns([4, 1])
    with col_info:
        if mem_type == "Buffer":
            st.caption("Keeps the last 6 messages verbatim.")
        elif mem_type == "Summary":
            st.caption("Summarises old turns when history exceeds 6 messages.")
        else:
            st.caption("Extracts entities per turn and injects them into the system prompt.")

    with col_clr:
        if st.button("🗑️ Clear", use_container_width=True):
            _clear(mem_type)
            st.rerun()

    # Display conversation history
    if mem_type == "Buffer":
        history: list[Message] = st.session_state[BUFFER_HISTORY_KEY]
    elif mem_type == "Summary":
        history = st.session_state[SUMMARY_HISTORY_KEY]
        summary = st.session_state[SUMMARY_STATE_KEY]
        if summary:
            with st.expander("📝 Current summary (injected as context)"):
                st.write(summary)
    else:
        history = st.session_state[ENTITY_HISTORY_KEY]
        entities = st.session_state[ENTITY_STATE_KEY]
        if any(entities.values()):
            with st.expander("🧠 Entity store (injected into system prompt)"):
                for k, vs in entities.items():
                    if vs:
                        st.markdown(f"**{k.capitalize()}:** {', '.join(vs)}")

    for msg in history:
        with st.chat_message(msg.role):
            st.write(msg.content)
            st.caption(msg.timestamp)

    user_input = st.chat_input("Type a message…")
    if user_input:
        with st.spinner("Thinking…"):
            if mem_type == "Buffer":
                state = chat_buffer(user_input, history)
                st.session_state[BUFFER_HISTORY_KEY] = state.messages
            elif mem_type == "Summary":
                state = chat_summary(user_input, history, st.session_state[SUMMARY_STATE_KEY])
                st.session_state[SUMMARY_HISTORY_KEY] = state.messages
                st.session_state[SUMMARY_STATE_KEY] = state.summary
            else:
                state = chat_entity(user_input, history, st.session_state[ENTITY_STATE_KEY])
                st.session_state[ENTITY_HISTORY_KEY] = state.messages
                st.session_state[ENTITY_STATE_KEY] = state.entities

        with st.expander(f"📊 Context sent this turn ({len(state.context_sent)} messages)"):
            for m in state.context_sent:
                st.markdown(f"**{m['role']}:** {m['content'][:200]}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Tokens in", state.tokens_in)
            c2.metric("Tokens out", state.tokens_out)
            c3.metric("Latency", f"{state.latency_ms:.0f} ms")
        st.rerun()
