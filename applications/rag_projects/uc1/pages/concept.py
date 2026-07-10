"""RAG UC1 — Concept page: Multi-Document RAG."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Multi-Document RAG — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- What RAG means and why it exists\n"
        "- How your documents get turned into something the AI can search\n"
        "- How the AI finds the right answer without making things up\n"
        "- Key terms explained in plain English before you see them in the app"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Without RAG**")
            st.markdown(
                "Imagine you have 50 company policy PDFs, hundreds of pages each. "
                "Someone asks: *'What is the leave policy for contractors?'*\n\n"
                "- You search manually — slow and error-prone\n"
                "- You ask ChatGPT — it guesses, it may be wrong\n"
                "- You ctrl+F each PDF — painful and incomplete\n\n"
                "**The AI doesn't know your documents.**"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**With RAG**")
            st.markdown(
                "You upload your documents once. The system reads and indexes them.\n\n"
                "- Ask any question in plain English\n"
                "- The AI finds the relevant passages from *your* documents\n"
                "- The answer is backed by actual source text — no guessing\n\n"
                "**The AI answers using your documents, not its imagination.**"
            )

    # ── What RAG means ───────────────────────────────────────────────────────
    st.markdown("### What Does RAG Stand For?")
    st.markdown(
        "**RAG = Retrieval-Augmented Generation**\n\n"
        "Breaking it down in plain English:\n"
        "- **Retrieval** — *Find* the relevant passages from your documents\n"
        "- **Augmented** — *Add* those passages to the AI's context\n"
        "- **Generation** — *Generate* an answer using that context\n\n"
        "Think of it like this: instead of asking an AI to remember your documents "
        "(it can't), you hand it the relevant pages every time it needs to answer."
    )

    # ── How it works — Visual ────────────────────────────────────────────────
    st.markdown("### How It Works — Step by Step")

    st.graphviz_chart("""
    digraph RAG {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        D [label="Your Documents\n(PDF, TXT, DOCX)" fillcolor="#dbeafe" color="#3b82f6"]
        C [label="Split into\nSmall Chunks" fillcolor="#e0f2fe" color="#0ea5e9"]
        E [label="Convert Each Chunk\nto an Embedding\n(fingerprint)" fillcolor="#f0fdf4" color="#22c55e"]
        V [label="Store in\nVector Database" fillcolor="#fef9c3" color="#eab308"]
        Q [label="Your Question" fillcolor="#fce7f3" color="#ec4899"]
        R [label="Find Most\nSimilar Chunks" fillcolor="#fff7ed" color="#f97316"]
        A [label="AI Reads Chunks\n& Writes Answer" fillcolor="#f0fdf4" color="#22c55e"]

        D -> C -> E -> V
        Q -> R
        V -> R
        R -> A
    }
    """)

    steps = [
        ("1️⃣ Split into chunks",
         "Your documents are cut into small, paragraph-sized pieces called **chunks**. "
         "This makes searching faster and more precise than searching whole pages."),
        ("2️⃣ Convert to embeddings",
         "Each chunk is converted into a list of numbers — called an **embedding** — "
         "that captures its *meaning*. Think of it as a unique fingerprint for each paragraph. "
         "Similar paragraphs get similar fingerprints."),
        ("3️⃣ Store in a vector database",
         "All the embeddings are stored in a **vector database** (ChromaDB in this app). "
         "This is a special index that can find similar fingerprints very quickly."),
        ("4️⃣ You ask a question",
         "Your question is also converted to an embedding (fingerprint). "
         "The system then searches the database for chunks with similar fingerprints — "
         "i.e., chunks that mean something close to what you asked."),
        ("5️⃣ AI writes the answer",
         "The top matching chunks are handed to the AI along with your question. "
         "The AI reads those chunks and writes an answer — **only using what's in the chunks**. "
         "No hallucination, no guessing from general knowledge."),
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
            st.markdown("**Chunk**")
            st.write("A small piece of a document — usually a paragraph or a few sentences. "
                     "Searching small pieces is more accurate than searching full pages.")
    with col_b:
        with st.container(border=True):
            st.markdown("**Embedding**")
            st.write("A list of numbers that represents the *meaning* of text. "
                     "Two sentences that mean the same thing have similar numbers, "
                     "even if the words are different.")
    with col_c:
        with st.container(border=True):
            st.markdown("**Vector Store**")
            st.write("A special database that stores embeddings and can find "
                     "the most similar ones in milliseconds. ChromaDB is the one used here.")

    st.success(
        "**Ready to try it?** Go to **Upload Docs** to load your documents, "
        "then **Chat** to ask questions. Every answer will show you exactly which "
        "document it came from."
    )
