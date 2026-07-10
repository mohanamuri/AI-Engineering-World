"""RAG UC3 — Concept page: Agentic RAG."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Agentic RAG — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why a fixed single search sometimes isn't enough\n"
        "- What an 'agent' is and how it decides what to do\n"
        "- How the AI rephrases your question to find better results\n"
        "- What 'adaptive retrieval' means in plain English"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem with UC1 & UC2 — One Search, No Second Chances")

    st.markdown(
        "UC1 and UC2 always search once and move on — "
        "no matter how good or bad the results are.\n\n"
        "Imagine asking: *'What were the key decisions in the Q3 board meeting regarding the Asia expansion?'*\n\n"
        "- If the search returns weak passages, the AI still writes an answer from them\n"
        "- Nobody checks: *'Were these results actually relevant?'*\n"
        "- The AI may confidently answer from weak evidence"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1 / UC2 — Fixed Search**")
            st.markdown(
                "Search once → pass results to AI → get answer\n\n"
                "- Simple and fast\n"
                "- No quality check on retrieved chunks\n"
                "- If first search is weak, answer is weak\n"
                "- No retries, no reformulation"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC3 — Agentic RAG**")
            st.markdown(
                "Search → check quality → decide: answer or search again?\n\n"
                "- AI evaluates its own search results\n"
                "- If results are weak: rephrases the query and searches again\n"
                "- Keeps trying until it has enough information\n"
                "- Every decision is shown to you in the chat"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — The Agent Loop")

    st.graphviz_chart("""
    digraph AgenticRAG {
        rankdir=TB
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        Q  [label="Your Question" fillcolor="#fce7f3" color="#ec4899"]
        S  [label="Search Documents" fillcolor="#dbeafe" color="#3b82f6"]
        Ch [label="Agent Checks:\nAre results good enough?" fillcolor="#fef9c3" color="#eab308" shape=diamond]
        R  [label="Rephrase Question\n& Search Again" fillcolor="#fff7ed" color="#f97316"]
        A  [label="AI Writes Final Answer" fillcolor="#f0fdf4" color="#22c55e"]

        Q -> S -> Ch
        Ch -> A    [label="Yes — enough context"]
        Ch -> R    [label="No — weak results"]
        R  -> S    [label="retry"]
    }
    """)

    steps = [
        ("1️⃣ First search",
         "The agent searches your documents for relevant chunks — same as UC1."),
        ("2️⃣ Quality check (new in UC3)",
         "Before writing the answer, the agent reads the retrieved chunks and asks itself: "
         "*'Do these chunks actually answer the question?'* "
         "This is done with a short LLM call — the agent acts as its own critic."),
        ("3️⃣ Reformulate & retry (if needed)",
         "If the chunks are weak or off-topic, the agent rephrases the original question "
         "into a new version that might retrieve better results — then searches again. "
         "This is called **query reformulation**."),
        ("4️⃣ Final answer",
         "Once the agent decides it has enough good context, it writes the final answer. "
         "In the chat UI you'll see every decision the agent made: "
         "*'Searching... Results insufficient. Reformulating... Searching again... Answer ready.'*"),
    ]
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    # ── Key terms ────────────────────────────────────────────────────────────
    st.markdown("### Key Terms (Plain English)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("**Agent**")
            st.write(
                "An AI that can make decisions and take actions — not just generate text. "
                "Here, the agent decides whether to search again or write the answer."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Query Reformulation**")
            st.write(
                "Automatically rewriting a search query to get better results. "
                "Like trying different keywords when your first Google search doesn't work."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Adaptive Retrieval**")
            st.write(
                "The system adapts how many times it searches based on result quality — "
                "instead of always searching exactly once."
            )

    st.success(
        "**Ready to try it?** Ask a complex, multi-part question in the Chat. "
        "Watch the agent's reasoning trace — you'll see every search attempt and "
        "the decision that led to the final answer."
    )
