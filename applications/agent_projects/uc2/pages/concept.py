"""Agent UC2 — Concept page: Plan-and-Execute Agent."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Plan-and-Execute Agent — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why the ReAct agent (UC1) struggles with complex, multi-step tasks\n"
        "- What separating 'planning' from 'doing' achieves\n"
        "- How the Planner → Executor → Responder pattern works\n"
        "- When to use this pattern instead of ReAct"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem with ReAct — It's Reactive, Not Proactive")

    st.markdown(
        "UC1's ReAct agent decides what to do one step at a time — reactive, no big picture.\n\n"
        "Imagine asking: *'Compare the population of France, Germany, and Japan, "
        "then calculate which two have the closest difference.'*\n\n"
        "A ReAct agent might:\n"
        "- Look up France → look up Germany → stop and answer prematurely\n"
        "- Forget to look up Japan before calculating\n"
        "- Take 6 steps when 3 would do — no global plan\n\n"
        "**Without a plan, complex tasks go off-track.**"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**UC1 — ReAct (reactive)**")
            st.markdown(
                "Decide one step at a time\n\n"
                "- Good for simple tasks\n"
                "- No global view of the task\n"
                "- Can lose track on multi-step work\n"
                "- Planner and executor are the same LLM call"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**UC2 — Plan-and-Execute**")
            st.markdown(
                "Plan the whole task first, then execute\n\n"
                "- Knows all steps before starting\n"
                "- Executor focuses only on one step at a time\n"
                "- Responder synthesises all results at the end\n"
                "- Three separate roles: Planner, Executor, Responder"
            )

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("### How It Works — Plan First, Execute Second")

    st.graphviz_chart("""
    digraph PlanExecute {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        T  [label="Your Task" fillcolor="#fce7f3" color="#ec4899"]
        Pl [label="📝 Planner\nCreates numbered\nstep-by-step plan" fillcolor="#dbeafe" color="#3b82f6"]
        Ex [label="⚙️ Executor\nRuns each step\n(calls tools)" fillcolor="#fef9c3" color="#eab308"]
        Re [label="📊 Responder\nSynthesises all\nstep results" fillcolor="#f0fdf4" color="#22c55e"]
        An [label="✅ Final Answer" fillcolor="#e0f2fe" color="#0ea5e9"]

        T  -> Pl
        Pl -> Ex [label="Step 1, 2, 3..."]
        Ex -> Ex [label="repeat per step"]
        Ex -> Re [label="all results"]
        Re -> An
    }
    """)

    steps = [
        ("📝 Step 1 — Planner creates a numbered plan",
         "The Planner LLM reads your task and writes a complete numbered plan: "
         "*'Step 1: Look up population of France. Step 2: Look up Germany. Step 3: Calculate difference...'* "
         "The Planner knows the full task structure before any tool is called."),
        ("⚙️ Step 2 — Executor runs each step",
         "The Executor works through the plan one step at a time. "
         "For each step: it reads the step instruction, calls the right tool, records the result. "
         "It doesn't decide what to do next — the plan already decided that."),
        ("📊 Step 3 — Responder synthesises",
         "Once all steps are complete, the Responder reads the entire plan "
         "plus all step results and writes a coherent final answer — "
         "pulling together everything the Executor found."),
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
            st.markdown("**Planner**")
            st.write(
                "The LLM call that reads the task and writes a numbered plan. "
                "It thinks strategically — it doesn't do any research itself."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Executor**")
            st.write(
                "The role that runs each step of the plan — calling tools, "
                "recording results. It focuses on one step at a time, not the big picture."
            )
    with col_c:
        with st.container(border=True):
            st.markdown("**Responder**")
            st.write(
                "The final LLM call that reads all step results and writes "
                "one coherent answer. It synthesises, not researches."
            )

    st.success(
        "**Ready to try it?** Go to **Run** and ask a multi-part question — "
        "something that requires 3 or more pieces of information. "
        "You'll see the plan the agent created before it started any tool calls."
    )
