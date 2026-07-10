"""RAG UC4 — Concept page: Self-RAG."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Self-RAG — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why generating an answer and stopping is not enough\n"
        "- How the AI critiques its own answer before showing it to you\n"
        "- What groundedness, relevance, and completeness mean\n"
        "- How self-reflection leads to better, more reliable answers"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — AI That Never Checks Its Own Work")

    st.markdown(
        "UC1, UC2, and UC3 all generate an answer and stop — nobody checks if it's actually good.\n\n"
        "Imagine a student who writes an essay but never proofreads it. "
        "The essay might be off-topic, miss key points, or make claims not supported by the sources.\n\n"
        "**Self-RAG adds a proofreader** — the AI reads its own answer and scores it "
        "on three criteria before you see it."
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1–UC3 — Generate & Stop**")
            st.markdown(
                "Search → generate answer → done\n\n"
                "- Fast\n"
                "- No quality guarantee\n"
                "- Answer might miss key parts of the question\n"
                "- Claims might not be backed by the documents"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC4 — Self-RAG**")
            st.markdown(
                "Search → generate → self-critique → retry if needed\n\n"
                "- Slower but more reliable\n"
                "- Every answer is scored before you see it\n"
                "- Low scores trigger a new search and a new answer\n"
                "- You see the scorecard for every attempt"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Generate, Critique, Retry")

    st.graphviz_chart("""
    digraph SelfRAG {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        Q  [label="Your Question" fillcolor="#fce7f3" color="#ec4899"]
        S  [label="Search\nDocuments" fillcolor="#dbeafe" color="#3b82f6"]
        G  [label="Generate\nAnswer" fillcolor="#e0f2fe" color="#0ea5e9"]
        Cr [label="Self-Critique\nGrounded? Relevant?\nComplete?" fillcolor="#fef9c3" color="#eab308" shape=diamond]
        P  [label="Final Answer\n+ Scorecard" fillcolor="#f0fdf4" color="#22c55e"]
        R  [label="Rewrite Query\n& Retry" fillcolor="#fff7ed" color="#f97316"]

        Q -> S -> G -> Cr
        Cr -> P [label="All scores pass"]
        Cr -> R [label="Score too low"]
        R  -> S
    }
    """)

    steps = [
        ("1️⃣ Search & generate",
         "The system retrieves relevant chunks and generates an answer — same as UC1."),
        ("2️⃣ Self-critique (new in UC4)",
         "The AI reads its own answer and scores it on three dimensions:\n\n"
         "- **Groundedness** — Is every claim supported by the retrieved documents?\n"
         "- **Relevance** — Does it actually answer the question that was asked?\n"
         "- **Completeness** — Is anything important missing?\n\n"
         "Each score is 0–10. The scorecard is shown to you every time."),
        ("3️⃣ Retry if needed",
         "If any score falls below the threshold, the system rewrites the search query "
         "to find better document passages, generates a new answer, and critiques again. "
         "This loop continues until all scores pass or the maximum attempts are reached."),
        ("4️⃣ Final answer with full transparency",
         "You see the final answer *and* the scorecard for every attempt. "
         "If the answer improved across attempts, you can see how and why."),
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
            st.markdown("**Groundedness**")
            st.write(
                "Every claim in the answer can be traced back to a specific document passage. "
                "A grounded answer never makes things up — it only states what the sources say."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Self-Reflection**")
            st.write(
                "The AI evaluating its own output. "
                "Just as a person re-reads their work before submitting, "
                "the AI re-reads its answer and assigns quality scores."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Critique Loop**")
            st.write(
                "A cycle of: generate → score → rewrite if needed → generate again. "
                "It stops when quality is good enough or the attempt limit is reached."
            )

    st.success(
        "**Ready to try it?** Ask a detailed question in the Chat. "
        "Watch the critique scorecard appear after each attempt — "
        "you'll see the AI improving its own answer in real time."
    )
