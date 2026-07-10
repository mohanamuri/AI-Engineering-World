"""MAS UC1 — Concept page: Supervisor Pipeline."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Supervisor Pipeline — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- What a multi-agent system (MAS) is and why it's different from a single agent\n"
        "- What a sequential pipeline means in plain English\n"
        "- How four agents hand work to each other in a fixed order\n"
        "- When a pipeline is the right pattern to use"
    )

    # ── MAS vs Single Agent ──────────────────────────────────────────────────
    st.markdown("### Single Agent vs Multi-Agent System")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Single Agent (Agent Projects)**")
            st.markdown(
                "One LLM handles everything: thinking, research, calculation, writing\n\n"
                "- Simple and fast for short tasks\n"
                "- Context grows large quickly\n"
                "- Hard to specialise or audit\n"
                "- Like asking one person to do a whole team's job"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**Multi-Agent System (MAS)**")
            st.markdown(
                "Multiple specialised agents — each does one role\n\n"
                "- Each agent is tuned for its specific job\n"
                "- Work is divided, context stays manageable\n"
                "- Clear handoffs make the process auditable\n"
                "- Like a team with defined roles"
            )

    # ── UC1 pipeline ─────────────────────────────────────────────────────────
    st.markdown("### UC1 — The Sequential Pipeline")
    st.markdown(
        "UC1 is the simplest multi-agent pattern: a **fixed sequence**, "
        "where each agent's output becomes the next agent's input. "
        "No branching, no loops — just a straight line from start to finish.\n\n"
        "Think of it like an assembly line: each station does its job and passes the part along."
    )

    st.graphviz_chart("""
    digraph Pipeline {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        T  [label="Your Topic" fillcolor="#fce7f3" color="#ec4899"]
        C  [label="🗂️ Collector\nGathers facts\n(Wikipedia)" fillcolor="#dbeafe" color="#3b82f6"]
        P  [label="🔬 Processor\nExtracts key insights\nfrom raw facts" fillcolor="#fef9c3" color="#eab308"]
        W  [label="✍️ Writer\nDrafts a structured\nresponse" fillcolor="#fff7ed" color="#f97316"]
        S  [label="🧭 Supervisor\nWrites executive\nsummary" fillcolor="#f0fdf4" color="#22c55e"]

        T -> C -> P -> W -> S
    }
    """)

    steps = [
        ("🗂️ Collector — gathers raw facts",
         "Searches Wikipedia for information about your topic. "
         "It collects the raw, unprocessed text — no interpretation yet. "
         "Output: a block of raw information."),
        ("🔬 Processor — extracts insights",
         "Reads the Collector's raw facts and extracts the key points, patterns, and insights. "
         "It doesn't write anything for the user — just structures the information. "
         "Output: a clean, structured list of insights."),
        ("✍️ Writer — drafts the response",
         "Takes the Processor's structured insights and writes a clear, readable response. "
         "Focused on quality prose — not research. "
         "Output: a well-written draft."),
        ("🧭 Supervisor — final summary",
         "Reads the Writer's draft and produces a short executive summary. "
         "Closes the pipeline with the most important takeaway. "
         "Output: the final deliverable shown to you."),
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
            st.markdown("**Sequential Pipeline**")
            st.write(
                "A fixed order of steps where A → B → C → D. "
                "No branching — the flow is predictable and auditable every time."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Handoff**")
            st.write(
                "When one agent finishes, it passes its complete output to the next agent "
                "as input. Each agent builds on what came before."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Accumulated Context**")
            st.write(
                "Each agent receives *all* previous outputs — not just the one before it. "
                "By the time the Writer acts, it has raw facts AND extracted insights."
            )

    st.success(
        "**Ready to try it?** Go to **Setup**, enter any topic you're curious about, "
        "then **Run** to watch the four agents hand off work to each other. "
        "You'll see each agent's output separately."
    )
