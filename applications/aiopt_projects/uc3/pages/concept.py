"""UC3 — Concept: Three memory strategies for multi-turn LLM conversations."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Memory Patterns")

    st.markdown(
        """
        ### The Context Window Problem

        Every LLM call is stateless. To maintain a conversation, you must resend prior
        messages on every turn. As the conversation grows, so does your context — until
        you hit the model's context limit and older messages fall off, or your cost per
        call becomes prohibitive.

        **Memory patterns** manage what gets sent to the LLM on each turn. Three strategies
        cover most production use cases.
        """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("**📦 Buffer Memory**")
            st.markdown(
                "Keep the last N messages verbatim. Simple and deterministic.\n\n"
                "- Pro: No extra LLM calls\n"
                "- Pro: No information loss within window\n"
                "- Con: Drops oldest context when window fills\n"
                "- Best for: Short, focused conversations"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**📝 Summary Memory**")
            st.markdown(
                "Summarise old turns with an LLM call; keep summary + recent messages.\n\n"
                "- Pro: Preserves key facts from old turns\n"
                "- Pro: Scales to very long conversations\n"
                "- Con: One extra LLM call per summary\n"
                "- Best for: Long conversations, support sessions"
            )
    with col3:
        with st.container(border=True):
            st.markdown("**🧠 Entity Memory**")
            st.markdown(
                "Extract named entities per turn; inject fact store into system prompt.\n\n"
                "- Pro: Structured knowledge across the conversation\n"
                "- Pro: No conversation re-reading needed\n"
                "- Con: LLM call for entity extraction each turn\n"
                "- Best for: Personal assistants, CRM bots, HR tools"
            )

    st.divider()
    st.markdown("### How Each Strategy Works")

    with st.expander("📦 Buffer Memory — Technical Detail"):
        st.markdown(
            "**Algorithm:** `context = history[-N:]` where N = window size (e.g. 6 messages).\n\n"
            "- Always send the last N messages to the LLM\n"
            "- No transformation — messages sent verbatim\n"
            "- When history exceeds N, older messages are simply dropped\n\n"
            "**Prompt structure:**\n"
            "```\n[System] You are a helpful assistant.\n[User] (turn N-2)\n[Assistant] (turn N-2)\n...[User] current turn\n```"
        )

    with st.expander("📝 Summary Memory — Technical Detail"):
        st.markdown(
            "**Algorithm:** When history exceeds a trigger size (e.g. 6 messages),\n"
            "summarise the old turns with a separate LLM call, then store:\n"
            "`(summary, recent_4_messages, current_turn)`\n\n"
            "**Prompt structure:**\n"
            "```\n[System] You are a helpful assistant.\n[User] [Conversation summary so far] ...\n[Assistant] Understood.\n... (recent 4 turns) ...\n[User] current turn\n```\n\n"
            "**Summary prompt:** 'Summarise this conversation in 3–5 bullet points, preserving key facts.'"
        )

    with st.expander("🧠 Entity Memory — Technical Detail"):
        st.markdown(
            "**Algorithm:** After every user message, extract entities with a separate LLM call.\n"
            "Maintain a fact store: `{person: [], place: [], org: [], fact: []}`.\n"
            "Inject the fact store into the system prompt on every turn.\n\n"
            "**Entity extraction prompt:**\n"
            "```\nExtract named entities from the text.\nReturn ONLY valid JSON: {\"person\": [], \"place\": [], \"org\": [], \"fact\": []}.\n```\n\n"
            "**System prompt with entities:**\n"
            "```\nYou are a helpful assistant.\n\nKnown entities from this conversation:\nPerson: Alice, Bob\nOrg: Acme Corp\nFact: Alice is a data scientist\n```"
        )

    st.divider()
    st.markdown("### Which Strategy for Which Use Case?")
    st.table({
        "Use Case": [
            "Customer support chat (< 10 turns)",
            "Legal document review session",
            "Personal assistant that learns user details",
            "Technical debugging session",
            "Long-running research session (50+ turns)",
        ],
        "Best strategy": ["Buffer", "Summary", "Entity", "Buffer or Summary", "Summary"],
        "Why": [
            "Short sessions don't need compression",
            "Key facts must survive long sessions",
            "Names, preferences, role — entity store is perfect",
            "Recent context is most relevant; old turns can be dropped",
            "Verbatim history would blow the context limit",
        ],
    })

    st.success(
        "**Next → Playground:** Choose a memory strategy and have a multi-turn conversation. "
        "Watch the context window change as the conversation grows."
    )
