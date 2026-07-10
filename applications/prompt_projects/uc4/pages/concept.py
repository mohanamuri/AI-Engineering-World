"""UC4 — Concept page: Prompt Chaining."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Prompt Chaining")
    st.write(
        "Complex tasks overwhelm a single prompt. Prompt chaining breaks them into a sequence of "
        "focused sub-prompts — each doing one thing well — where every step's output becomes "
        "the next step's input. The result is reliably better quality than any single prompt."
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 📄 Single prompt")
            st.write(
                "One prompt handles everything: research, drafting, editing, formatting. "
                "The model must hold all of this in context simultaneously."
            )
            st.markdown("**Problems:**")
            st.markdown(
                "- Model attention is diluted across all sub-tasks\n"
                "- Early mistakes propagate to the final output\n"
                "- Hard to debug — which step went wrong?\n"
                "- Token limits constrain depth on each sub-task"
            )
            st.warning("**Result:** Adequate but shallow output on complex tasks.")

    with col2:
        with st.container(border=True):
            st.markdown("#### 🔗 Prompt chain")
            st.write(
                "The task is decomposed: Step 1 creates an outline, Step 2 drafts content, "
                "Step 3 refines and polishes. Each step is focused and deep."
            )
            st.markdown("**Benefits:**")
            st.markdown(
                "- Each step is fully focused on one concern\n"
                "- Errors are caught between steps\n"
                "- Each step can use a different system prompt\n"
                "- Intermediate outputs are inspectable"
            )
            st.success("**Result:** Significantly higher quality on complex tasks.")

    st.divider()
    st.markdown("#### The Outline → Draft → Refine pattern")

    st.code(
        """# Step 1 — Planner creates an outline
outline = llm(
    system="You are a strategic planner. Output a numbered outline only.",
    user=f"Outline this task: {task}"
)

# Step 2 — Writer expands the outline into full content
draft = llm(
    system="You are a skilled writer. Expand each point in full.",
    user=f"Task: {task}\\nOutline:\\n{outline}\\nExpand into full content:"
)

# Step 3 — Editor polishes the draft
final = llm(
    system="You are an editor. Polish for clarity, flow, and impact.",
    user=f"Polish this draft:\\n{draft}"
)
""",
        language="python",
    )

    st.divider()
    st.markdown("#### Why decomposition works")
    c1, c2, c3 = st.columns(3)
    c1.metric("Focus per step", "100%", "vs diluted attention in single prompt")
    c2.metric("Debuggability", "Per-step", "Isolate which step fails")
    c3.metric("Quality gain", "Significant", "On complex writing/analysis tasks")
