"""UC1 — Compare: Two scenarios side by side to see how one factor flips the recommendation."""

import streamlit as st

from applications.finetune_projects.services.decision_engine import (
    FineTuneScenario,
    PRESET_SCENARIOS,
    should_finetune,
)

_TASK_TYPES = ["style", "classification", "factual_qa", "domain_knowledge", "instruction_following"]

_REC_COLOR = {
    "Fine-tune": "🟢",
    "RAG": "🔵",
    "Both": "🟡",
    "Neither — use base model": "🔴",
}


def _scenario_form(prefix: str, preset_key: str, label: str) -> FineTuneScenario:
    """Render a compact scenario form and return a FineTuneScenario."""
    preset_name = st.selectbox(
        f"Preset ({label})",
        options=["— custom —"] + list(PRESET_SCENARIOS.keys()),
        key=f"{prefix}_preset",
    )
    preset = PRESET_SCENARIOS.get(preset_name) if preset_name != "— custom —" else None

    labeled = st.slider(
        "Labeled examples", 0, 5000, step=50,
        value=preset.labeled_examples if preset else 200,
        key=f"{prefix}_labeled",
    )
    task = st.selectbox(
        "Task type", _TASK_TYPES,
        index=_TASK_TYPES.index(preset.task_type) if preset else 0,
        key=f"{prefix}_task",
    )
    proprietary = st.checkbox(
        "Proprietary data",
        value=preset.data_is_proprietary if preset else False,
        key=f"{prefix}_prop",
    )
    changes = st.checkbox(
        "Knowledge changes frequently",
        value=preset.knowledge_changes_frequently if preset else False,
        key=f"{prefix}_changes",
    )
    latency = st.checkbox(
        "Latency critical",
        value=preset.latency_critical if preset else False,
        key=f"{prefix}_latency",
    )
    gpu = st.checkbox(
        "GPU available",
        value=preset.gpu_available if preset else False,
        key=f"{prefix}_gpu",
    )
    budget = st.slider(
        "Budget (USD/mo)", 0.0, 5000.0, step=50.0,
        value=float(preset.budget_monthly_usd) if preset else 500.0,
        key=f"{prefix}_budget",
    )
    explain = st.checkbox(
        "Need explainability",
        value=preset.need_explainability if preset else False,
        key=f"{prefix}_explain",
    )

    return FineTuneScenario(
        labeled_examples=labeled,
        data_is_proprietary=proprietary,
        task_type=task,
        knowledge_changes_frequently=changes,
        latency_critical=latency,
        gpu_available=gpu,
        budget_monthly_usd=budget,
        need_explainability=explain,
    )


def render() -> None:
    st.subheader("⚖️ Compare — Two Scenarios Side by Side")

    st.markdown(
        "Configure two different scenarios and run the decision engine on both. "
        "Try changing a single factor (e.g. examples from 50 → 600) to see how it flips the recommendation."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Scenario A")
        with st.container(border=True):
            scenario_a = _scenario_form("finetune_uc1_cmp_a", "preset_a", "A")

    with col2:
        st.markdown("### Scenario B")
        with st.container(border=True):
            scenario_b = _scenario_form("finetune_uc1_cmp_b", "preset_b", "B")

    if st.button("Compare both scenarios", type="primary"):
        decision_a = should_finetune(scenario_a)
        decision_b = should_finetune(scenario_b)

        st.divider()
        st.markdown("### Results")
        res_col1, res_col2 = st.columns(2)

        with res_col1:
            icon = _REC_COLOR.get(decision_a.recommendation, "⚪")
            st.markdown(f"**Scenario A: {icon} {decision_a.recommendation}**")
            st.caption(f"Confidence: {decision_a.confidence}")
            with st.container(border=True):
                st.markdown("**Why:**")
                st.write(decision_a.primary_reason)
            with st.expander("Pros / Cons"):
                st.markdown("**Pros:**")
                for p in decision_a.pros:
                    st.markdown(f"- {p}")
                st.markdown("**Cons:**")
                for c in decision_a.cons:
                    st.markdown(f"- {c}")

        with res_col2:
            icon = _REC_COLOR.get(decision_b.recommendation, "⚪")
            st.markdown(f"**Scenario B: {icon} {decision_b.recommendation}**")
            st.caption(f"Confidence: {decision_b.confidence}")
            with st.container(border=True):
                st.markdown("**Why:**")
                st.write(decision_b.primary_reason)
            with st.expander("Pros / Cons"):
                st.markdown("**Pros:**")
                for p in decision_b.pros:
                    st.markdown(f"- {p}")
                st.markdown("**Cons:**")
                for c in decision_b.cons:
                    st.markdown(f"- {c}")

        st.divider()
        if decision_a.recommendation != decision_b.recommendation:
            st.warning(
                f"The two scenarios lead to **different recommendations** "
                f"({decision_a.recommendation} vs {decision_b.recommendation}). "
                "This shows how sensitive the decision is to your specific constraints. "
                "Identify the key differentiating factor in your scenario."
            )
        else:
            st.success(
                f"Both scenarios converge on **{decision_a.recommendation}**. "
                "The recommendation is robust across these two configurations."
            )

        st.markdown("### Factor Comparison")
        st.table({
            "Factor": [
                "Labeled examples", "Task type", "Proprietary data",
                "Knowledge changes", "Latency critical", "GPU available", "Budget (USD/mo)",
            ],
            "Scenario A": [
                scenario_a.labeled_examples, scenario_a.task_type,
                "Yes" if scenario_a.data_is_proprietary else "No",
                "Yes" if scenario_a.knowledge_changes_frequently else "No",
                "Yes" if scenario_a.latency_critical else "No",
                "Yes" if scenario_a.gpu_available else "No",
                f"${scenario_a.budget_monthly_usd:,.0f}",
            ],
            "Scenario B": [
                scenario_b.labeled_examples, scenario_b.task_type,
                "Yes" if scenario_b.data_is_proprietary else "No",
                "Yes" if scenario_b.knowledge_changes_frequently else "No",
                "Yes" if scenario_b.latency_critical else "No",
                "Yes" if scenario_b.gpu_available else "No",
                f"${scenario_b.budget_monthly_usd:,.0f}",
            ],
        })
