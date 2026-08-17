"""RAG UC6 — Concept page: Corrective RAG (CRAG)."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Corrective RAG (CRAG) — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why retrieved chunks are not always relevant to the question\n"
        "- How CRAG grades every retrieved chunk before using it\n"
        "- When and how Wikipedia is used as a free fallback knowledge source\n"
        "- What CORRECT, AMBIGUOUS, and INCORRECT mean for a chunk"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — Bad Retrieval Produces Bad Answers")

    st.markdown(
        "Every RAG system (UC1–UC5) retrieves chunks and sends them to the LLM. "
        "But what if the retrieved chunks are **not relevant to the question**?\n\n"
        "Example: You upload a company HR policy and ask *'What is the capital of France?'*\n"
        "Standard RAG will still retrieve the most similar HR chunks and try to answer from them "
        "— producing a confusing or hallucinated answer.\n\n"
        "**CRAG solves this by validating the retrieval result before generating.**"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1–UC5 — Trust and Use**")
            st.markdown(
                "Retrieve → immediately generate from those chunks\n\n"
                "- Fast\n"
                "- Assumes retrieved chunks are relevant\n"
                "- If your docs don't cover the topic, the LLM confabulates\n"
                "- No external fallback"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC6 — Corrective RAG**")
            st.markdown(
                "Retrieve → grade each chunk → decide source → generate\n\n"
                "- Slower (one grade call per chunk)\n"
                "- Validates relevance before generating\n"
                "- Falls back to Wikipedia if local docs are insufficient\n"
                "- Shows grade and decision transparency"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Grade, Decide, Then Answer")

    st.graphviz_chart("""
    digraph CRAG {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        Q  [label="Your Question" fillcolor="#fce7f3" color="#ec4899"]
        R  [label="Retrieve Chunks\n(ChromaDB)" fillcolor="#dbeafe" color="#3b82f6"]
        G  [label="Grade Each Chunk\n(CORRECT / AMBIGUOUS / INCORRECT)" fillcolor="#fef9c3" color="#eab308" shape=diamond]
        LD [label="Use Local Docs\nOnly" fillcolor="#f0fdf4" color="#22c55e"]
        WD [label="Fetch Wikipedia\n(Free REST API)" fillcolor="#e0f2fe" color="#0ea5e9"]
        CB [label="Combine Local\n+ Wikipedia" fillcolor="#ede9fe" color="#7c3aed"]
        A  [label="Generate Answer" fillcolor="#f0fdf4" color="#22c55e"]

        Q -> R -> G
        G -> LD [label="Most CORRECT"]
        G -> WD [label="Most INCORRECT"]
        G -> CB [label="Mixed"]
        LD -> A
        WD -> A
        CB -> A
    }
    """)

    steps = [
        ("1️⃣ Retrieve top-k chunks from your documents",
         "Same as UC1 — ChromaDB vector search returns the most similar chunks."),
        ("2️⃣ Grade each chunk (new in UC6)",
         "The LLM reads each retrieved chunk and classifies it:\n\n"
         "- **CORRECT** — this chunk directly addresses the question\n"
         "- **AMBIGUOUS** — this chunk is related but only partially useful\n"
         "- **INCORRECT** — this chunk is off-topic or irrelevant\n\n"
         "You see the grade and reason for every chunk in the Chat panel."),
        ("3️⃣ Decision logic",
         "Based on the grades:\n\n"
         "- **Most CORRECT** → answer using local document chunks only\n"
         "- **Mixed (CORRECT + AMBIGUOUS)** → use local chunks AND supplement with Wikipedia\n"
         "- **Most INCORRECT** → ignore local chunks, use Wikipedia only\n\n"
         "The threshold is configurable — you can make it strict or lenient."),
        ("4️⃣ Wikipedia fallback (free, no API key)",
         "Wikipedia is accessed via the public REST API. "
         "The system searches for articles related to the question and extracts a short summary. "
         "No authentication needed — completely free."),
        ("5️⃣ Generate answer with source label",
         "The LLM generates a final answer from the selected source(s) "
         "and labels the answer: **Local Documents**, **Wikipedia**, or **Local + Wikipedia**."),
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
            st.markdown("**Relevance Grading**")
            st.write(
                "Using an LLM to score whether a retrieved passage is actually useful "
                "for answering the question. Think of it as a teacher marking "
                "homework — CORRECT means 'good answer', INCORRECT means 'off-topic'."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Corrective Mechanism**")
            st.write(
                "The 'correction' in CRAG is switching the knowledge source based on "
                "whether local retrieval succeeded. It's like a student checking "
                "their textbook first, then looking online if the textbook doesn't help."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Wikipedia REST API**")
            st.write(
                "A public web API that returns Wikipedia article summaries. "
                "No sign-up, no API key, completely free. "
                "CRAG uses it as a general knowledge fallback when your documents "
                "don't cover the question."
            )

    st.success(
        "**Ready to try it?** Upload documents, then in Chat ask a question "
        "that your documents *don't* cover well. "
        "Watch the grader mark chunks as INCORRECT and see CRAG automatically "
        "switch to Wikipedia to answer your question."
    )
