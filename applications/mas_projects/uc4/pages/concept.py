"""MAS UC4 — Concept page: Research Team."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Research Team — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- How four specialist agents work as a real research team\n"
        "- What iterative research means — and why it's more thorough\n"
        "- How shared memory lets agents build on each other's findings\n"
        "- Why this is the most capable MAS pattern in the platform"
    )

    # ── What makes this different ─────────────────────────────────────────────
    st.markdown("### The Most Complete MAS Pattern")

    st.markdown(
        "UC1 = sequential pipeline (fixed stages)\n"
        "UC2 = parallel agents (same question, different angles)\n"
        "UC3 = adversarial agents (opposing positions)\n\n"
        "**UC4 = a full research team with iterative research and shared memory.**\n\n"
        "Imagine a real research project: a Project Manager breaks it into questions, "
        "a Researcher answers each one, an Analyst synthesises the findings, "
        "and a Writer produces the final report. "
        "That's exactly what UC4 does — with four AI agents."
    )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — The Research Team")

    st.graphviz_chart("""
    digraph ResearchTeam {
        rankdir=TB
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        Q  [label="Complex Query" fillcolor="#fce7f3" color="#ec4899"]
        Pl [label="📋 Planner\nBreaks query into\nresearch questions" fillcolor="#dbeafe" color="#3b82f6"]
        Re [label="🔎 Researcher\nAnswers each question\n(Wikipedia loop)" fillcolor="#fef9c3" color="#eab308"]
        An [label="📊 Analyst\nSynthesises all\nresearch findings" fillcolor="#fff7ed" color="#f97316"]
        Wr [label="📝 Writer\nProduces structured\nfinal report" fillcolor="#f0fdf4" color="#22c55e"]

        Q  -> Pl
        Pl -> Re [label="question 1, 2, 3..."]
        Re -> Re [label="loop per question"]
        Re -> An [label="all findings"]
        An -> Wr
    }
    """)

    steps = [
        ("📋 Planner — decomposes the query",
         "Reads your complex question and breaks it into 3–5 focused research questions. "
         "Example: *'Tell me about electric vehicles'* becomes:\n"
         "1. What is the current global EV market share?\n"
         "2. What are the main battery technologies used?\n"
         "3. What are the key environmental benefits and concerns?\n\n"
         "Good decomposition is the key to good research."),
        ("🔎 Researcher — iterative lookup loop",
         "For *each* research question, the Researcher searches Wikipedia and records findings. "
         "It runs in a loop — one Wikipedia lookup per question — "
         "accumulating findings in shared memory before handing all results to the Analyst. "
         "This is the *iterative research* pattern."),
        ("📊 Analyst — synthesises findings",
         "Reads all the Researcher's findings and extracts cross-cutting themes, "
         "patterns, and contradictions. Produces a structured analysis — not a report, just the synthesis layer."),
        ("📝 Writer — final structured report",
         "Takes the Analyst's synthesis and writes a comprehensive, well-structured report "
         "with headings, key findings, and a conclusion. "
         "This is the final output shown to you."),
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
            st.markdown("**Iterative Research**")
            st.write(
                "The Researcher node is called once per question — in a loop. "
                "Each iteration adds to shared memory, building a richer knowledge base before analysis."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Shared Memory**")
            st.write(
                "A shared data store that all agents can read from. "
                "When the Researcher adds a finding, the Analyst can read it. "
                "This is how agents build on each other's work."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Query Decomposition**")
            st.write(
                "Breaking one complex question into several simpler, focused questions "
                "that can each be researched independently — then synthesised together."
            )

    st.success(
        "**Ready to try it?** Go to **Setup**, enter a complex research topic, "
        "then **Run**. You'll see the Planner's research questions, "
        "each research finding, the analysis, and the final report — step by step."
    )
