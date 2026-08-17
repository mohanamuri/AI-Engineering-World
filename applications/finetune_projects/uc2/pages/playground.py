"""UC2 — Playground: Interactive LoRA parameter math visualization."""

import numpy as np
import streamlit as st

try:
    import plotly.graph_objects as go
    _PLOTLY = True
except ImportError:
    _PLOTLY = False

from applications.finetune_projects.services.lora_concepts import (
    LoRAConfig,
    get_common_model_configs,
    rank_decomposition_demo,
)
from applications.finetune_projects.uc2.constants import LORA_CONFIG_KEY, LORA_STATS_KEY


def _fmt_params(n: int) -> str:
    """Format param count as e.g. '65,536' or '16.7 M'."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f} M"
    if n >= 1_000:
        return f"{n:,}"
    return str(n)


def render() -> None:
    st.subheader("🧪 Playground — LoRA Parameter Math")

    st.markdown(
        "Adjust the model dimension **d**, LoRA rank **r**, and scaling factor **alpha**. "
        "See the parameter counts, reduction factor, and matrix slices update in real time."
    )

    # Model preset selector
    model_configs = get_common_model_configs()
    model_names = ["— custom —"] + [m["model"] for m in model_configs]
    preset_name = st.selectbox(
        "Load a model preset",
        options=model_names,
        key="finetune_uc2_model_preset",
    )
    preset_d = 768
    if preset_name != "— custom —":
        for m in model_configs:
            if m["model"] == preset_name:
                preset_d = m["d"]
                break

    st.divider()

    col_sliders, col_summary = st.columns([2, 1])

    with col_sliders:
        d = st.slider(
            "Model dimension d",
            min_value=128, max_value=8192, step=128,
            value=preset_d,
            help="Hidden size of the transformer layer (e.g. 768 for BERT-base, 4096 for LLaMA-7B)",
            key="finetune_uc2_d",
        )
        r = st.slider(
            "LoRA rank r",
            min_value=1, max_value=64, step=1,
            value=8,
            help="Rank of the low-rank decomposition. Lower = fewer params, more efficient.",
            key="finetune_uc2_r",
        )
        alpha = st.slider(
            "Alpha (scaling factor)",
            min_value=4.0, max_value=128.0, step=4.0,
            value=16.0,
            help="Scaling: effective ΔW = (alpha/r) × B×A. Typically set equal to r.",
            key="finetune_uc2_alpha",
        )

    config = LoRAConfig(d=d, r=r, alpha=alpha)
    stats = rank_decomposition_demo(config)
    st.session_state[LORA_CONFIG_KEY] = config
    st.session_state[LORA_STATS_KEY] = stats

    with col_summary:
        with st.container(border=True):
            st.markdown("**Results**")
            st.metric("Original params (d×d)", _fmt_params(stats.original_params))
            st.metric("LoRA params (2×d×r)", _fmt_params(stats.lora_params))
            st.metric("Reduction factor", f"{stats.reduction_factor:.1f}×")
            st.metric("Trainable %", f"{stats.trainable_pct:.4f}%")
            st.metric("Scaling (α/r)", f"{stats.scaling:.2f}")

    st.divider()

    # Bar chart
    if _PLOTLY:
        fig = go.Figure(data=[
            go.Bar(
                x=["Original W (d×d)", "LoRA (B + A)"],
                y=[stats.original_params, stats.lora_params],
                marker_color=["#e74c3c", "#2ecc71"],
                text=[_fmt_params(stats.original_params), _fmt_params(stats.lora_params)],
                textposition="outside",
            )
        ])
        fig.update_layout(
            title=f"Parameter count — Original vs LoRA (d={d}, r={r})",
            yaxis_title="Number of parameters",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("#### Parameter Comparison")
        st.table({
            "Matrix": ["Original W (d×d)", "LoRA A (r×d)", "LoRA B (d×r)", "LoRA total"],
            "Shape": [f"{d}×{d}", f"{r}×{d}", f"{d}×{r}", f"2×{d}×{r}"],
            "Params": [
                _fmt_params(stats.original_params),
                _fmt_params(d * r),
                _fmt_params(d * r),
                _fmt_params(stats.lora_params),
            ],
        })

    st.divider()
    st.markdown("#### Matrix Slices (first 8×8 / 8×r visible)")

    col_A, col_B = st.columns(2)
    with col_A:
        with st.container(border=True):
            st.markdown(f"**Matrix A** (shape: {min(d,8)}×{r}) — Gaussian init")
            st.caption("A ~ N(0, 0.01) — small random values at init")
            import pandas as pd
            df_A = pd.DataFrame(
                stats.matrix_A,
                columns=[f"r{i}" for i in range(r)],
                index=[f"d{i}" for i in range(min(d, 8))],
            )
            st.dataframe(df_A.style.format("{:.4f}"), use_container_width=True)

    with col_B:
        with st.container(border=True):
            st.markdown(f"**Matrix B** (shape: {r}×{min(d,8)}) — Zero init")
            st.caption("B = 0 at start → ΔW = B×A = 0 → no disruption to base model")
            df_B = pd.DataFrame(
                stats.matrix_B,
                columns=[f"d{i}" for i in range(min(d, 8))],
                index=[f"r{i}" for i in range(r)],
            )
            st.dataframe(df_B.style.format("{:.4f}"), use_container_width=True)

    st.divider()
    st.markdown("#### Full Model Parameter Estimate")
    st.markdown(
        f"If LoRA is applied to Q and V projections in all transformer layers:"
    )

    for m in model_configs:
        orig_per_layer = m["d"] * m["d"]
        lora_per_layer = 2 * m["d"] * r
        total_orig = orig_per_layer * 2 * m["layers"]   # Q + V per layer
        total_lora = lora_per_layer * 2 * m["layers"]
        pct = total_lora / total_orig * 100
        st.caption(
            f"{m['model']} (d={m['d']}, {m['layers']} layers): "
            f"orig {_fmt_params(total_orig)} → LoRA {_fmt_params(total_lora)} "
            f"({pct:.3f}% trainable, r={r})"
        )

    st.info(
        "**Try it:** Drag r from 1 to 64 to see the trade-off. "
        "Select LLaMA-7B to see why r=8 keeps trainable params under 0.1%."
    )
