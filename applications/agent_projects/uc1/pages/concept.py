"""Agent UC1 — Concept page: ReAct Agent."""

import streamlit as st


def render() -> None:
    st.subheader("📖 ReAct Agent — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- What an AI agent is and how it's different from a plain chatbot\n"
        "- What 'tools' are and why the AI needs them\n"
        "- How the ReAct loop works: Reason → Act → Observe → Repeat\n"
        "- Why you can see every step the agent takes — no black box"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — A Plain LLM Can Only Talk, Not Do")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**A plain LLM (chatbot)**")
            st.markdown(
                "Ask: *'What is 1,247 × 389?'*\n\n"
                "- LLM guesses: **484,883** ← wrong (correct is 485,083)\n\n"
                "Ask: *'What is today's temperature in London?'*\n\n"
                "- LLM makes up a number — it can't access live data\n\n"
                "**LLMs are great at language. They're poor at real-world tasks.**"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**An AI agent**")
            st.markdown(
                "Ask: *'What is 1,247 × 389?'*\n\n"
                "- Agent uses Calculator tool → **485,083** ← correct\n\n"
                "Ask: *'What did Einstein contribute to physics?'*\n\n"
                "- Agent uses Wikipedia tool → retrieves actual article → answers accurately\n\n"
                "**An agent can act in the world — it's not limited to what it memorised.**"
            )

    # ── What is ReAct ────────────────────────────────────────────────────────
    st.markdown("### What Is ReAct?")
    st.markdown(
        "**ReAct = Reason + Act** — a pattern for how an AI agent thinks and works.\n\n"
        "Instead of jumping straight to an answer, the agent goes through a loop:\n"
        "1. **Reason** — think about what it knows and what it needs\n"
        "2. **Act** — call a tool to get more information\n"
        "3. **Observe** — read the tool's result\n"
        "4. **Reason again** — is this enough to answer? If not, call another tool\n"
        "5. **Answer** — once it has enough information, write the final response\n\n"
        "This loop is called the **ReAct loop**. You'll see every iteration in the app."
    )

    # ── Visual ───────────────────────────────────────────────────────────────
    st.graphviz_chart("""
    digraph ReAct {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        T  [label="Your Task" fillcolor="#fce7f3" color="#ec4899"]
        R1 [label="🤔 Reason\nWhat do I need?" fillcolor="#dbeafe" color="#3b82f6"]
        A  [label="🔧 Act\nCall a Tool" fillcolor="#fef9c3" color="#eab308"]
        O  [label="📋 Observe\nRead Tool Result" fillcolor="#fff7ed" color="#f97316"]
        R2 [label="🤔 Reason again\nDo I have enough?" fillcolor="#dbeafe" color="#3b82f6" shape=diamond]
        An [label="✅ Answer" fillcolor="#f0fdf4" color="#22c55e"]

        T  -> R1 -> A -> O -> R2
        R2 -> An [label="Yes"]
        R2 -> A  [label="No — use another tool"]
    }
    """)

    steps = [
        ("🤔 Reason",
         "The agent reads your task and thinks: *'What do I know? What do I need to find out? "
         "Which tool should I use?'* This reasoning is shown in the trace as a 'thought'."),
        ("🔧 Act — call a tool",
         "The agent calls one of its available tools:\n"
         "- **Calculator** — evaluates math safely\n"
         "- **Wikipedia** — looks up facts from Wikipedia\n\n"
         "It passes specific inputs — the exact math expression, or the exact search term."),
        ("📋 Observe — read the result",
         "The tool returns its result. The agent reads it exactly as you would read a search result. "
         "This result is added to the agent's context."),
        ("🔁 Reason again — loop or answer?",
         "The agent decides: *'Do I now have enough to answer the original question?'* "
         "If yes → write the final answer. If no → reason about the next tool call."),
    ]
    for emoji_title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{emoji_title}**")
            st.write(body)

    # ── Key terms ────────────────────────────────────────────────────────────
    st.markdown("### Key Terms (Plain English)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("**Agent**")
            st.write(
                "An AI that can decide what to do, take actions (tool calls), "
                "and keep going until a task is complete — not just generate one response."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Tool**")
            st.write(
                "A function the agent can call to interact with the world: "
                "calculate something, look something up, read a file, call an API. "
                "Tools give the agent real-world capabilities."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Reasoning Trace**")
            st.write(
                "The full log of every thought, tool call, and observation "
                "the agent made to reach its answer. "
                "It makes the agent's process completely transparent."
            )

    st.success(
        "**Ready to try it?** Go to **Setup** to pick your tools, "
        "then **Run** to ask a question. Watch the full reasoning trace — "
        "🤔 Thought → 🔧 Tool Call → 📋 Result → ✅ Answer."
    )
