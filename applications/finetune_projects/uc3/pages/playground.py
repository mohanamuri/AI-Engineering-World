"""UC3 — Playground: Configure PEFT pipeline and generate code."""

import streamlit as st

from applications.finetune_projects.services.peft_demo import (
    PEFTDemoConfig,
    estimate_gpu_memory_gb,
    generate_full_pipeline,
)
from applications.finetune_projects.uc3.constants import PEFT_CONFIG_KEY

_BASE_MODELS = [
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-13b-hf",
    "meta-llama/Meta-Llama-3-8B",
    "mistralai/Mistral-7B-v0.1",
    "google/gemma-2b",
    "google/gemma-7b",
    "microsoft/phi-2",
    "tiiuae/falcon-7b",
]

_TASK_TYPES = ["CAUSAL_LM", "SEQ_CLS", "SEQ_2_SEQ_LM"]

_MODEL_PARAMS_B = {
    "meta-llama/Llama-2-7b-hf": 7.0,
    "meta-llama/Llama-2-13b-hf": 13.0,
    "meta-llama/Meta-Llama-3-8B": 8.0,
    "mistralai/Mistral-7B-v0.1": 7.0,
    "google/gemma-2b": 2.0,
    "google/gemma-7b": 7.0,
    "microsoft/phi-2": 2.7,
    "tiiuae/falcon-7b": 7.0,
}

_STEP_LABELS = {
    "1_install": "Step 1: Install Dependencies",
    "2_lora_config": "Step 2: LoraConfig",
    "3_model_wrap": "Step 3: Load Model + get_peft_model()",
    "4_training_loop": "Step 4: Training Loop",
    "5_inference": "Step 5: Load Adapter + Merge",
}


def render() -> None:
    st.subheader("🧪 Playground — PEFT Code Generator")

    st.markdown(
        "Configure your model and training setup. "
        "The playground generates production-ready code for each step of the PEFT pipeline."
    )

    col_cfg, col_adv = st.columns(2)

    with col_cfg:
        with st.container(border=True):
            st.markdown("**Base Model & Task**")
            base_model = st.selectbox(
                "Base model",
                options=_BASE_MODELS,
                key="finetune_uc3_base_model",
            )
            task_type = st.selectbox(
                "Task type",
                options=_TASK_TYPES,
                help="CAUSAL_LM for instruction/chat, SEQ_CLS for classification, SEQ_2_SEQ_LM for T5-style",
                key="finetune_uc3_task_type",
            )
            target_modules_input = st.multiselect(
                "Target modules",
                options=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                default=["q_proj", "v_proj"],
                help="Which weight matrices to apply LoRA to.",
                key="finetune_uc3_target_mods",
            )

        with st.container(border=True):
            st.markdown("**LoRA Config**")
            r = st.slider("Rank r", 1, 64, value=8, key="finetune_uc3_r")
            alpha = st.slider("Alpha", 4, 128, value=16, key="finetune_uc3_alpha")
            dropout = st.slider("LoRA dropout", 0.0, 0.5, step=0.05, value=0.1, key="finetune_uc3_dropout")

    with col_adv:
        with st.container(border=True):
            st.markdown("**Training Config**")
            batch_size = st.slider("Batch size per device", 1, 16, value=4, key="finetune_uc3_batch")
            lr = st.select_slider(
                "Learning rate",
                options=[1e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3],
                value=2e-4,
                format_func=lambda x: f"{x:.0e}",
                key="finetune_uc3_lr",
            )
            epochs = st.slider("Epochs", 1, 10, value=3, key="finetune_uc3_epochs")
            max_seq_len = st.select_slider(
                "Max sequence length",
                options=[128, 256, 512, 1024, 2048],
                value=512,
                key="finetune_uc3_seq_len",
            )

        with st.container(border=True):
            st.markdown("**GPU Memory Estimate**")
            params_b = _MODEL_PARAMS_B.get(base_model, 7.0)
            mem = estimate_gpu_memory_gb(params_b, r)
            st.metric("Full fine-tune", f"{mem['full_finetune_gb']:.0f} GB")
            st.metric("LoRA (8-bit base)", f"{mem['lora_gb']:.0f} GB")
            st.metric("Memory savings", f"{mem['savings_pct']:.0f}%")

    config = PEFTDemoConfig(
        base_model=base_model,
        task_type=task_type,
        r=r,
        lora_alpha=alpha,
        target_modules=target_modules_input or ["q_proj", "v_proj"],
        lora_dropout=dropout,
        batch_size=batch_size,
        lr=lr,
        epochs=epochs,
        max_seq_len=max_seq_len,
    )
    st.session_state[PEFT_CONFIG_KEY] = config

    st.divider()
    st.markdown("### Generated PEFT Pipeline")

    pipeline = generate_full_pipeline(config)

    for step_key, step_label in _STEP_LABELS.items():
        with st.expander(step_label, expanded=(step_key == "1_install")):
            lang = "bash" if step_key == "1_install" else "python"
            st.code(pipeline[step_key], language=lang)

    st.divider()
    st.markdown("#### Verify your setup")
    st.markdown(
        "After wrapping the model with `get_peft_model()`, always run:"
    )
    st.code("model.print_trainable_parameters()", language="python")
    st.markdown(
        "Expected output format: "
        "`trainable params: X || all params: Y || trainable%: Z`\n\n"
        f"For {base_model} with r={r}: expect trainable% between 0.01% and 1%."
    )

    st.info(
        "**No GPU needed here** — this is a code walkthrough. "
        "Copy any section and run it locally when you have GPU access."
    )
