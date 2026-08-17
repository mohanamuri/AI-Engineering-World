"""UC2 — Compare: Two LoRA configs side by side — rank trade-off."""

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


def _fmt_params(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f} M"
    if n >= 1_000:
        return f"{n:,}"
    return str(n)


def render() -> None:
    st.subheader("⚖️ Compare — LoRA Rank Trade-off")

    st.markdown(
        "Compare two LoRA configurations side by side. "
        "The key question: how does changing rank r affect trainable parameter count and memory?"
    )

    model_configs = get_common_model_configs()
    model_names = [m["model"] for m in model_configs]
    model_choice = st.selectbox(
        "Select base model for comparison",
        options=model_names,
        index=2,  # LLaMA-7B default
        key="finetune_uc2_cmp_model",
    )
    selected_model = next(m for m in model_configs if m["model"] == model_choice)
    d = selected_model["d"]

    st.caption(f"Model: {model_choice} | d = {d}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Config A")
        r_a = st.slider(
            "Rank r (A)", min_value=1, max_value=64, step=1,
            value=4, key="finetune_uc2_cmp_r_a",
        )
        alpha_a = st.slider(
            "Alpha (A)", min_value=4.0, max_value=128.0, step=4.0,
            value=8.0, key="finetune_uc2_cmp_alpha_a",
        )

    with col2:
        st.markdown("### Config B")
        r_b = st.slider(
            "Rank r (B)", min_value=1, max_value=64, step=1,
            value=16, key="finetune_uc2_cmp_r_b",
        )
        alpha_b = st.slider(
            "Alpha (B)", min_value=4.0, max_value=128.0, step=4.0,
            value=32.0, key="finetune_uc2_cmp_alpha_b",
        )

    stats_a = rank_decomposition_demo(LoRAConfig(d=d, r=r_a, alpha=alpha_a))
    stats_b = rank_decomposition_demo(LoRAConfig(d=d, r=r_b, alpha=alpha_b))

    st.divider()
    st.markdown("### Results")

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        with st.container(border=True):
            st.markdown(f"**Config A — r={r_a}, α={alpha_a}**")
            st.metric("LoRA params (per layer)", _fmt_params(stats_a.lora_params))
            st.metric("Reduction factor", f"{stats_a.reduction_factor:.1f}×")
            st.metric("Trainable %", f"{stats_a.trainable_pct:.4f}%")
            st.metric("Scaling (α/r)", f"{stats_a.scaling:.2f}")

    with res_col2:
        with st.container(border=True):
            st.markdown(f"**Config B — r={r_b}, α={alpha_b}**")
            st.metric("LoRA params (per layer)", _fmt_params(stats_b.lora_params))
            st.metric("Reduction factor", f"{stats_b.reduction_factor:.1f}×")
            st.metric("Trainable %", f"{stats_b.trainable_pct:.4f}%")
            st.metric("Scaling (α/r)", f"{stats_b.scaling:.2f}")

    if _PLOTLY:
        fig = go.Figure(data=[
            go.Bar(
                name=f"Config A (r={r_a})",
                x=["Original W (d×d)", "LoRA params"],
                y=[stats_a.original_params, stats_a.lora_params],
                marker_color=["#3498db", "#2ecc71"],
                text=[_fmt_params(stats_a.original_params), _fmt_params(stats_a.lora_params)],
                textposition="outside",
            ),
            go.Bar(
                name=f"Config B (r={r_b})",
                x=["Original W (d×d)", "LoRA params"],
                y=[stats_b.original_params, stats_b.lora_params],
                marker_color=["#3498db", "#e67e22"],
                text=[_fmt_params(stats_b.original_params), _fmt_params(stats_b.lora_params)],
                textposition="outside",
            ),
        ])
        fig.update_layout(
            barmode="group",
            title=f"Parameter count — Config A (r={r_a}) vs Config B (r={r_b})",
            yaxis_title="Number of parameters",
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Full model estimate (Q+V, all layers)
    layers = selected_model["layers"]
    total_a = stats_a.lora_params * 2 * layers
    total_b = stats_b.lora_params * 2 * layers

    st.markdown(f"#### Full model trainable params (Q+V projections, {layers} layers)")
    st.table({
        "Config": [f"A (r={r_a})", f"B (r={r_b})", "Difference"],
        "Total trainable params": [
            _fmt_params(total_a),
            _fmt_params(total_b),
            _fmt_params(abs(total_b - total_a)),
        ],
        "Memory (fp32)": [
            f"{total_a * 4 / 1e6:.1f} MB",
            f"{total_b * 4 / 1e6:.1f} MB",
            f"{abs(total_b - total_a) * 4 / 1e6:.1f} MB",
        ],
    })

    if r_a != r_b:
        ratio = total_b / total_a if total_a > 0 else 0
        st.info(
            f"Config B (r={r_b}) has **{ratio:.1f}× more trainable parameters** than Config A (r={r_a}). "
            f"Higher rank = more expressive adaptation but more memory and risk of overfitting on small datasets."
        )

    st.markdown("#### When to choose which rank")
    st.table({
        "Rank r": ["1–4", "8 (default)", "16–32", "64+"],
        "Best for": [
            "Extreme memory constraint, simple style tasks",
            "Most fine-tuning tasks — instruction following, classification",
            "Complex domain adaptation, more training data available",
            "Near full fine-tune quality, large dataset, high GPU budget",
        ],
        "Risk": [
            "Underfitting — model can't learn enough",
            "Balanced — works for most cases",
            "Overfitting on small datasets",
            "Approaching full fine-tune cost",
        ],
    })
