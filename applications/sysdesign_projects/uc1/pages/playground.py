"""UC1 — Playground: Interactive latency budget builder with waterfall chart."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from applications.sysdesign_projects.services.latency_calculator import (
    LatencyBudget,
    PRESET_CONFIGS,
)
from applications.sysdesign_projects.uc1.constants import LATENCY_RESULT_KEY


CATEGORY_COLORS = {
    "Infrastructure": "#636EFA",
    "ML": "#EF553B",
    "Retrieval": "#00CC96",
    "LLM": "#AB63FA",
}


def _build_chart(budget: LatencyBudget) -> go.Figure:
    breakdown = budget.breakdown()
    df = pd.DataFrame(breakdown)
    df = df[df["ms"] > 0]  # hide zero-ms stages

    fig = px.bar(
        df,
        x="ms",
        y="stage",
        color="category",
        orientation="h",
        color_discrete_map=CATEGORY_COLORS,
        labels={"ms": "Latency (ms)", "stage": "Stage", "category": "Category"},
        title="Latency Waterfall — per Request",
        text="ms",
    )
    fig.update_traces(texttemplate="%{text:.0f} ms", textposition="outside")
    fig.update_layout(
        height=400,
        yaxis={"categoryorder": "total ascending"},
        margin={"l": 10, "r": 20, "t": 50, "b": 10},
        legend_title_text="Category",
    )
    return fig


def render() -> None:
    st.subheader("🧪 Playground — Latency Budget Builder")

    # Preset selector
    preset_name = st.selectbox(
        "Start from a preset",
        list(PRESET_CONFIGS.keys()),
        index=1,
        key="sysdesign_uc1_preset",
    )
    preset = PRESET_CONFIGS[preset_name]

    st.divider()
    st.markdown("**Adjust individual stages (ms):**")

    col1, col2 = st.columns(2)

    with col1:
        network_in = st.slider("Network (in) ms", 0, 200, int(preset.network_in_ms), 5, key="sysdesign_uc1_net_in")
        embedding = st.slider("Embedding ms", 0, 100, int(preset.embedding_ms), 1, key="sysdesign_uc1_embed")
        vector_search = st.slider("Vector Search ms", 0, 200, int(preset.vector_search_ms), 5, key="sysdesign_uc1_vsearch")
        reranking = st.slider("Reranking ms (0 = disabled)", 0, 200, int(preset.reranking_ms), 5, key="sysdesign_uc1_rerank")
        context_prep = st.slider("Context Prep ms", 0, 50, int(preset.context_prep_ms), 1, key="sysdesign_uc1_ctx")

    with col2:
        llm_ttft = st.slider("LLM TTFT ms", 50, 1000, int(preset.llm_ttft_ms), 10, key="sysdesign_uc1_ttft")
        llm_gen = st.slider("LLM Generation ms", 100, 5000, int(preset.llm_generation_ms), 50, key="sysdesign_uc1_gen")
        post_process = st.slider("Post-process ms", 0, 100, int(preset.post_process_ms), 1, key="sysdesign_uc1_post")
        network_out = st.slider("Network (out) ms", 0, 200, int(preset.network_out_ms), 5, key="sysdesign_uc1_net_out")

    budget = LatencyBudget(
        network_in_ms=float(network_in),
        embedding_ms=float(embedding),
        vector_search_ms=float(vector_search),
        reranking_ms=float(reranking),
        context_prep_ms=float(context_prep),
        llm_ttft_ms=float(llm_ttft),
        llm_generation_ms=float(llm_gen),
        post_process_ms=float(post_process),
        network_out_ms=float(network_out),
    )

    # Store result in session
    st.session_state[LATENCY_RESULT_KEY] = budget

    st.divider()

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total (no streaming)", f"{budget.total_ms:.0f} ms")
    c2.metric("Perceived (streaming)", f"{budget.total_with_streaming_ms:.0f} ms")
    c3.metric("LLM share", f"{budget.llm_pct:.1f}%")
    c4.metric("Bottleneck", budget.bottleneck)

    streaming_saving = budget.total_ms - budget.total_with_streaming_ms
    pct_saving = streaming_saving / budget.total_ms * 100 if budget.total_ms > 0 else 0
    st.info(
        f"**Streaming saves {streaming_saving:.0f} ms ({pct_saving:.0f}%) of perceived latency** — "
        f"user sees first token at {budget.total_with_streaming_ms:.0f} ms instead of waiting "
        f"for {budget.total_ms:.0f} ms."
    )

    # Waterfall chart
    st.plotly_chart(_build_chart(budget), use_container_width=True)

    # Category breakdown
    st.divider()
    st.markdown("**Category breakdown:**")
    breakdown = budget.breakdown()
    totals: dict[str, float] = {}
    for item in breakdown:
        cat = item["category"]
        totals[cat] = totals.get(cat, 0) + item["ms"]

    cat_cols = st.columns(len(totals))
    for i, (cat, ms) in enumerate(totals.items()):
        pct = ms / budget.total_ms * 100 if budget.total_ms > 0 else 0
        cat_cols[i].metric(cat, f"{ms:.0f} ms", f"{pct:.1f}%")

    st.info(
        "**Try it:** Switch presets above to see how the waterfall changes. "
        "Enable reranking (+80ms) and see how small that is compared to LLM generation."
    )
