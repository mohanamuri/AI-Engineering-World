"""Agent UC3 — Concept page: Reflection Agent."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Reflection Agent — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why generating one draft and stopping is rarely good enough\n"
        "- How the agent acts as its own critic — scoring its own output\n"
        "- What the Generate → Critique → Revise loop looks like\n"
        "- When this pattern is useful vs when it's overkill"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — First Drafts Are Rarely the Best")

    st.markdown(
        "UC1 and UC2 both produce an output and stop — neither one checks whether it's actually good.\n\n"
        "Think about how good writers, engineers, and analysts work:\n"
        "they **draft → review → revise**. They never submit the first version.\n\n"
        "The Reflection Agent applies the same process to AI-generated content: "
        "write a draft, critique it systematically, rewrite where needed — all automatically."
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1 / UC2 — Generate & Stop**")
            st.markdown(
                "Write answer → done\n\n"
                "- Fast: one LLM call\n"
                "- No quality check\n"
                "- First draft = final answer\n"
                "- Works fine for simple tasks"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC3 — Reflection Agent**")
            st.markdown(
                "Write → critique → revise → final\n\n"
                "- More LLM calls, but higher quality\n"
                "- Systematic quality scoring per draft\n"
                "- Low scores trigger targeted rewrites\n"
                "- You see every draft and its scores"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — The Reflection Loop")

    st.graphviz_chart("""
    digraph Reflection {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        T  [label="Your Task" fillcolor="#fce7f3" color="#ec4899"]
        G  [label="✍️ Generate\nWrite a draft" fillcolor="#dbeafe" color="#3b82f6"]
        C  [label="🔍 Critique\nScore: Clarity,\nAccuracy, Completeness" fillcolor="#fef9c3" color="#eab308" shape=diamond]
        R  [label="🔄 Revise\nTargeted rewrite" fillcolor="#fff7ed" color="#f97316"]
        F  [label="✅ Final Answer\n+ All draft scores" fillcolor="#f0fdf4" color="#22c55e"]

        T -> G -> C
        C -> R [label="Score too low"]
        R -> G [label="rewrite"]
        C -> F [label="Score passes"]
    }
    """)

    steps = [
        ("✍️ Generate — write a draft",
         "The agent writes a complete answer to your task. "
         "No tools needed — this is pure generation from the LLM."),
        ("🔍 Critique — score the draft",
         "A separate LLM call reads the draft and scores it on three dimensions (1–5 each):\n\n"
         "- **Clarity** — Is it easy to read and understand?\n"
         "- **Accuracy** — Is the content factually correct and logically sound?\n"
         "- **Completeness** — Does it fully address every part of the task?\n\n"
         "These scores are shown to you for every draft."),
        ("🔄 Revise — targeted rewrite",
         "If any score falls below the threshold, the agent gets specific feedback: "
         "*'The clarity score is low because the second paragraph is unclear — rewrite it.'* "
         "The rewrite targets the exact weakness, not the whole draft."),
        ("✅ Final answer with full history",
         "Once all scores pass (or the max revisions are reached), the final draft is shown. "
         "You can view every previous draft alongside its scores to see how it improved."),
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
            st.markdown("**Self-Critique**")
            st.write(
                "The AI evaluating its own output — not the user. "
                "It acts like a reviewer giving structured feedback on a draft."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Quality Loop**")
            st.write(
                "The cycle of: generate → score → revise → score again. "
                "It stops when the quality threshold is met or max attempts reached."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Targeted Rewrite**")
            st.write(
                "Rewriting only the part of the draft that scored poorly — "
                "not restarting from scratch. More efficient and focused."
            )

    st.success(
        "**Ready to try it?** Go to **Run** and ask for a piece of writing — "
        "an essay, explanation, or analysis. Watch the draft scores improve "
        "across revisions. Try adjusting the quality threshold in Setup."
    )
