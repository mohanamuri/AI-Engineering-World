"""UC1 — Compare: Side-by-side comparison of two latency configurations."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from applications.sysdesign_projects.services.latency_calculator import (
    LatencyBudget,
    PRESET_CONFIGS,
)


CATEGORY_COLORS = {
    "Infrastructure": "#636EFA",
    "ML": "#EF553B",
    "Retrieval": "#00CC96",
    "LLM": "#AB63FA",
}


def _build_grouped_bar(budget_a: LatencyBudget, name_a: str,
                        budget_b: LatencyBudget, name_b: str) -> go.Figure:
    bd_a = {item["stage"]: item["ms"] for item in budget_a.breakdown()}
    bd_b = {item["stage"]: item["ms"] for item in budget_b.breakdown()}

    stages = list(bd_a.keys())

    fig = go.Figure(data=[
        go.Bar(name=name_a, x=stages, y=[bd_a[s] for s in stages], marker_color="#636EFA"),
        go.Bar(name=name_b, x=stages, y=[bd_b[s] for s in stages], marker_color="#EF553B"),
    ])
    fig.update_layout(
        barmode="group",
        title="Stage-by-Stage Latency Comparison",
        xaxis_title="Stage",
        yaxis_title="Latency (ms)",
        height=400,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
    )
    return fig


def render() -> None:
    st.subheader("⚖️ Compare — Two Latency Configurations")

    st.markdown(
        "Select two configurations and compare their latency waterfall side-by-side. "
        "See exactly which stages differ and by how much."
    )

    preset_names = list(PRESET_CONFIGS.keys())

    col_sel_a, col_sel_b = st.columns(2)
    with col_sel_a:
        name_a = st.selectbox("Configuration A", preset_names, index=1, key="sysdesign_uc1_cmp_a")
    with col_sel_b:
        name_b = st.selectbox("Configuration B", preset_names, index=2, key="sysdesign_uc1_cmp_b")

    budget_a = PRESET_CONFIGS[name_a]
    budget_b = PRESET_CONFIGS[name_b]

    # Summary metrics
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown(f"**{name_a}**")
            st.metric("Total (no streaming)", f"{budget_a.total_ms:.0f} ms")
            st.metric("Perceived (streaming)", f"{budget_a.total_with_streaming_ms:.0f} ms")
            st.metric("LLM share", f"{budget_a.llm_pct:.1f}%")
            st.metric("Bottleneck", budget_a.bottleneck)

    with col2:
        with st.container(border=True):
            st.markdown(f"**{name_b}**")
            delta_total = budget_b.total_ms - budget_a.total_ms
            delta_streaming = budget_b.total_with_streaming_ms - budget_a.total_with_streaming_ms
            st.metric("Total (no streaming)", f"{budget_b.total_ms:.0f} ms",
                      delta=f"{delta_total:+.0f} ms vs A")
            st.metric("Perceived (streaming)", f"{budget_b.total_with_streaming_ms:.0f} ms",
                      delta=f"{delta_streaming:+.0f} ms vs A")
            st.metric("LLM share", f"{budget_b.llm_pct:.1f}%")
            st.metric("Bottleneck", budget_b.bottleneck)

    # Grouped bar chart
    st.plotly_chart(_build_grouped_bar(budget_a, name_a, budget_b, name_b), use_container_width=True)

    # Stage-by-stage table
    st.divider()
    st.markdown("### Stage-by-Stage Breakdown")

    bd_a = {item["stage"]: item["ms"] for item in budget_a.breakdown()}
    bd_b = {item["stage"]: item["ms"] for item in budget_b.breakdown()}
    stages = list(bd_a.keys())

    rows = []
    for s in stages:
        diff = bd_b[s] - bd_a[s]
        pct_diff = (diff / bd_a[s] * 100) if bd_a[s] > 0 else 0.0
        rows.append({
            "Stage": s,
            f"A: {name_a[:25]} (ms)": f"{bd_a[s]:.0f}",
            f"B: {name_b[:25]} (ms)": f"{bd_b[s]:.0f}",
            "Diff (B−A)": f"{diff:+.0f} ms",
            "Change": f"{pct_diff:+.0f}%" if bd_a[s] > 0 else "—",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Key takeaway
    faster = name_a if budget_a.total_ms < budget_b.total_ms else name_b
    slower = name_b if budget_a.total_ms < budget_b.total_ms else name_a
    faster_budget = budget_a if budget_a.total_ms < budget_b.total_ms else budget_b
    slower_budget = budget_b if budget_a.total_ms < budget_b.total_ms else budget_a
    speedup = slower_budget.total_ms / faster_budget.total_ms if faster_budget.total_ms > 0 else 1

    st.success(
        f"**{faster}** is **{speedup:.2f}× faster** than **{slower}** "
        f"({faster_budget.total_ms:.0f} ms vs {slower_budget.total_ms:.0f} ms total)."
    )
