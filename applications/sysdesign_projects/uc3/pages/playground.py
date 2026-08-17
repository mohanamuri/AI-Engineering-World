"""UC3 — Playground: Architecture pattern recommendation engine."""

import streamlit as st

from applications.sysdesign_projects.services.arch_patterns import (
    ArchRequirements,
    PATTERNS,
    get_pattern_recommendation,
)
from applications.sysdesign_projects.uc3.constants import ARCH_RESULT_KEY


def _render_pattern_card(pattern, expanded: bool = True) -> None:
    with st.expander(f"**{pattern.name}** — {pattern.rps_range} | {pattern.estimated_cost}", expanded=expanded):
        st.code(pattern.diagram, language=None)
        st.markdown(f"*{pattern.description}*")
        st.markdown(f"**Best for:** {pattern.best_for}")

        col_comp, col_trade = st.columns(2)
        with col_comp:
            st.markdown("**Components:**")
            for comp in pattern.components:
                st.markdown(
                    f"- **{comp.name}** ({comp.cost_tier}) — {comp.purpose}  \n"
                    f"  `{', '.join(comp.examples)}`"
                )
        with col_trade:
            col_p, col_c = st.columns(2)
            with col_p:
                st.markdown("**Pros:**")
                for p in pattern.pros:
                    st.markdown(f"- {p}")
            with col_c:
                st.markdown("**Cons:**")
                for c in pattern.cons:
                    st.markdown(f"- {c}")


def render() -> None:
    st.subheader("🧪 Playground — Architecture Pattern Recommender")

    st.markdown("Enter your system requirements and get a recommended architecture pattern.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Traffic & Performance**")
        expected_rps = st.number_input(
            "Expected RPS (requests per second)",
            min_value=0.1, max_value=10000.0, value=10.0, step=1.0,
            key="sysdesign_uc3_rps",
        )
        latency_budget_ms = st.number_input(
            "Max acceptable latency (ms)",
            min_value=100, max_value=30000, value=2000, step=100,
            key="sysdesign_uc3_latency",
        )
        data_volume_gb = st.number_input(
            "Knowledge base size (GB)",
            min_value=0.01, max_value=1000.0, value=1.0, step=0.5,
            key="sysdesign_uc3_data",
        )

    with col2:
        st.markdown("**Requirements**")
        need_global = st.checkbox(
            "Global distribution required (multi-region / CDN)",
            value=False, key="sysdesign_uc3_global",
        )
        multi_tenant = st.checkbox(
            "Multi-tenant (serving multiple organisations)",
            value=False, key="sysdesign_uc3_multitenant",
        )
        compliance = st.checkbox(
            "Compliance required (HIPAA / GDPR / SOC2)",
            value=False, key="sysdesign_uc3_compliance",
        )
        budget_tier = st.selectbox(
            "Budget tier",
            ["startup", "growth", "enterprise"],
            index=0, key="sysdesign_uc3_budget",
        )

    req = ArchRequirements(
        expected_rps=float(expected_rps),
        avg_latency_budget_ms=float(latency_budget_ms),
        need_global_distribution=need_global,
        data_volume_gb=float(data_volume_gb),
        multi_tenant=multi_tenant,
        compliance_required=compliance,
        budget_tier=budget_tier,
    )

    pattern, reasons = get_pattern_recommendation(req)

    # Save result
    st.session_state[ARCH_RESULT_KEY] = {"pattern": pattern, "reasons": reasons, "req": req}

    st.divider()
    st.markdown("### Recommendation")

    st.success(f"**Recommended: {pattern.name}**")

    st.markdown("**Why this pattern:**")
    for r in reasons:
        st.markdown(f"- {r}")

    _render_pattern_card(pattern, expanded=True)

    st.divider()
    st.markdown("### All Patterns for Reference")
    st.caption("Expand any pattern to see its full details.")

    for key, p in PATTERNS.items():
        if p.name != pattern.name:
            _render_pattern_card(p, expanded=False)
