"""UC3 — Insights: Interview Q&A and connected concepts for PEFT with HuggingFace."""

import streamlit as st


def render() -> None:
    st.subheader("💡 Insights — PEFT with HuggingFace")

    st.markdown("#### PEFT pipeline checklist")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**Before training**")
            st.markdown(
                "- Run `print_trainable_parameters()` — confirm < 1% trainable\n"
                "- Set `tokenizer.pad_token = tokenizer.eos_token` for causal models\n"
                "- Use `load_in_8bit=True` or `load_in_4bit=True` to save GPU RAM\n"
                "- Validate dataset format matches task_type\n"
                "- Set `fp16=True` in TrainingArguments"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**After training**")
            st.markdown(
                "- Call `model.merge_and_unload()` for production deployment\n"
                "- Compare validation loss to baseline (base model prompted)\n"
                "- Check adapter size on disk (should be MB, not GB)\n"
                "- Test on held-out examples not seen during training\n"
                "- Monitor for catastrophic forgetting on general tasks"
            )

    st.divider()
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions asked in ML Engineering interviews about PEFT and LoRA in production.")

    qa_pairs = [
        (
            "How much GPU memory does LoRA save compared to full fine-tuning?",
            "The savings come from two sources:\n\n"
            "1. **Frozen base model gradients** — since base weights never update, "
            "no gradients are stored for them. This eliminates ~14 GB for a 7B model (at fp16).\n"
            "2. **Quantization** — loading the base model in 8-bit (bitsandbytes) halves weight memory. "
            "Combined: full fine-tune of a 7B model needs ~56 GB; LoRA with 8-bit base needs ~14 GB. "
            "QLoRA (4-bit base) reduces this further to ~8 GB, making 7B fine-tuning possible "
            "on a consumer GPU (RTX 3060 12GB or Colab T4 16GB)."
        ),
        (
            "What does merge_and_unload() do and why is it important for production?",
            "`merge_and_unload()` computes W' = W + (α/r)×B×A for every LoRA-adapted layer "
            "and writes the result back into the base model's weight matrices. "
            "After merging, the LoRA adapter modules are removed entirely.\n\n"
            "Why it matters for production:\n"
            "- Zero inference overhead — no extra matrix multiplications at runtime\n"
            "- Standard model format — deploy like any normal transformers model\n"
            "- Simpler serving infrastructure — no need for LoRA-aware inference servers\n\n"
            "When NOT to merge: if you need to serve multiple LoRA adapters "
            "(different fine-tuned behaviors) on a single base model. "
            "In that case, keep adapters separate and swap them per request (multi-LoRA serving)."
        ),
        (
            "How does bitsandbytes quantization work with LoRA (QLoRA)?",
            "QLoRA (Dettmers et al., 2023) combines:\n\n"
            "1. **NF4 quantization** (4-bit Normal Float) — the base model weights are stored in 4-bit. "
            "The quantization preserves the distribution of neural network weights better than INT4.\n"
            "2. **Double quantization** — quantize the quantization constants themselves, "
            "saving additional memory.\n"
            "3. **Paged optimizers** — use CPU RAM as overflow for optimizer states, "
            "preventing OOM on memory spikes.\n"
            "4. **LoRA adapters in fp16** — the trainable adapter matrices A and B train in full precision.\n\n"
            "In practice: `load_in_4bit=True, bnb_4bit_quant_type='nf4'` in `from_pretrained()`. "
            "This makes 65B models trainable on a single 48 GB GPU."
        ),
        (
            "What are the most common mistakes when setting up PEFT fine-tuning?",
            "Top 5 mistakes:\n\n"
            "1. **Wrong task_type in LoraConfig** — using `CAUSAL_LM` for a classification task "
            "or vice versa. Always match task_type to your model architecture.\n\n"
            "2. **Forgetting pad_token** — causal models (Llama, Mistral) don't have a pad token. "
            "Set `tokenizer.pad_token = tokenizer.eos_token` before tokenization.\n\n"
            "3. **Not verifying trainable_parameters** — always run `print_trainable_parameters()`. "
            "If trainable% is 0% or 100%, your LoraConfig didn't apply correctly.\n\n"
            "4. **Too high learning rate** — full fine-tune uses 1e-5 to 5e-5. "
            "LoRA adapters benefit from higher LRs (1e-4 to 5e-4) because adapters start at zero.\n\n"
            "5. **Serving without merge_and_unload** — unmerged adapters add inference overhead "
            "and require a PEFT-aware serving stack."
        ),
        (
            "How do you serve multiple LoRA adapters efficiently in production?",
            "The multi-LoRA serving pattern:\n\n"
            "**Architecture**: one shared base model loaded once in GPU memory + "
            "N lightweight adapters stored separately (each 8–30 MB).\n\n"
            "**At request time**: identify which adapter is needed (by customer, use-case, or language) "
            "→ load that adapter's A and B matrices → run inference.\n\n"
            "**Frameworks that support this**:\n"
            "- **vLLM** (open source) — built-in LoRA support, concurrent multi-adapter serving\n"
            "- **LoRAX** (Predibase) — specialized multi-LoRA server\n"
            "- **TorchServe** — with custom handler for adapter swapping\n\n"
            "**Economics**: serving 50 fine-tuned 7B variants would normally need "
            "50 × 14 GB = 700 GB of GPU memory. Multi-LoRA serving needs ~14 GB + 50 × 25 MB ≈ 15 GB. "
            "This is the production deployment pattern at scale."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        (
            "SFTTrainer (TRL library)",
            "HuggingFace's `trl` library provides `SFTTrainer` — a Trainer subclass "
            "optimized for supervised fine-tuning. It handles instruction formatting, "
            "packing short sequences into longer ones for efficiency, and response masking "
            "(computing loss only on the assistant's response, not the instruction).",
        ),
        (
            "Gradient Checkpointing",
            "Technique to trade compute for memory: instead of storing all activations "
            "during the forward pass (needed for backprop), recompute them on the fly during backprop. "
            "Reduces activation memory by ~60% at the cost of ~30% slower training. "
            "Enable with `gradient_checkpointing=True` in TrainingArguments.",
        ),
        (
            "Flash Attention 2",
            "Memory-efficient attention implementation that reduces attention memory "
            "from O(n²) to O(n) using tiling. Essential for training on long sequences. "
            "Enable with `attn_implementation='flash_attention_2'` in `from_pretrained()`. "
            "Requires `pip install flash-attn`.",
        ),
        (
            "Wandb / MLflow Training Tracking",
            "Integrate tracking in one line: `report_to='wandb'` in TrainingArguments. "
            "Track: training loss, validation loss, GPU memory usage, learning rate schedule. "
            "Compare multiple LoRA runs with different r values on the same chart.",
        ),
        (
            "GGUF Format for Deployment",
            "After `merge_and_unload()`, convert the merged model to GGUF format "
            "using `llama.cpp`'s `convert.py`. GGUF supports quantized deployment "
            "(4-bit, 5-bit, 8-bit) on CPU-only machines using `llama.cpp` or `ollama`. "
            "This is the standard for deploying custom fine-tuned models locally.",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC4 → Instruction Tuning:** You can now write the training code. "
        "Next: learn how to prepare your dataset in the right format "
        "(Alpaca, ChatML, or ShareGPT) so the model learns the right behavior."
    )
