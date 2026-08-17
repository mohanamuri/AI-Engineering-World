"""UC2 — Concept: LoRA Architecture — the math of Low-Rank Adaptation."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — LoRA Architecture")

    st.info(
        "**What you'll learn in this section**\n\n"
        "- Why fine-tuning all 7B parameters is impossible for most teams\n"
        "- The low-rank approximation insight that makes LoRA work\n"
        "- The exact math: W' = W + BA where B ∈ R^(d×r), A ∈ R^(r×d)\n"
        "- How choosing rank r controls the quality/efficiency trade-off\n"
        "- Why initializing B=0 is critical"
    )

    st.markdown(
        "You want to fine-tune LLaMA-7B on your custom dataset. "
        "The model has 7 billion parameters. To train it with standard backpropagation, "
        "you need: the model weights (~14 GB at fp16) + gradients (~14 GB) + "
        "Adam optimizer states (~28 GB) = **~56 GB of GPU memory**. "
        "An A100 80GB costs $3/hour on cloud platforms. Most teams don't have 80 GB GPUs.\n\n"
        "**LoRA (Low-Rank Adaptation) solves this** by never updating the original weights at all. "
        "Instead, it learns a small correction — and the math is surprisingly elegant."
    )

    st.divider()
    st.markdown("### The Problem: Fine-tuning Costs GPU Memory")

    st.table({
        "Component": ["Model weights (fp16)", "Gradients (fp16)", "Adam optimizer (fp32)", "Total"],
        "7B model": ["14 GB", "14 GB", "28 GB", "~56 GB"],
        "13B model": ["26 GB", "26 GB", "52 GB", "~104 GB"],
        "70B model": ["140 GB", "140 GB", "280 GB", "~560 GB"],
        "Single consumer GPU (RTX 3090)": ["24 GB total — barely fits 7B weights alone", "—", "—", "—"],
    })

    st.divider()
    st.markdown("### The LoRA Insight: Weight Updates Are Low-Rank")

    st.markdown(
        "Researchers observed that **the weight updates during fine-tuning have low intrinsic dimensionality** — "
        "meaning the meaningful changes live in a much smaller subspace than the full d×d matrix. "
        "LoRA exploits this by decomposing the weight update ΔW into two small matrices:"
    )

    st.markdown("### Step-by-Step Math")

    steps = [
        (
            "Step 1: The original weight matrix",
            "Each attention layer has weight matrices (Q, K, V, O projections). "
            "For LLaMA-7B, these are W ∈ R^(4096×4096) — each with **16.7 million parameters**.",
            r"W \in \mathbb{R}^{d \times d}, \quad d = 4096",
        ),
        (
            "Step 2: The LoRA decomposition",
            "Instead of updating W directly, LoRA learns two matrices: "
            "B ∈ R^(d×r) and A ∈ R^(r×d), where r << d. "
            "The weight update is their product:",
            r"\Delta W = B \cdot A, \quad B \in \mathbb{R}^{d \times r}, \, A \in \mathbb{R}^{r \times d}",
        ),
        (
            "Step 3: Parameter count reduction",
            "Original: d×d = 4096×4096 = 16,777,216 params. "
            "LoRA (r=8): d×r + r×d = 2×4096×8 = 65,536 params. "
            "That's a **256× reduction** in trainable parameters for this layer.",
            r"\text{LoRA params} = 2dr \ll d^2 \quad \text{(for } r \ll d \text{)}",
        ),
        (
            "Step 4: Initialization — why B=0 is critical",
            "A is initialized with a small Gaussian (random noise). "
            "B is initialized to **zero**. "
            "This means ΔW = B×A = 0 at the start of training — "
            "the fine-tuned model is identical to the base model at step 0. "
            "This prevents any disruption to pre-trained capabilities.",
            r"\Delta W_0 = B_0 \cdot A_0 = 0 \cdot A_0 = 0",
        ),
        (
            "Step 5: Scaling factor α/r",
            "The effective weight update is scaled by α/r: "
            "ΔW_eff = (α/r) × B×A. "
            "α is a hyperparameter (typically set to the same value as r, e.g. both = 16). "
            "The scaling prevents the update magnitude from growing with rank r.",
            r"\Delta W_{\text{eff}} = \frac{\alpha}{r} \cdot B \cdot A",
        ),
        (
            "Step 6: Forward pass with LoRA",
            "At inference, the adapted output is: "
            "h = Wx + ΔW_eff × x = Wx + (α/r)×BA×x. "
            "W is frozen (never updated). Only A and B have gradients.",
            r"h = Wx + \frac{\alpha}{r} B A x",
        ),
    ]

    for title, explanation, formula in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(explanation)
            st.latex(formula)

    st.divider()
    st.markdown("### Choosing the Rank r")

    st.table({
        "Rank r": [1, 4, 8, 16, 32, 64],
        "Trainable params (d=4096, 1 layer)": [
            "8,192", "32,768", "65,536", "131,072", "262,144", "524,288"
        ],
        "Reduction vs full (16.7M)": [
            "2048×", "512×", "256×", "128×", "64×", "32×"
        ],
        "When to use": [
            "Extreme memory constraint, simple task",
            "Style transfer, simple classification",
            "Most tasks (sweet spot default)",
            "Complex tasks, more expressive",
            "Near fine-tune quality, high memory",
            "Approaching full fine-tune",
        ],
    })

    st.divider()
    st.markdown("### Which Matrices to Apply LoRA To?")
    st.markdown(
        "LoRA is typically applied to the attention projection matrices. "
        "The most common `target_modules` configuration:"
    )
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Conservative (fewer params)**")
            st.code('target_modules=["q_proj", "v_proj"]', language="python")
            st.caption("Just Q and V attention projections. Default in most LoRA papers.")
    with col2:
        with st.container(border=True):
            st.markdown("**Comprehensive (more params, better quality)**")
            st.code('target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]', language="python")
            st.caption("All 4 attention projections. Better quality, ~2× more trainable params.")

    st.divider()
    st.markdown("### Why Low-Rank Works")
    st.markdown(
        "The key insight: **fine-tuning mostly adjusts directions in the weight space, not magnitudes**. "
        "Studies show that ΔW during fine-tuning has an effective rank much lower than d. "
        "Arora et al. (2018) showed that for many learning tasks, the weight matrices lie near "
        "a low-dimensional manifold — LoRA exploits this by directly parameterizing that manifold.\n\n"
        "In practice: rank r=8 captures most of the useful adaptation signal "
        "for the vast majority of fine-tuning tasks, including instruction following, "
        "style transfer, and domain adaptation."
    )

    st.success(
        "**Next → Playground:** Adjust d, r, and alpha with sliders and see the "
        "parameter counts and reduction factors update live."
    )
