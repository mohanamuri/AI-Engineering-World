"""UC4 — Playground: Interactive monthly cost estimator with pie chart."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from applications.sysdesign_projects.services.cost_estimator import (
    CostConfig,
    CostBreakdown,
    MODEL_PRICING,
    estimate_monthly_cost,
)
from applications.sysdesign_projects.uc4.constants import COST_RESULT_KEY


def _build_pie_chart(breakdown: CostBreakdown) -> go.Figure:
    labels = ["LLM Input", "LLM Output", "Embedding", "Vector DB", "Cache", "Hosting"]
    values = [
        breakdown.llm_input_usd,
        breakdown.llm_output_usd,
        breakdown.embedding_usd,
        breakdown.vector_db_usd,
        breakdown.cache_usd,
        breakdown.hosting_usd,
    ]
    # Filter out zero values for cleaner chart
    filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
    if not filtered:
        filtered = [("Total", 0.01)]
    filt_labels, filt_values = zip(*filtered)

    fig = px.pie(
        values=filt_values,
        names=filt_labels,
        title="Monthly Cost Breakdown",
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=380, margin={"l": 10, "r": 10, "t": 50, "b": 10})
    return fig


def render() -> None:
    st.subheader("🧪 Playground — Monthly Cost Estimator")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Traffic**")
        monthly_requests = st.number_input(
            "Monthly requests",
            min_value=100, max_value=10_000_000, value=10_000, step=1000,
            key="sysdesign_uc4_requests",
        )
        avg_input_tokens = st.slider(
            "Avg input tokens per request", 100, 8000, 1000, 100,
            key="sysdesign_uc4_input_tok",
        )
        avg_output_tokens = st.slider(
            "Avg output tokens per request", 50, 2000, 500, 50,
            key="sysdesign_uc4_output_tok",
        )
        cache_hit_rate = st.slider(
            "Cache hit rate", 0.0, 0.9, 0.3, 0.05, format="%.2f",
            key="sysdesign_uc4_cache_rate",
        )

    with col2:
        st.markdown("**Model & Infrastructure**")
        model_name = st.selectbox(
            "LLM Model",
            list(MODEL_PRICING.keys()),
            index=0,
            key="sysdesign_uc4_model",
        )
        model_prices = MODEL_PRICING[model_name]

        monthly_doc_updates = st.number_input(
            "New documents to embed per month",
            min_value=0, max_value=100_000, value=100, step=10,
            key="sysdesign_uc4_docs",
        )
        vector_db_usd = st.number_input(
            "Vector DB monthly cost ($)",
            min_value=0.0, max_value=500.0, value=0.0, step=5.0,
            key="sysdesign_uc4_vdb",
        )
        cache_usd = st.number_input(
            "Cache (Redis) monthly cost ($)",
            min_value=0.0, max_value=200.0, value=0.0, step=5.0,
            key="sysdesign_uc4_cache_cost",
        )
        hosting_usd = st.number_input(
            "Hosting monthly cost ($)",
            min_value=0.0, max_value=500.0, value=7.0, step=5.0,
            key="sysdesign_uc4_hosting",
        )

    config = CostConfig(
        monthly_requests=int(monthly_requests),
        avg_input_tokens=int(avg_input_tokens),
        avg_output_tokens=int(avg_output_tokens),
        cache_hit_rate=cache_hit_rate,
        input_token_cost_per_1m=model_prices["input"],
        output_token_cost_per_1m=model_prices["output"],
        monthly_doc_updates=int(monthly_doc_updates),
        avg_doc_tokens=2000,
        embedding_cost_per_1m=0.02,
        vector_db_monthly_usd=float(vector_db_usd),
        cache_monthly_usd=float(cache_usd),
        hosting_monthly_usd=float(hosting_usd),
    )

    breakdown = estimate_monthly_cost(config)
    st.session_state[COST_RESULT_KEY] = breakdown

    st.divider()

    # Top-level metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly total", f"${breakdown.total_usd:.2f}")
    c2.metric("Cost per request", f"{breakdown.cost_per_request_cents:.3f} ¢")
    c3.metric("Annual projection", f"${breakdown.total_usd * 12:.0f}")

    # Pie chart
    col_pie, col_detail = st.columns([3, 2])
    with col_pie:
        st.plotly_chart(_build_pie_chart(breakdown), use_container_width=True)

    with col_detail:
        st.markdown("**Line-item breakdown:**")
        line_items = [
            ("LLM Input tokens", breakdown.llm_input_usd),
            ("LLM Output tokens", breakdown.llm_output_usd),
            ("Embeddings", breakdown.embedding_usd),
            ("Vector DB", breakdown.vector_db_usd),
            ("Cache (Redis)", breakdown.cache_usd),
            ("Hosting", breakdown.hosting_usd),
        ]
        for item_name, cost in line_items:
            pct = (cost / breakdown.total_usd * 100) if breakdown.total_usd > 0 else 0
            st.markdown(f"- **{item_name}:** ${cost:.3f} ({pct:.1f}%)")
        st.markdown(f"**Total: ${breakdown.total_usd:.2f}/month**")

    st.divider()

    # Cache ROI section
    st.markdown("### Cache ROI Analysis")

    col_roi1, col_roi2 = st.columns(2)
    with col_roi1:
        with st.container(border=True):
            st.markdown("**Cache performance**")
            st.metric("LLM cost saved by cache", f"${breakdown.savings_from_cache_usd:.2f}/month")
            st.metric("Cache infrastructure cost", f"${breakdown.cache_usd:.2f}/month")
            if breakdown.cache_roi_pct == float("inf"):
                st.metric("Cache ROI", "∞ (free cache!)")
            else:
                st.metric("Cache ROI", f"{breakdown.cache_roi_pct:.0f}%")

    with col_roi2:
        with st.container(border=True):
            st.markdown("**Interpretation**")
            if breakdown.cache_usd == 0:
                st.info(
                    "Cache is free (in-memory). You're saving "
                    f"${breakdown.savings_from_cache_usd:.2f}/month with no cache cost. "
                    "Consider paid Redis to persist cache across restarts."
                )
            elif breakdown.cache_roi_pct >= 200:
                st.success(
                    f"Cache ROI = {breakdown.cache_roi_pct:.0f}% — excellent. "
                    f"You spend ${breakdown.cache_usd:.2f} and save ${breakdown.savings_from_cache_usd:.2f}. "
                    "Consider increasing cache hit rate further."
                )
            elif breakdown.cache_roi_pct >= 100:
                st.info(
                    f"Cache ROI = {breakdown.cache_roi_pct:.0f}% — positive. "
                    "Cache pays for itself and then some."
                )
            else:
                st.warning(
                    f"Cache ROI = {breakdown.cache_roi_pct:.0f}% — marginal. "
                    "Cache costs more than it saves at this traffic level. "
                    "Consider free in-memory cache until monthly requests exceed 100K."
                )

    # Scale projection
    st.divider()
    st.markdown("### Cost at Different Traffic Scales")

    scale_data = []
    for mult, label in [(0.1, "10% of current"), (1, "Current"), (10, "10×"), (100, "100×")]:
        scaled_config = CostConfig(
            monthly_requests=max(1, int(monthly_requests * mult)),
            avg_input_tokens=int(avg_input_tokens),
            avg_output_tokens=int(avg_output_tokens),
            cache_hit_rate=cache_hit_rate,
            input_token_cost_per_1m=model_prices["input"],
            output_token_cost_per_1m=model_prices["output"],
            monthly_doc_updates=int(monthly_doc_updates),
            avg_doc_tokens=2000,
            embedding_cost_per_1m=0.02,
            vector_db_monthly_usd=float(vector_db_usd),
            cache_monthly_usd=float(cache_usd),
            hosting_monthly_usd=float(hosting_usd),
        )
        scaled_bd = estimate_monthly_cost(scaled_config)
        scale_data.append({
            "Scale": label,
            "Monthly requests": f"{int(monthly_requests * mult):,}",
            "Monthly cost": f"${scaled_bd.total_usd:.2f}",
            "Annual cost": f"${scaled_bd.total_usd * 12:,.0f}",
            "Cost / request": f"{scaled_bd.cost_per_request_cents:.3f} ¢",
        })

    st.dataframe(pd.DataFrame(scale_data), use_container_width=True, hide_index=True)
