"""UC2 — Insights: Interview Q&A and connected concepts for LoRA Architecture."""

import streamlit as st


def render() -> None:
    st.subheader("💡 Insights — LoRA Architecture")

    st.markdown("#### LoRA at a glance")
    st.table({
        "Concept": [
            "Full weight update", "LoRA decomposition", "ΔW formula",
            "B init", "A init", "Effective scaling",
        ],
        "Formula / Value": [
            "W' = W + ΔW", "ΔW = B × A", "(α/r) × B × A",
            "B = 0", "A ~ N(0, σ²)", "α/r",
        ],
        "Why": [
            "Standard fine-tuning — updates all d×d params",
            "Low-rank factorization — 2dr << d² params",
            "Scale update magnitude independent of r",
            "Ensures ΔW = 0 at training start → no disruption",
            "Breaks symmetry so gradients flow",
            "Keeps update magnitude consistent as r changes",
        ],
    })

    st.divider()
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions asked in ML Engineering interviews about LoRA and PEFT.")

    qa_pairs = [
        (
            "Why does low-rank approximation work for fine-tuning?",
            "Experimental evidence (Aghajanyan et al., 2020) shows that the weight updates ΔW "
            "during fine-tuning have low intrinsic dimensionality — the meaningful signal "
            "for task adaptation lives in a much lower-dimensional subspace than the full d×d matrix.\n\n"
            "Intuitively: a model with 7B pre-trained parameters already 'knows' most of the world. "
            "Fine-tuning on a narrow task (e.g. classification, style) only needs to push a small "
            "set of directions in weight space. A rank-8 approximation captures these directions "
            "without wasting capacity on irrelevant ones. "
            "In practice, r=8 matches full fine-tune quality for most tasks at < 0.1% of the trainable params."
        ),
        (
            "How do you choose the LoRA rank r?",
            "Guidelines:\n"
            "- **r=4**: extreme memory constraint or very simple task (style-only, binary classification)\n"
            "- **r=8**: default for most tasks — instruction following, summarization, classification\n"
            "- **r=16**: more complex domain adaptation, if you have 5k+ training examples\n"
            "- **r=32+**: approaching full fine-tune quality, useful when you need maximum expressiveness\n\n"
            "Practical approach: start with r=8, evaluate on a held-out validation set, "
            "then increase r only if you observe clear underfitting (loss not decreasing, "
            "validation quality plateau). Higher r increases risk of overfitting on small datasets."
        ),
        (
            "What is the relationship between alpha and r, and how do you set alpha?",
            "Alpha (α) is a scaling hyperparameter for the LoRA update: "
            "ΔW_eff = (α/r) × B×A. "
            "The scaling ensures that the update magnitude stays consistent as you change r.\n\n"
            "Common convention: set α = r (e.g. r=8, α=8) — this gives scaling = 1.0. "
            "Or set α = 2r (e.g. r=8, α=16) — scaling = 2.0, slightly larger updates. "
            "The QLoRA paper recommends α = r as a starting point. "
            "In practice, α is less sensitive than r — most practitioners fix α=16 regardless of r "
            "and just tune r."
        ),
        (
            "Which weight matrices should you apply LoRA to (target_modules)?",
            "Standard choice: `['q_proj', 'v_proj']` — the query and value projections "
            "in each attention layer. This is the original LoRA paper configuration.\n\n"
            "More comprehensive: `['q_proj', 'k_proj', 'v_proj', 'o_proj']` — all 4 attention projections. "
            "~2× more trainable params but better quality on complex tasks.\n\n"
            "Extended: add MLP layers (`['gate_proj', 'up_proj', 'down_proj']`) "
            "for tasks requiring factual knowledge changes. "
            "Rule: start with q+v, add more if quality is insufficient. "
            "Use `model.print_trainable_parameters()` to confirm your config took effect."
        ),
        (
            "How does LoRA compare to other PEFT methods (Prefix Tuning, Adapters, IA³)?",
            "**LoRA**: adds low-rank matrices in parallel to attention weights. "
            "Adapters for inference can be merged (zero overhead). Most popular, best ecosystem support.\n\n"
            "**Prefix Tuning**: prepends trainable 'virtual tokens' to the input. "
            "Does not modify model weights. Works well for generation tasks. "
            "Downside: reduces effective context length.\n\n"
            "**Adapters** (Houlsby): inserts small MLP bottleneck modules between transformer layers. "
            "Cannot be merged — adds inference latency.\n\n"
            "**IA³**: scales attention keys/values and MLP activations with learned vectors. "
            "Fewest trainable params of all methods. Fast but lower capacity.\n\n"
            "**When to use LoRA**: default choice for most tasks. "
            "Use IA³ if you need the absolute minimum trainable params. "
            "Use Prefix Tuning if you cannot modify model weights at all."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        (
            "Singular Value Decomposition (SVD)",
            "The mathematical foundation for low-rank approximations. "
            "Any matrix M can be written as M = UΣV^T. "
            "Keeping only the top-r singular values gives the best rank-r approximation (Eckart–Young theorem). "
            "LoRA doesn't use SVD at training time, but the intuition is the same: "
            "the most important 'directions' can be captured with a small r.",
        ),
        (
            "QLoRA (Quantized LoRA)",
            "Combines LoRA with 4-bit quantization (NF4 or INT4). "
            "The base model is loaded in 4-bit (bitsandbytes library), "
            "while LoRA adapters train in fp16. "
            "Result: 65B models trainable on a single 48 GB GPU. "
            "Paper: Dettmers et al. (2023). Library: `bitsandbytes` + PEFT.",
        ),
        (
            "Rank-Deficiency in Neural Networks",
            "Empirical observation that gradient and weight matrices in trained neural networks "
            "are often close to low-rank. This explains why LoRA works: "
            "fine-tuning on a narrow domain mostly adjusts a small set of directions. "
            "Reference: Aghajanyan et al. 'Intrinsic Dimensionality' (2020).",
        ),
        (
            "Merge and Unload",
            "After training, LoRA adapters can be merged back into the base weights: "
            "W' = W + (α/r)×B×A. "
            "This produces a single model with zero inference overhead — no extra computation at runtime. "
            "Use `model.merge_and_unload()` in the PEFT library. "
            "Essential for production deployment.",
        ),
        (
            "Multi-LoRA Serving",
            "Production systems often serve many LoRA adapters on top of a single shared base model. "
            "The base model weights are loaded once; adapters are swapped per request. "
            "Frameworks: vLLM (built-in LoRA support), LoRAX, OpenRouter. "
            "This is how cloud providers serve custom fine-tuned models efficiently.",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC3 → PEFT with HuggingFace:** Now that you understand the LoRA math, "
        "see how to implement it in 5 steps using the HuggingFace PEFT library."
    )
