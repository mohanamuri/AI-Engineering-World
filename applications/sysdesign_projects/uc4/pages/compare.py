"""UC4 — Compare: Side-by-side cost comparison of two models at same traffic."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from applications.sysdesign_projects.services.cost_estimator import (
    CostConfig,
    MODEL_PRICING,
    estimate_monthly_cost,
)


def _build_grouped_cost_bar(
    breakdown_a, label_a: str,
    breakdown_b, label_b: str,
) -> go.Figure:
    categories = ["LLM Input", "LLM Output", "Embedding", "Vector DB", "Cache", "Hosting"]
    values_a = [
        breakdown_a.llm_input_usd, breakdown_a.llm_output_usd,
        breakdown_a.embedding_usd, breakdown_a.vector_db_usd,
        breakdown_a.cache_usd, breakdown_a.hosting_usd,
    ]
    values_b = [
        breakdown_b.llm_input_usd, breakdown_b.llm_output_usd,
        breakdown_b.embedding_usd, breakdown_b.vector_db_usd,
        breakdown_b.cache_usd, breakdown_b.hosting_usd,
    ]
    fig = go.Figure(data=[
        go.Bar(name=label_a[:30], x=categories, y=values_a, marker_color="#636EFA",
               text=[f"${v:.2f}" for v in values_a], textposition="outside"),
        go.Bar(name=label_b[:30], x=categories, y=values_b, marker_color="#EF553B",
               text=[f"${v:.2f}" for v in values_b], textposition="outside"),
    ])
    fig.update_layout(
        barmode="group",
        title="Cost Comparison by Category",
        yaxis_title="Cost (USD/month)",
        height=400,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
    )
    return fig


def render() -> None:
    st.subheader("⚖️ Compare — Two Models at Same Traffic")

    st.markdown(
        "Compare the monthly cost of two different LLM models given identical traffic and infrastructure. "
        "See where the savings come from and whether the cheaper model is worth the quality trade-off."
    )

    model_names = list(MODEL_PRICING.keys())

    col_sel_a, col_sel_b = st.columns(2)
    with col_sel_a:
        model_a = st.selectbox("Model A", model_names, index=0, key="sysdesign_uc4_cmp_a")
    with col_sel_b:
        model_b = st.selectbox("Model B", model_names, index=2, key="sysdesign_uc4_cmp_b")

    st.divider()
    st.markdown("**Shared traffic configuration:**")

    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_requests = st.number_input(
            "Monthly requests", min_value=100, max_value=5_000_000,
            value=50_000, step=1000, key="sysdesign_uc4_cmp_reqs",
        )
    with col2:
        avg_input_tokens = st.slider("Avg input tokens", 100, 4000, 1000, 100, key="sysdesign_uc4_cmp_in")
        avg_output_tokens = st.slider("Avg output tokens", 50, 1000, 500, 50, key="sysdesign_uc4_cmp_out")
    with col3:
        cache_hit_rate = st.slider("Cache hit rate", 0.0, 0.9, 0.3, 0.05, format="%.2f",
                                   key="sysdesign_uc4_cmp_cache")
        hosting_usd = st.number_input("Hosting $", 0.0, 200.0, 7.0, 5.0, key="sysdesign_uc4_cmp_host")

    prices_a = MODEL_PRICING[model_a]
    prices_b = MODEL_PRICING[model_b]

    def make_config(prices):
        return CostConfig(
            monthly_requests=int(monthly_requests),
            avg_input_tokens=int(avg_input_tokens),
            avg_output_tokens=int(avg_output_tokens),
            cache_hit_rate=cache_hit_rate,
            input_token_cost_per_1m=prices["input"],
            output_token_cost_per_1m=prices["output"],
            monthly_doc_updates=100,
            avg_doc_tokens=2000,
            embedding_cost_per_1m=0.02,
            vector_db_monthly_usd=0.0,
            cache_monthly_usd=0.0,
            hosting_monthly_usd=float(hosting_usd),
        )

    bd_a = estimate_monthly_cost(make_config(prices_a))
    bd_b = estimate_monthly_cost(make_config(prices_b))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown(f"**Model A: {model_a}**")
            st.markdown(
                f"- Input: ${prices_a['input']:.2f}/1M tokens\n"
                f"- Output: ${prices_a['output']:.2f}/1M tokens"
            )
            st.metric("Monthly LLM cost", f"${bd_a.llm_input_usd + bd_a.llm_output_usd:.2f}")
            st.metric("Total monthly cost", f"${bd_a.total_usd:.2f}")
            st.metric("Cost per request", f"{bd_a.cost_per_request_cents:.3f} ¢")
            st.metric("Annual projection", f"${bd_a.total_usd * 12:,.0f}")

    with col2:
        with st.container(border=True):
            st.markdown(f"**Model B: {model_b}**")
            st.markdown(
                f"- Input: ${prices_b['input']:.2f}/1M tokens\n"
                f"- Output: ${prices_b['output']:.2f}/1M tokens"
            )
            delta_total = bd_b.total_usd - bd_a.total_usd
            st.metric("Monthly LLM cost", f"${bd_b.llm_input_usd + bd_b.llm_output_usd:.2f}",
                      delta=f"{delta_total:+.2f} vs A")
            st.metric("Total monthly cost", f"${bd_b.total_usd:.2f}")
            st.metric("Cost per request", f"{bd_b.cost_per_request_cents:.3f} ¢")
            st.metric("Annual projection", f"${bd_b.total_usd * 12:,.0f}")

    st.plotly_chart(_build_grouped_cost_bar(bd_a, model_a, bd_b, model_b), use_container_width=True)

    # Savings analysis
    st.divider()
    st.markdown("### Savings Analysis")

    cheaper = model_a if bd_a.total_usd <= bd_b.total_usd else model_b
    cheaper_bd = bd_a if bd_a.total_usd <= bd_b.total_usd else bd_b
    costlier_bd = bd_b if bd_a.total_usd <= bd_b.total_usd else bd_a
    monthly_saving = abs(bd_b.total_usd - bd_a.total_usd)
    annual_saving = monthly_saving * 12
    ratio = costlier_bd.total_usd / cheaper_bd.total_usd if cheaper_bd.total_usd > 0 else 1.0

    if monthly_saving > 0:
        st.success(
            f"**{cheaper}** saves **${monthly_saving:.2f}/month** (${annual_saving:.0f}/year). "
            f"The costlier model is **{ratio:.1f}×** more expensive. "
            f"Consider whether the quality difference justifies this cost at your traffic level."
        )
    else:
        st.info("Both models have the same cost at this configuration.")

    # Break-even analysis
    if monthly_saving > 0 and cheaper_bd.total_usd > 0:
        st.markdown("### Scale at Which Costs Become Significant")
        scale_rows = []
        for scale in [1_000, 10_000, 100_000, 500_000, 1_000_000]:
            cfg_cheap = CostConfig(
                monthly_requests=scale,
                avg_input_tokens=int(avg_input_tokens),
                avg_output_tokens=int(avg_output_tokens),
                cache_hit_rate=cache_hit_rate,
                input_token_cost_per_1m=min(prices_a["input"], prices_b["input"]),
                output_token_cost_per_1m=min(prices_a["output"], prices_b["output"]),
                monthly_doc_updates=100, avg_doc_tokens=2000,
                embedding_cost_per_1m=0.02, vector_db_monthly_usd=0.0,
                cache_monthly_usd=0.0, hosting_monthly_usd=float(hosting_usd),
            )
            cfg_costly = CostConfig(
                monthly_requests=scale,
                avg_input_tokens=int(avg_input_tokens),
                avg_output_tokens=int(avg_output_tokens),
                cache_hit_rate=cache_hit_rate,
                input_token_cost_per_1m=max(prices_a["input"], prices_b["input"]),
                output_token_cost_per_1m=max(prices_a["output"], prices_b["output"]),
                monthly_doc_updates=100, avg_doc_tokens=2000,
                embedding_cost_per_1m=0.02, vector_db_monthly_usd=0.0,
                cache_monthly_usd=0.0, hosting_monthly_usd=float(hosting_usd),
            )
            bd_cheap = estimate_monthly_cost(cfg_cheap)
            bd_costly = estimate_monthly_cost(cfg_costly)
            scale_rows.append({
                "Monthly requests": f"{scale:,}",
                f"Cheaper ({model_a if prices_a['input'] <= prices_b['input'] else model_b})": f"${bd_cheap.total_usd:.0f}",
                f"Costlier ({model_b if prices_a['input'] <= prices_b['input'] else model_a})": f"${bd_costly.total_usd:.0f}",
                "Monthly saving": f"${abs(bd_costly.total_usd - bd_cheap.total_usd):.0f}",
            })

        st.dataframe(pd.DataFrame(scale_rows), use_container_width=True, hide_index=True)
