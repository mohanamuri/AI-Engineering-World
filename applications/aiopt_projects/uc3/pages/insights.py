"""UC3 — Insights: Key takeaways, interview Q&A, and connected concepts."""

import streamlit as st

from applications.aiopt_projects.uc3.constants import (
    BUFFER_HISTORY_KEY,
    ENTITY_STATE_KEY,
    SUMMARY_STATE_KEY,
)


def render() -> None:
    st.subheader("💡 Insights — Memory Patterns")

    buf_history = st.session_state.get(BUFFER_HISTORY_KEY, [])
    summary     = st.session_state.get(SUMMARY_STATE_KEY, "")
    entities    = st.session_state.get(ENTITY_STATE_KEY, {})

    if buf_history or summary or any((entities or {}).values()):
        st.markdown("#### Your session")
        c1, c2, c3 = st.columns(3)
        c1.metric("Buffer turns", len(buf_history) // 2)
        c2.metric("Summary active?", "Yes" if summary else "No")
        c3.metric("Entities extracted", sum(len(v) for v in (entities or {}).values()))
        st.divider()

    st.markdown("#### Strategy Decision Guide")
    st.table({
        "Criterion": [
            "Conversation length",
            "Extra LLM calls per turn",
            "Key facts must persist",
            "Users mention names/orgs",
            "Memory footprint (RAM)",
            "Simplest to implement",
        ],
        "Buffer": ["Short (< 10 turns)", "0", "Only in window", "Lost outside window", "Low", "✅ Yes"],
        "Summary": ["Long (10–100 turns)", "1 (on trigger)", "Yes (in summary)", "May be summarised", "Low", "Medium"],
        "Entity": ["Any length", "1 every turn", "Yes (structured)", "Always tracked", "Low (dict)", "Medium"],
    })

    st.divider()

    # ── Interview Q&A ────────────────────────────────────────────────────────
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions in LLM system design and AI engineering interviews.")

    qa_pairs = [
        (
            "Why do LLMs need external memory management? Isn't the context window enough?",
            "The context window is finite (typically 4K–128K tokens depending on the model). "
            "Once exceeded, either: (a) the application throws an error, "
            "(b) old messages are silently dropped, losing conversation history, or "
            "(c) costs skyrocket as you pay for every token in every call. "
            "Memory management decides *what to keep* and *what to compress* so conversations "
            "can run indefinitely at predictable cost."
        ),
        (
            "What is the difference between Buffer, Summary, and Entity memory?",
            "**Buffer memory** keeps the last N messages verbatim — simple sliding window, "
            "no extra LLM calls. Loses old context entirely when full.\n\n"
            "**Summary memory** periodically summarises old turns with an LLM call, "
            "retaining key facts in compressed form. Works for long sessions where facts matter.\n\n"
            "**Entity memory** extracts named entities (people, places, facts) each turn "
            "and stores them in a structured dict. Injects this fact store into the system prompt. "
            "Best for assistants that need to remember specific facts about the user."
        ),
        (
            "How would you implement memory for a customer support chatbot handling 50-turn conversations?",
            "Use **summary memory** with a trigger at 8–10 messages: "
            "(1) When history exceeds the trigger, call the LLM to summarise old turns into "
            "3–5 bullets. (2) Replace old turns with the summary + keep the last 4 messages. "
            "(3) Persist the summary in a database keyed by session ID so it survives page refreshes. "
            "For additional robustness, also track entity memory for the customer's account number, "
            "product name, and issue description — these must survive the entire session."
        ),
        (
            "What are the failure modes of summary memory?",
            "Three key failures: "
            "(1) **Information loss** — the summariser drops a detail the user considers critical. "
            "Mitigation: always keep the last 4 messages verbatim alongside the summary. "
            "(2) **Hallucination in summary** — the summariser invents facts. "
            "Mitigation: use temperature=0.0 for summarisation; lower temperatures reduce fabrication. "
            "(3) **Cascading errors** — a wrong summary propagates to all future turns. "
            "Mitigation: let users reset the conversation history or correct the summary explicitly."
        ),
        (
            "How does entity memory differ from RAG?",
            "Entity memory extracts facts *from the current conversation* and maintains them "
            "in a structured dict across turns. It's transient (lives for the session) and "
            "updates in real time.\n\n"
            "RAG retrieves relevant information from an *external, pre-indexed document store* "
            "on every query. It's persistent (lives across sessions) and static (the index "
            "is built upfront).\n\n"
            "They complement each other: use RAG for background knowledge, entity memory "
            "for what the user told you this session."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()

    # ── Connected Concepts ───────────────────────────────────────────────────
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("Context Window", "The maximum number of tokens an LLM can process in a single call "
         "(input + output combined). Examples: GPT-4o = 128K, Claude 3.5 Sonnet = 200K, "
         "llama-3.1-8b = 128K. Memory patterns exist because even 128K tokens cost money "
         "and add latency when sent on every turn."),
        ("LangChain Memory Classes", "LangChain provides pre-built implementations of these patterns: "
         "`ConversationBufferMemory`, `ConversationSummaryMemory`, `ConversationEntityMemory`. "
         "This UC implements them from scratch with Groq so you understand the underlying mechanics "
         "before using a library abstraction."),
        ("Retrieval-Augmented Memory", "An advanced pattern: store all conversation turns in a vector "
         "database. On each new turn, retrieve the most *relevant* past turns (not just the most "
         "recent). This solves the problem of buffer memory where recent turns may not be the "
         "most contextually relevant ones."),
        ("Token Budget", "The total tokens sent per turn = system prompt + memory context + current turn. "
         "In production, define a token budget per call (e.g. 2K for memory context) and design your "
         "memory strategy to stay within it. Summary memory and entity memory are both designed "
         "to fit within a fixed budget."),
        ("Session Persistence", "Memory stored in Python dicts or Streamlit session state disappears "
         "when the server restarts. In production, persist conversation history and entity stores in "
         "Redis (for fast access) or a database (PostgreSQL + JSON column for entity stores). "
         "Use session IDs to retrieve the right conversation per user."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC4 → Streaming + Fallback:** Memory controls *what* the model knows. "
        "Streaming controls *how fast* the user sees the response. "
        "Fallback ensures the response arrives even when the primary model fails."
    )
