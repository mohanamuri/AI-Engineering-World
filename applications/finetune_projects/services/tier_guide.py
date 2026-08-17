"""Shared Tier Guide page — shown in every Fine-tuning UC."""

import streamlit as st


def render() -> None:
    st.subheader("📋 Fine-tuning Techniques — Series Guide")

    st.markdown(
        """
        This project covers **4 essential fine-tuning concepts** that every ML engineer needs to know.
        Each use case answers a real question you will face when moving from "use the API" to
        "build a production-ready custom model."

        **No GPU required** — all demos are code walkthroughs and math visualizations.
        You learn the concepts and patterns without needing any training hardware.
        """
    )

    st.divider()
    st.markdown("### The 4 Use Cases at a Glance")
    st.markdown("*Each row answers one of the most-asked fine-tuning interview questions.*")

    rows = [
        {
            "uc": "UC1",
            "technique": "Fine-tune vs RAG",
            "concern": "Architecture Decision",
            "icon": "🔀",
            "interview_q": "When should you fine-tune a model vs use RAG?",
            "one_line": "Rule-based decision tree — plug in your scenario constraints and get a reasoned recommendation.",
        },
        {
            "uc": "UC2",
            "technique": "LoRA Architecture",
            "concern": "Parameter Efficiency",
            "icon": "🔢",
            "interview_q": "How does LoRA reduce GPU memory requirements for fine-tuning?",
            "one_line": "Replace d×d weight updates with two small matrices (d×r and r×d) — same expressiveness, 48× fewer trainable params.",
        },
        {
            "uc": "UC3",
            "technique": "PEFT with HuggingFace",
            "concern": "Implementation",
            "icon": "🤗",
            "interview_q": "How do you fine-tune a 7B model on a single GPU?",
            "one_line": "LoraConfig → get_peft_model → Trainer — five steps from base model to trained adapter.",
        },
        {
            "uc": "UC4",
            "technique": "Instruction Tuning",
            "concern": "Data Preparation",
            "icon": "📝",
            "interview_q": "What format should your fine-tuning dataset be in?",
            "one_line": "Alpaca for simplicity, ChatML for chat models, ShareGPT for multi-turn — know when to use each.",
        },
    ]

    for r in rows:
        with st.container(border=True):
            col_badge, col_content = st.columns([1, 5])
            with col_badge:
                st.markdown(f"### {r['icon']}")
                st.markdown(f"**{r['uc']}**")
            with col_content:
                st.markdown(f"#### {r['technique']}")
                st.markdown(f"*Concern: {r['concern']}*")
                st.markdown(f"**{r['one_line']}**")
                st.caption(f"Interview question this answers: \"{r['interview_q']}\"")

    st.divider()
    st.markdown("### What Each UC Teaches — In Plain English")

    with st.expander("UC1 — Fine-tune vs RAG", expanded=False):
        st.markdown(
            """
            **The problem:** Engineers reach for fine-tuning when RAG would have been faster and cheaper
            — or they build a RAG pipeline when the real need was consistent output style.
            A wrong architectural decision wastes weeks.

            **The solution:** A clear decision framework based on 3 questions:
            1. Does the knowledge change frequently? → RAG wins
            2. Do you have 500+ labeled examples? → Fine-tuning becomes viable
            3. Is latency critical (< 200 ms)? → Fine-tuning wins (no retrieval step)

            **You will learn:**
            - The full decision tree with confidence levels
            - Real-world scenarios mapped to the right approach
            - When to use BOTH (fine-tune style + RAG for knowledge)
            - Common mistakes engineers make when choosing
            """
        )

    with st.expander("UC2 — LoRA Architecture", expanded=False):
        st.markdown(
            """
            **The problem:** Fine-tuning a 7B model requires updating 7 billion parameters —
            that needs ~80 GB of GPU memory for gradients + optimizer states.
            Most teams don't have this hardware.

            **The solution (LoRA):** Instead of updating W directly, learn a low-rank decomposition
            ΔW = B × A where B ∈ R^(d×r) and A ∈ R^(r×d).
            With r=8 and d=4096: original 16M params → 65K LoRA params (**99.6% reduction**).

            **You will learn:**
            - The mathematical intuition: why low-rank works
            - How to calculate trainable parameter counts
            - Why B is initialized to zero (ensures ΔW=0 at training start)
            - How rank r controls the quality/efficiency trade-off
            """
        )

    with st.expander("UC3 — PEFT with HuggingFace", expanded=False):
        st.markdown(
            """
            **The problem:** Even with LoRA theory understood, translating it to working code
            involves many moving parts: model loading, quantization, config, training loop, saving.

            **The solution:** HuggingFace PEFT library provides a clean API:
            `LoraConfig` → `get_peft_model()` → `Trainer` → `merge_and_unload()`.
            Five clear steps that always follow the same pattern.

            **You will learn:**
            - The full PEFT pipeline in runnable code
            - How 8-bit quantization (bitsandbytes) further reduces GPU memory
            - How `print_trainable_parameters()` confirms you set up LoRA correctly
            - How to merge adapters back into the base model for production deployment
            """
        )

    with st.expander("UC4 — Instruction Tuning", expanded=False):
        st.markdown(
            """
            **The problem:** A base language model (trained to predict the next token) cannot
            reliably follow instructions. It needs to be taught the instruction-following behaviour
            through supervised fine-tuning on (instruction, response) pairs.

            **The solution:** Instruction tuning on a carefully formatted dataset.
            The format matters — Alpaca, ChatML, and ShareGPT are not interchangeable.
            Use the wrong format and training will fail silently.

            **You will learn:**
            - The difference between Alpaca, ChatML, and ShareGPT formats
            - Why data quality matters more than quantity (1k curated > 100k noisy)
            - How to structure your dataset for different model families
            - The full data quality checklist before you start training
            """
        )

    st.divider()
    st.markdown("### How These Connect in Practice — The Full Fine-tuning Workflow")
    st.markdown(
        """
        In a real fine-tuning project, you apply all four lessons in sequence:

        ```
        Step 1 — UC1: Decision
            Should I fine-tune or use RAG?
            → Run the decision framework with your scenario constraints
            → Fine-tuning chosen for: style, classification, latency-critical tasks

        Step 2 — UC4: Data Preparation
            Collect and format your instruction tuning dataset
            → Pick format: Alpaca (simple) / ChatML (chat model) / ShareGPT (multi-turn)
            → Apply quality checklist: diversity, balance, no contamination

        Step 3 — UC2: Architecture Choice
            Choose LoRA rank r based on your GPU budget and quality target
            → r=4  → ~99.9% param reduction, fastest, may underfit complex tasks
            → r=8  → sweet spot for most tasks (default)
            → r=16 → more capacity, 2× memory vs r=8
            → r=64 → near full fine-tune quality, high memory

        Step 4 — UC3: Implementation
            Run the PEFT pipeline:
            LoraConfig → get_peft_model → Trainer → merge_and_unload
            → Verify trainable params with print_trainable_parameters()
            → Use 8-bit quantization to fit on a single consumer GPU
        ```

        Together, these four concepts enable you to go from "I have a dataset" to
        "I have a production-deployed custom model" without needing a GPU cluster.
        """
    )
