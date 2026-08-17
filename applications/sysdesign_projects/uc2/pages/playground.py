"""UC2 — Playground: Interactive RPS simulator with scaling curve."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from applications.sysdesign_projects.services.throughput_sim import (
    ThroughputConfig,
    ThroughputResult,
    simulate_throughput,
    simulate_scaling_curve,
)
from applications.sysdesign_projects.uc2.constants import THROUGHPUT_RESULT_KEY


def _build_scaling_chart(curve_data: list[dict]) -> go.Figure:
    df = pd.DataFrame(curve_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["replicas"], y=df["rps_baseline"],
        mode="lines+markers", name="Baseline (no opt)",
        line={"color": "#636EFA", "dash": "dot"},
    ))
    fig.add_trace(go.Scatter(
        x=df["replicas"], y=df["rps_cache"],
        mode="lines+markers", name="+ Cache",
        line={"color": "#00CC96"},
    ))
    fig.add_trace(go.Scatter(
        x=df["replicas"], y=df["rps_batching"],
        mode="lines+markers", name="+ Batching",
        line={"color": "#EF553B"},
    ))
    fig.add_trace(go.Scatter(
        x=df["replicas"], y=df["rps_both"],
        mode="lines+markers", name="Cache + Batching",
        line={"color": "#AB63FA", "width": 3},
    ))
    fig.update_layout(
        title="RPS vs Replicas — Scaling Curve",
        xaxis_title="Replicas",
        yaxis_title="Requests per Second (RPS)",
        height=420,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        legend={"orientation": "h", "y": -0.2},
    )
    return fig


def _build_bar_chart(result: ThroughputResult) -> go.Figure:
    labels = ["Baseline", "+ Cache", "+ Batching", "Cache + Batch"]
    values = [
        result.rps_no_optimisation,
        result.rps_with_cache,
        result.rps_with_batching,
        result.rps_with_both,
    ]
    colors = ["#636EFA", "#00CC96", "#EF553B", "#AB63FA"]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=[f"{v:.2f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="RPS by Optimisation Strategy",
        yaxis_title="RPS",
        height=350,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
    )
    return fig


def render() -> None:
    st.subheader("🧪 Playground — Throughput Simulator")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**System Configuration**")
        replicas = st.slider("Replicas", 1, 20, 1, 1, key="sysdesign_uc2_replicas")
        avg_latency_ms = st.slider("Avg latency per request (ms)", 200, 5000, 1600, 50,
                                   key="sysdesign_uc2_latency")

    with col2:
        st.markdown("**Optimisation Levers**")
        cache_hit_rate = st.slider("Cache hit rate", 0.0, 0.9, 0.3, 0.05,
                                   format="%.2f", key="sysdesign_uc2_cache")
        batch_size = st.slider("Batch size", 1, 16, 1, 1, key="sysdesign_uc2_batch")

    with st.expander("Advanced settings"):
        cache_latency_ms = st.slider("Cache response latency (ms)", 1, 50, 5, 1,
                                     key="sysdesign_uc2_cache_lat")
        batch_overhead_ms = st.slider("Batch overhead (ms)", 0, 200, 50, 10,
                                      key="sysdesign_uc2_batch_oh")

    config = ThroughputConfig(
        replicas=replicas,
        avg_latency_ms=float(avg_latency_ms),
        cache_hit_rate=cache_hit_rate,
        batch_size=batch_size,
        cache_latency_ms=float(cache_latency_ms),
        batch_overhead_ms=float(batch_overhead_ms),
    )

    result = simulate_throughput(config)
    st.session_state[THROUGHPUT_RESULT_KEY] = result

    st.divider()

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Baseline RPS", f"{result.rps_no_optimisation:.2f}")
    c2.metric("+ Cache", f"{result.rps_with_cache:.2f}",
              delta=f"+{result.cache_throughput_gain_pct:.0f}%")
    c3.metric("+ Batching", f"{result.rps_with_batching:.2f}",
              delta=f"+{result.batch_throughput_gain_pct:.0f}%")
    c4.metric("Cache + Batch", f"{result.rps_with_both:.2f}",
              delta=f"+{result.combined_gain_pct:.0f}%")

    # Bar chart for current config
    st.plotly_chart(_build_bar_chart(result), use_container_width=True)

    st.divider()

    # Scaling curve
    st.markdown("**Scaling Curve: RPS vs Replicas (up to 20)**")
    curve_data = simulate_scaling_curve(20, config)
    st.plotly_chart(_build_scaling_chart(curve_data), use_container_width=True)

    # Derived insights
    st.divider()
    st.markdown("**Key numbers for your configuration:**")

    effective_lat_cache = (
        cache_hit_rate * float(cache_latency_ms) +
        (1 - cache_hit_rate) * float(avg_latency_ms)
    )
    effective_lat_batch = (float(avg_latency_ms) + float(batch_overhead_ms)) / batch_size

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**Cache effect on effective latency**")
            st.markdown(
                f"- Without cache: **{avg_latency_ms} ms** per request\n"
                f"- With {cache_hit_rate:.0%} hit rate: **{effective_lat_cache:.0f} ms** effective\n"
                f"- Reduction: **{avg_latency_ms - effective_lat_cache:.0f} ms** saved on average"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Batching effect on effective latency**")
            st.markdown(
                f"- Without batching: **{avg_latency_ms} ms** per request\n"
                f"- With batch={batch_size}: **{effective_lat_batch:.0f} ms** per request\n"
                f"- Amortized overhead: {batch_overhead_ms} ms / {batch_size} = "
                f"**{batch_overhead_ms / batch_size:.0f} ms** extra per request"
            )

    st.info(
        "**Try it:** Set batch_size=1 and cache=0 to see the pure baseline. "
        "Then increase cache hit rate to 0.5 — watch how dramatically RPS jumps. "
        "Then add batching on top."
    )
