"""RAG UC5 — Concept page: GraphRAG."""

import streamlit as st


def render() -> None:
    st.subheader("📖 GraphRAG — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why similarity search sometimes misses the right answer\n"
        "- What a Knowledge Graph is and how it is built from your documents\n"
        "- How following entity relationships finds answers that keyword search can't\n"
        "- What BFS graph traversal means in plain English"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — Similarity Search Misses Relationships")

    st.markdown(
        "UC1–UC4 all rely on the same core idea: find chunks that are *similar* to your question. "
        "This works well for direct questions like 'What is the refund policy?'\n\n"
        "But it fails for questions that require following relationships, such as:\n\n"
        "- 'Who approves leave requests for employees in the operations department?'\n"
        "- 'Which policy governs the benefits described in the onboarding guide?'\n\n"
        "These questions require knowing **who manages what**, "
        "**which document governs which rule** — not just word similarity."
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1–UC4 — Similarity Search**")
            st.markdown(
                "Query → find similar chunks → generate\n\n"
                "- Fast\n"
                "- Works well for direct questions\n"
                "- Fails when the answer requires following a chain of relationships\n"
                "- Cannot reason about *who connects to what*"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC5 — GraphRAG**")
            st.markdown(
                "Query → extract entities → traverse graph → gather chunks → generate\n\n"
                "- Slower (graph build takes time)\n"
                "- Finds indirectly related information\n"
                "- Can follow entity chains across multiple documents\n"
                "- Shows you the graph path it took"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Build a Map, Then Follow It")

    st.graphviz_chart("""
    digraph GraphRAG {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        D  [label="Your Documents" fillcolor="#fce7f3" color="#ec4899"]
        E  [label="Entity Extraction\n(LLM per chunk)" fillcolor="#dbeafe" color="#3b82f6"]
        KG [label="Knowledge Graph\n(entities + relations)" fillcolor="#f0fdf4" color="#22c55e"]
        Q  [label="Your Question" fillcolor="#fce7f3" color="#ec4899"]
        QE [label="Extract Query\nEntities" fillcolor="#dbeafe" color="#3b82f6"]
        T  [label="Graph Traversal\n(BFS, max N hops)" fillcolor="#fef9c3" color="#eab308"]
        C  [label="Gather Relevant\nChunks" fillcolor="#e0f2fe" color="#0ea5e9"]
        A  [label="Generate Answer" fillcolor="#f0fdf4" color="#22c55e"]

        D -> E -> KG
        Q -> QE -> T
        KG -> T
        T -> C -> A
    }
    """)

    steps = [
        ("1️⃣ Upload and build the graph (one time)",
         "After uploading your documents, click **Build Knowledge Graph**. "
         "The LLM reads each chunk and extracts triples like:\n\n"
         "- `leave policy` → **governs** → `annual leave rules`\n"
         "- `hr department` → **manages** → `leave approvals`\n"
         "- `operations team` → **reports_to** → `hr department`\n\n"
         "These become nodes and edges in the graph. Each node also stores "
         "which chunks it appeared in."),
        ("2️⃣ Extract query entities",
         "When you ask a question, the LLM extracts the key entities from it. "
         "For example: 'Who approves leave for operations?' → "
         "entities: `leave`, `operations`."),
        ("3️⃣ Graph traversal (BFS)",
         "The system finds those entities in the graph and expands outward — "
         "following edges up to max_hops. "
         "Starting from `operations` → finds `hr department` (1 hop) → "
         "finds `leave approvals` (2 hops). "
         "All visited entities' chunks are collected."),
        ("4️⃣ Generate answer from graph-gathered chunks",
         "The LLM generates a final answer using the chunks discovered "
         "via graph traversal — not similarity matching. "
         "You can see the matched entities, expanded entities, and the traversal path."),
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
            st.markdown("**Knowledge Graph**")
            st.write(
                "A map of things (entities) and how they connect (relations). "
                "Think of it like a mind map drawn from your documents automatically."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**BFS (Breadth-First Search)**")
            st.write(
                "A graph traversal method. Start at one node, visit all its "
                "direct neighbours (1 hop), then their neighbours (2 hops), and so on. "
                "Controlled by the max_hops setting."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Entity Extraction**")
            st.write(
                "Using an LLM to identify names, concepts, and how they relate "
                "within a text. The output is (subject, relation, object) triples — "
                "the building blocks of the knowledge graph."
            )

    st.success(
        "**Ready to try it?** Upload documents, click **Build Knowledge Graph**, "
        "then go to Chat. Ask a relational question — something that requires "
        "knowing *who manages what* or *which policy governs which rule*. "
        "Watch the graph traversal trace appear with every answer."
    )
