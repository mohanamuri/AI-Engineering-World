"""UC2 — Compare: Side-by-side comparison of two scaling strategies."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from applications.sysdesign_projects.services.throughput_sim import (
    ThroughputConfig,
    simulate_throughput,
    simulate_scaling_curve,
)


STRATEGY_PRESETS = {
    "Baseline — 1 replica, no optimisation": ThroughputConfig(
        replicas=1, avg_latency_ms=1600, cache_hit_rate=0.0, batch_size=1,
    ),
    "Scale Out — 4 replicas only": ThroughputConfig(
        replicas=4, avg_latency_ms=1600, cache_hit_rate=0.0, batch_size=1,
    ),
    "Cache First — 1 replica + 40% cache": ThroughputConfig(
        replicas=1, avg_latency_ms=1600, cache_hit_rate=0.4, batch_size=1,
    ),
    "Batching — 1 replica + batch=4": ThroughputConfig(
        replicas=1, avg_latency_ms=1600, cache_hit_rate=0.0, batch_size=4,
    ),
    "Balanced — 3 replicas + cache + batch": ThroughputConfig(
        replicas=3, avg_latency_ms=1600, cache_hit_rate=0.3, batch_size=4,
    ),
    "Enterprise — 8 replicas + cache + batch": ThroughputConfig(
        replicas=8, avg_latency_ms=1600, cache_hit_rate=0.5, batch_size=8,
    ),
}


def _build_comparison_chart(
    curve_a: list[dict], label_a: str,
    curve_b: list[dict], label_b: str,
) -> go.Figure:
    df_a = pd.DataFrame(curve_a)
    df_b = pd.DataFrame(curve_b)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_a["replicas"], y=df_a["rps_both"],
        mode="lines+markers", name=f"A: {label_a[:30]}",
        line={"color": "#636EFA", "width": 2},
    ))
    fig.add_trace(go.Scatter(
        x=df_b["replicas"], y=df_b["rps_both"],
        mode="lines+markers", name=f"B: {label_b[:30]}",
        line={"color": "#EF553B", "width": 2},
    ))
    fig.update_layout(
        title="Scaling Curve Comparison (cache + batching combined)",
        xaxis_title="Replicas",
        yaxis_title="RPS",
        height=380,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
    )
    return fig


def render() -> None:
    st.subheader("⚖️ Compare — Two Scaling Strategies")

    st.markdown(
        "Compare two different scaling configurations at the same traffic level. "
        "See which strategy gives more RPS for the same cost."
    )

    preset_names = list(STRATEGY_PRESETS.keys())

    col_sel_a, col_sel_b = st.columns(2)
    with col_sel_a:
        name_a = st.selectbox("Strategy A", preset_names, index=2, key="sysdesign_uc2_cmp_a")
    with col_sel_b:
        name_b = st.selectbox("Strategy B", preset_names, index=4, key="sysdesign_uc2_cmp_b")

    config_a = STRATEGY_PRESETS[name_a]
    config_b = STRATEGY_PRESETS[name_b]

    result_a = simulate_throughput(config_a)
    result_b = simulate_throughput(config_b)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown(f"**Strategy A: {name_a}**")
            st.metric("Baseline RPS", f"{result_a.rps_no_optimisation:.2f}")
            st.metric("With Cache", f"{result_a.rps_with_cache:.2f}",
                      delta=f"+{result_a.cache_throughput_gain_pct:.0f}%")
            st.metric("With Batching", f"{result_a.rps_with_batching:.2f}",
                      delta=f"+{result_a.batch_throughput_gain_pct:.0f}%")
            st.metric("Combined (best)", f"{result_a.rps_with_both:.2f}",
                      delta=f"+{result_a.combined_gain_pct:.0f}%")
            st.caption(
                f"Replicas: {config_a.replicas} | "
                f"Cache: {config_a.cache_hit_rate:.0%} | "
                f"Batch: {config_a.batch_size}"
            )

    with col2:
        with st.container(border=True):
            st.markdown(f"**Strategy B: {name_b}**")
            delta_b = result_b.rps_with_both - result_a.rps_with_both
            st.metric("Baseline RPS", f"{result_b.rps_no_optimisation:.2f}")
            st.metric("With Cache", f"{result_b.rps_with_cache:.2f}",
                      delta=f"+{result_b.cache_throughput_gain_pct:.0f}%")
            st.metric("With Batching", f"{result_b.rps_with_batching:.2f}",
                      delta=f"+{result_b.batch_throughput_gain_pct:.0f}%")
            st.metric("Combined (best)", f"{result_b.rps_with_both:.2f}",
                      delta=f"{delta_b:+.2f} vs A")
            st.caption(
                f"Replicas: {config_b.replicas} | "
                f"Cache: {config_b.cache_hit_rate:.0%} | "
                f"Batch: {config_b.batch_size}"
            )

    # Scaling curves
    curve_a = simulate_scaling_curve(10, config_a)
    curve_b = simulate_scaling_curve(10, config_b)
    st.plotly_chart(_build_comparison_chart(curve_a, name_a, curve_b, name_b), use_container_width=True)

    # Analysis table
    st.divider()
    st.markdown("### Detailed Comparison")

    winner_rps = name_a if result_a.rps_with_both >= result_b.rps_with_both else name_b
    winner_result = result_a if result_a.rps_with_both >= result_b.rps_with_both else result_b
    loser_result = result_b if result_a.rps_with_both >= result_b.rps_with_both else result_a

    ratio = winner_result.rps_with_both / loser_result.rps_with_both if loser_result.rps_with_both > 0 else 1.0

    st.table({
        "Metric": ["Baseline RPS", "Best RPS", "Cache gain", "Batch gain", "Combined gain"],
        f"A: {name_a[:20]}": [
            f"{result_a.rps_no_optimisation:.2f}",
            f"{result_a.rps_with_both:.2f}",
            f"+{result_a.cache_throughput_gain_pct:.0f}%",
            f"+{result_a.batch_throughput_gain_pct:.0f}%",
            f"+{result_a.combined_gain_pct:.0f}%",
        ],
        f"B: {name_b[:20]}": [
            f"{result_b.rps_no_optimisation:.2f}",
            f"{result_b.rps_with_both:.2f}",
            f"+{result_b.cache_throughput_gain_pct:.0f}%",
            f"+{result_b.batch_throughput_gain_pct:.0f}%",
            f"+{result_b.combined_gain_pct:.0f}%",
        ],
    })

    st.success(
        f"**{winner_rps}** achieves **{ratio:.2f}× higher RPS** in the best-case (combined) scenario."
    )
