"""Agent UC4 — Concept page: Multi-Agent Supervisor."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Multi-Agent Supervisor — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why one agent doing everything has limits\n"
        "- How a team of specialist agents works better than a generalist\n"
        "- What the Supervisor pattern does — routing work to the right specialist\n"
        "- How this connects to multi-agent systems (MAS)"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — One Agent Doing Everything")

    st.markdown(
        "UC1–UC3 each use a single LLM as the agent — one entity doing all the thinking, "
        "researching, calculating, and writing.\n\n"
        "Think of a solo consultant who has to research the market, run the numbers, "
        "write the report, and present the findings — all alone. "
        "Compared to a team with a researcher, an analyst, and a writer, "
        "the solo consultant is slower and more error-prone.\n\n"
        "**UC4 builds a small team of specialist agents — each excellent at one thing.**"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1–UC3 — Single Agent**")
            st.markdown(
                "One LLM does everything\n\n"
                "- Simpler to set up\n"
                "- Context grows large quickly\n"
                "- Generalist: decent at everything, expert at nothing\n"
                "- Harder to specialise per task type"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC4 — Multi-Agent Supervisor**")
            st.markdown(
                "Supervisor + 3 specialist agents\n\n"
                "- Each agent has one focused role\n"
                "- Supervisor reads task, routes to right specialist\n"
                "- Specialists use tailored system prompts\n"
                "- Result: better quality, clearer separation of concerns"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Supervisor Routes, Specialists Deliver")

    st.graphviz_chart("""
    digraph MultiAgent {
        rankdir=TB
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        T  [label="Your Task" fillcolor="#fce7f3" color="#ec4899"]
        Su [label="🧭 Supervisor\nReads task, routes\nto right specialist" fillcolor="#dbeafe" color="#3b82f6"]
        Re [label="🔍 Researcher\n(Wikipedia)" fillcolor="#fef9c3" color="#eab308"]
        An [label="🧮 Analyst\n(Calculator)" fillcolor="#fff7ed" color="#f97316"]
        Wr [label="✍️ Writer\n(Final synthesis)" fillcolor="#f0fdf4" color="#22c55e"]
        Fi [label="✅ Final Answer" fillcolor="#e0f2fe" color="#0ea5e9"]

        T  -> Su
        Su -> Re [label="needs facts"]
        Su -> An [label="needs numbers"]
        Re -> Su [label="result"]
        An -> Su [label="result"]
        Su -> Wr [label="enough info"]
        Wr -> Fi
    }
    """)

    steps = [
        ("🧭 Supervisor — the router",
         "The Supervisor reads your task and decides who to call next: "
         "*'This needs research — call the Researcher.'* "
         "After each specialist finishes, the Supervisor re-evaluates: "
         "*'Do we have enough to write the answer?'* If not, it routes to another specialist."),
        ("🔍 Researcher — facts specialist",
         "The Researcher's only job is looking up information from Wikipedia. "
         "It has a system prompt focused on factual retrieval — "
         "no calculations, no writing, just finding accurate information."),
        ("🧮 Analyst — numbers specialist",
         "The Analyst's only job is mathematical reasoning and calculation using the Calculator tool. "
         "It receives the Researcher's findings and crunches the numbers."),
        ("✍️ Writer — synthesis specialist",
         "The Writer's job is producing the final, polished answer. "
         "It reads everything the Researcher found and the Analyst calculated, "
         "and writes a coherent, well-structured response."),
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
            st.markdown("**Supervisor Pattern**")
            st.write(
                "A central agent that reads the task, decides which specialist to use, "
                "collects results, and decides when the task is complete."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Specialist Agent**")
            st.write(
                "An agent with a narrow, focused role and a system prompt optimised for it. "
                "A specialist does one thing — but does it better than a generalist."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Dynamic Routing**")
            st.write(
                "The Supervisor doesn't follow a fixed script — "
                "it dynamically chooses which specialist to call next based on "
                "what's been done and what's still needed."
            )

    st.success(
        "**Ready to try it?** Go to **Run** and ask a question that needs both "
        "research *and* calculation — e.g. *'What is the GDP per capita of Germany "
        "divided by France's population?'* Watch the Supervisor route between specialists."
    )
