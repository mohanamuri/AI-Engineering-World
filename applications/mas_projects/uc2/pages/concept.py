"""MAS UC2 — Concept page: Parallel Agents."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Parallel Agents — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why one perspective is often not enough for complex questions\n"
        "- How multiple agents can tackle the same task simultaneously\n"
        "- What Fan-out / Fan-in means in plain English\n"
        "- How an Aggregator combines diverse viewpoints into one answer"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — One Agent, One Blind Spot")

    st.markdown(
        "UC1's pipeline processes a topic through a fixed sequence — "
        "one perspective, one angle.\n\n"
        "Imagine asking: *'Should my company adopt microservices?'*\n\n"
        "- A single agent might give a balanced answer — but it's one view\n"
        "- It might miss the critic's objections, or the creative alternatives\n"
        "- A panel of specialists — each with a different lens — gives richer coverage\n\n"
        "**UC2 runs three specialist agents in parallel, each with a distinct perspective.**"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1 — Sequential pipeline**")
            st.markdown(
                "One stream of processing, one output style\n\n"
                "- Good depth on one angle\n"
                "- Can miss alternative views\n"
                "- Output reflects one coherent narrative"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC2 — Parallel agents**")
            st.markdown(
                "Three agents work simultaneously, each on the same task\n\n"
                "- Three distinct perspectives\n"
                "- Blind spots in one agent are covered by another\n"
                "- Aggregator merges all three into a richer answer"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Fan-Out and Fan-In")

    st.graphviz_chart("""
    digraph Parallel {
        rankdir=TB
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        T  [label="Your Task" fillcolor="#fce7f3" color="#ec4899"]
        F  [label="Facts Agent\nObjective facts\n& data" fillcolor="#dbeafe" color="#3b82f6"]
        C  [label="Critic Agent\nRisks, flaws\n& counterpoints" fillcolor="#fef9c3" color="#eab308"]
        Cr [label="Creative Agent\nAlternatives &\nunconventional angles" fillcolor="#fff7ed" color="#f97316"]
        Ag [label="🔀 Aggregator\nMerges all three\nperspectives" fillcolor="#f0fdf4" color="#22c55e"]
        An [label="✅ Final Answer" fillcolor="#e0f2fe" color="#0ea5e9"]

        T -> F
        T -> C
        T -> Cr
        F -> Ag
        C -> Ag
        Cr -> Ag
        Ag -> An
    }
    """)

    steps = [
        ("Fan-out — same task, three agents",
         "The same task is sent to three agents simultaneously. "
         "Each agent has a different system prompt that locks in its perspective:\n"
         "- **Facts Agent** — only objective information and verifiable data\n"
         "- **Critic Agent** — only risks, flaws, and counterarguments\n"
         "- **Creative Agent** — only alternatives and unconventional ideas\n\n"
         "The agents don't know about each other — they work independently."),
        ("Fan-in — Aggregator merges outputs",
         "Once all three agents are done, the Aggregator reads all three outputs "
         "and writes one coherent answer that incorporates the facts, critiques, and alternatives. "
         "The final answer is richer and more balanced than any single agent could produce."),
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
            st.markdown("**Fan-out**")
            st.write(
                "Sending the same input to multiple agents at the same time — "
                "like distributing copies of a document to a panel of reviewers."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Fan-in**")
            st.write(
                "Collecting all outputs from parallel agents and merging them — "
                "like a panel discussion where all reviewers share findings before writing the report."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Aggregator**")
            st.write(
                "The agent whose only job is to read multiple outputs and synthesise them "
                "into one coherent, balanced response."
            )

    st.success(
        "**Ready to try it?** Go to **Setup**, enter any topic or decision question, "
        "then **Run**. Watch three agents work simultaneously — "
        "then see how the Aggregator weaves their outputs into one answer."
    )
