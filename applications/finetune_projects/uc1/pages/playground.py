"""UC1 — Playground: Interactive Fine-tune vs RAG decision engine."""

import streamlit as st

from applications.finetune_projects.services.decision_engine import (
    FineTuneScenario,
    PRESET_SCENARIOS,
    should_finetune,
)
from applications.finetune_projects.uc1.constants import DECISION_RESULT_KEY


_TASK_TYPES = ["style", "classification", "factual_qa", "domain_knowledge", "instruction_following"]

_RECOMMENDATION_COLORS = {
    "Fine-tune": "success",
    "RAG": "info",
    "Both": "warning",
    "Neither — use base model": "error",
}


def _confidence_badge(confidence: str) -> str:
    icons = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
    return f"{icons.get(confidence, '')} {confidence} confidence"


def render() -> None:
    st.subheader("🧪 Playground — Fine-tune vs RAG Decision Engine")

    st.markdown(
        "Configure your scenario below. The decision engine applies a rule-based framework "
        "to recommend the right architecture — no LLM calls, pure Python logic."
    )

    # Preset loader
    preset_name = st.selectbox(
        "Load a preset scenario (optional)",
        options=["— custom —"] + list(PRESET_SCENARIOS.keys()),
        key="finetune_uc1_preset",
    )

    preset = PRESET_SCENARIOS.get(preset_name) if preset_name != "— custom —" else None

    st.divider()
    st.markdown("#### Configure Your Scenario")

    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown("**Data Availability**")
            labeled_examples = st.slider(
                "Labeled examples available",
                min_value=0, max_value=5000, step=50,
                value=preset.labeled_examples if preset else 200,
                help="Number of (input, output) training pairs you have.",
                key="finetune_uc1_labeled",
            )
            data_is_proprietary = st.checkbox(
                "Data is proprietary / confidential",
                value=preset.data_is_proprietary if preset else False,
                help="Is the training data sensitive or confidential?",
                key="finetune_uc1_proprietary",
            )

        with st.container(border=True):
            st.markdown("**Task Characteristics**")
            task_type = st.selectbox(
                "Task type",
                options=_TASK_TYPES,
                index=_TASK_TYPES.index(preset.task_type) if preset else 0,
                help="What kind of task are you solving?",
                key="finetune_uc1_task",
            )
            knowledge_changes = st.checkbox(
                "Knowledge changes frequently (weekly/monthly)",
                value=preset.knowledge_changes_frequently if preset else False,
                key="finetune_uc1_changes",
            )
            latency_critical = st.checkbox(
                "Latency critical (sub-200 ms required)",
                value=preset.latency_critical if preset else False,
                key="finetune_uc1_latency",
            )

    with col_b:
        with st.container(border=True):
            st.markdown("**Constraints**")
            gpu_available = st.checkbox(
                "GPU available for training",
                value=preset.gpu_available if preset else False,
                key="finetune_uc1_gpu",
            )
            budget = st.slider(
                "Monthly budget (USD)",
                min_value=0.0, max_value=5000.0, step=50.0,
                value=float(preset.budget_monthly_usd) if preset else 500.0,
                key="finetune_uc1_budget",
            )
            need_explainability = st.checkbox(
                "Need explainability / source citations",
                value=preset.need_explainability if preset else False,
                key="finetune_uc1_explain",
            )

        with st.container(border=True):
            st.markdown("**Quick Summary**")
            st.caption(f"Examples: {labeled_examples} | Task: {task_type}")
            st.caption(f"Proprietary: {'Yes' if data_is_proprietary else 'No'} | GPU: {'Yes' if gpu_available else 'No'}")
            st.caption(f"Knowledge fresh: {'Yes' if knowledge_changes else 'No'} | Latency critical: {'Yes' if latency_critical else 'No'}")

    st.divider()

    if st.button("Run Decision Engine", type="primary"):
        scenario = FineTuneScenario(
            labeled_examples=labeled_examples,
            data_is_proprietary=data_is_proprietary,
            task_type=task_type,
            knowledge_changes_frequently=knowledge_changes,
            latency_critical=latency_critical,
            gpu_available=gpu_available,
            budget_monthly_usd=budget,
            need_explainability=need_explainability,
        )
        decision = should_finetune(scenario)
        st.session_state[DECISION_RESULT_KEY] = decision
        st.rerun()

    decision = st.session_state.get(DECISION_RESULT_KEY)
    if decision:
        alert_fn = getattr(st, _RECOMMENDATION_COLORS.get(decision.recommendation, "info"))
        alert_fn(
            f"**Recommendation: {decision.recommendation}**  —  {_confidence_badge(decision.confidence)}\n\n"
            f"{decision.primary_reason}"
        )

        col_pros, col_cons = st.columns(2)
        with col_pros:
            with st.container(border=True):
                st.markdown("**Pros**")
                for pro in decision.pros:
                    st.markdown(f"- {pro}")
        with col_cons:
            with st.container(border=True):
                st.markdown("**Cons**")
                for con in decision.cons:
                    st.markdown(f"- {con}")

        with st.container(border=True):
            st.markdown("**When to reconsider**")
            st.write(decision.when_to_reconsider)

    st.info(
        "**Try it:** Load each preset to see how real-world scenarios map to recommendations. "
        "Then tweak sliders — e.g. drag labeled_examples above 500 and watch the recommendation change."
    )
