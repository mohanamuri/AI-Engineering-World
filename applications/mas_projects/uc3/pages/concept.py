"""MAS UC3 — Concept page: Debate & Judge."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Debate & Judge — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why adversarial agents find flaws that cooperative agents miss\n"
        "- How two AI agents argue opposite sides of any topic\n"
        "- What a neutral Judge does and how it evaluates arguments\n"
        "- When the debate pattern is useful in practice"
    )

    # ── Why adversarial? ─────────────────────────────────────────────────────
    st.markdown("### Why Adversarial? — Stress-Testing Ideas")

    st.markdown(
        "UC1 and UC2 use *cooperative* agents — they all work toward the same goal.\n\n"
        "But the best way to test an idea is to have someone argue against it. "
        "Courts use this: prosecution vs defence. "
        "Philosophy uses this: thesis vs antithesis. "
        "Science uses this: peer review challenges assumptions.\n\n"
        "**UC3 applies the same logic to AI: two agents argue opposite sides, "
        "then a neutral Judge evaluates the quality of each argument.**"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Cooperative agents (UC1 / UC2)**")
            st.markdown(
                "Agents collaborate toward one answer\n\n"
                "- Good for research and synthesis\n"
                "- May converge too quickly — no challenge\n"
                "- Hidden assumptions go unquestioned\n"
                "- Output tends to agree with the initial framing"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**Adversarial agents (UC3)**")
            st.markdown(
                "Agents argue opposite positions\n\n"
                "- Forces both sides to be examined\n"
                "- Surfaces trade-offs and counterarguments\n"
                "- Hidden assumptions get challenged\n"
                "- Useful for decisions, policies, and risk analysis"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Multiple Rounds of Debate")

    st.graphviz_chart("""
    digraph Debate {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        T  [label="Topic &\nPosition" fillcolor="#fce7f3" color="#ec4899"]
        Pr [label="🟦 Proponent\nArgues FOR" fillcolor="#dbeafe" color="#3b82f6"]
        Op [label="🟥 Opponent\nArgues AGAINST" fillcolor="#fef9c3" color="#dc2626"]
        Lo [label="Round 2, 3...\n(same agents respond\nto each other)" fillcolor="#f5f5f5" color="#9ca3af"]
        Ju [label="⚖️ Judge\nEvaluates both\n& decides winner" fillcolor="#f0fdf4" color="#22c55e"]

        T  -> Pr
        T  -> Op
        Pr -> Lo
        Op -> Lo
        Lo -> Ju
    }
    """)

    steps = [
        ("🟦 Proponent — argues FOR",
         "The Proponent agent is given a position to defend and instructed to argue *for* it "
         "as persuasively as possible — using logic, evidence, and examples. "
         "Its goal is not to be balanced; its goal is to win the argument."),
        ("🟥 Opponent — argues AGAINST",
         "The Opponent is given the opposite position. "
         "It reads the Proponent's argument and constructs a counterargument — "
         "identifying weaknesses, offering alternative evidence, and challenging assumptions."),
        ("Multi-round exchange",
         "For each round, the Proponent responds to the Opponent's critique, "
         "and the Opponent responds to the Proponent's defence. "
         "Arguments get more refined with each round."),
        ("⚖️ Judge — evaluates and decides",
         "The Judge reads the complete debate transcript and evaluates: "
         "Which side used stronger logic? Which had better evidence? "
         "Which argument had fewer weaknesses? "
         "The Judge declares a winner and explains why."),
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
            st.markdown("**Adversarial MAS**")
            st.write(
                "A multi-agent system where agents have *opposing* objectives — "
                "designed to challenge each other, not cooperate."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Conditional Routing**")
            st.write(
                "After each round, the system checks: more rounds needed? "
                "If yes, loop again. If max rounds reached, pass to Judge. "
                "This is routing based on a condition."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Judge**")
            st.write(
                "A neutral agent with no assigned position — "
                "it evaluates the *quality of arguments*, not whether it agrees with the conclusion."
            )

    st.success(
        "**Ready to try it?** Go to **Setup**, pick a topic and a position, set the number of debate rounds, "
        "then **Run**. Read both sides' arguments before seeing the Judge's verdict."
    )
