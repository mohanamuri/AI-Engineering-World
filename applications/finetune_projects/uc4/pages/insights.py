"""UC4 — Insights: Interview Q&A and connected concepts for Instruction Tuning."""

import streamlit as st


def render() -> None:
    st.subheader("💡 Insights — Instruction Tuning")

    st.markdown("#### Format quick reference")
    st.table({
        "Format": ["Alpaca", "ChatML", "ShareGPT"],
        "Structure": [
            "### Instruction / ### Input / ### Response",
            "<|im_start|>role ... <|im_end|>",
            "{from: human/gpt, value: ...}",
        ],
        "System prompt": ["No", "Yes", "Yes"],
        "Multi-turn": ["No", "Yes", "Yes (native)"],
        "When to use": [
            "Single-turn, older models, simple tasks",
            "Most modern models (default choice 2024+)",
            "Conversational datasets, ChatGPT distillation",
        ],
    })

    st.divider()
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions asked in ML Engineering interviews about instruction tuning and SFT.")

    qa_pairs = [
        (
            "What is the difference between instruction tuning and RLHF?",
            "**Instruction tuning** (also called Supervised Fine-Tuning / SFT) trains the model "
            "on (instruction, ideal_response) pairs using standard cross-entropy loss. "
            "The model learns to produce the exact response in the training data.\n\n"
            "**RLHF** (Reinforcement Learning from Human Feedback) has two additional steps:\n"
            "1. A reward model is trained on human preference comparisons "
            "(response A vs response B — which is better?)\n"
            "2. The language model is fine-tuned using PPO (Proximal Policy Optimization) "
            "to maximize the reward model's score.\n\n"
            "In practice: SFT is the foundation that runs first; RLHF builds on top of an SFT model. "
            "Modern alternatives to RLHF (DPO, ORPO) use the preference data directly without a separate "
            "reward model, making them much simpler to implement."
        ),
        (
            "How many examples do you need for instruction tuning?",
            "The LIMA paper (2023) answered this empirically: **1,000 carefully curated examples** "
            "were enough to produce a strong instruction-following model from LLaMA-65B. "
            "The quality of examples mattered far more than quantity.\n\n"
            "Practical guidelines:\n"
            "- **< 100**: too few — use few-shot prompting\n"
            "- **500–2,000**: viable for a single focused skill (classification, summarization, style)\n"
            "- **2,000–10,000**: good general instruction following\n"
            "- **10,000–50,000**: strong multi-skill generalization\n"
            "- **> 50,000**: diminishing returns, data curation becomes the bottleneck\n\n"
            "Key caveat: 10,000 noisy examples often underperforms 1,000 clean ones. "
            "Invest in curation before scaling volume."
        ),
        (
            "What is the difference between data quality and data quantity in fine-tuning?",
            "Data quantity increases coverage (more instruction types, more edge cases). "
            "Data quality ensures each example teaches the right behaviour.\n\n"
            "**Quality signals to check:**\n"
            "- Factual accuracy of outputs (wrong facts teach wrong behavior)\n"
            "- Format consistency (same template for all examples)\n"
            "- Instruction diversity (> 50% unique instruction patterns)\n"
            "- Length balance (mix of short and long responses)\n"
            "- No test set leakage (never train on held-out eval examples)\n\n"
            "**Rule of thumb**: always prefer a 1,000-example human-reviewed dataset "
            "over a 100,000-example GPT-4-generated-but-unreviewed dataset. "
            "A 5% sample review (checking 50 random examples) is enough to spot systematic issues."
        ),
        (
            "How do you prevent catastrophic forgetting during instruction tuning?",
            "Catastrophic forgetting occurs when fine-tuning on a narrow task causes the model "
            "to lose general capabilities (reasoning, world knowledge, language quality).\n\n"
            "Mitigation strategies:\n\n"
            "1. **LoRA** — since base weights are frozen, forgetting is largely prevented. "
            "The most reliable approach.\n\n"
            "2. **Low learning rate** — use 1e-5 to 5e-5 for full fine-tuning "
            "(vs 1e-4 for LoRA adapters). Slow updates preserve general knowledge.\n\n"
            "3. **Mixed training data** — include a sample of general instruction data "
            "(e.g. 20% Alpaca/FLAN) alongside your domain data.\n\n"
            "4. **Replay** — periodically evaluate on a general benchmark (MMLU, HellaSwag) "
            "during fine-tuning and stop if general performance drops.\n\n"
            "5. **Elastic Weight Consolidation (EWC)** — penalizes changes to parameters "
            "important for previous tasks. Rarely used in practice; LoRA + low LR is simpler."
        ),
        (
            "How do you evaluate an instruction-tuned model?",
            "Evaluation is harder than training — there is no single ground-truth for instruction following.\n\n"
            "**Automated metrics:**\n"
            "- **Held-out test set** — compute exact match or ROUGE against reference outputs\n"
            "- **LLM-as-judge** — use GPT-4 or Claude to score response quality on 1-5 scale "
            "(MT-Bench methodology)\n"
            "- **Task-specific benchmarks** — for classification: F1/accuracy; "
            "for summarization: ROUGE; for code: pass@k\n\n"
            "**Human evaluation (gold standard):**\n"
            "- A/B comparison: show humans two model outputs, ask which is better\n"
            "- Absolute rating: score responses on helpfulness, accuracy, safety\n\n"
            "**Production evaluation:**\n"
            "- Track user engagement metrics (thumbs up/down, edit rate)\n"
            "- Monitor for refusals on legitimate queries and hallucinations on factual ones\n\n"
            "Recommendation: start with LLM-as-judge for fast iteration, "
            "then run human evaluation on the final model before deployment."
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
            "HuggingFace's `trl` library provides `SFTTrainer`, optimized for instruction tuning. "
            "Key features: response masking (loss computed only on assistant's output, not instruction), "
            "sequence packing (batches multiple short examples into one sequence for efficiency), "
            "and native support for all three formats (Alpaca, ChatML, ShareGPT via `dataset_text_field`).",
        ),
        (
            "Response Masking",
            "During training, you only want the model to predict the assistant's response tokens, "
            "not the instruction tokens (which are always the same). "
            "Response masking sets the instruction token labels to -100 (ignored by cross-entropy loss). "
            "Without masking, the model wastes capacity learning to predict the instruction template "
            "it already sees perfectly.",
        ),
        (
            "DPO (Direct Preference Optimization)",
            "A simpler alternative to RLHF that uses preference data (chosen/rejected pairs) "
            "without training a separate reward model. "
            "Trains the model directly to prefer chosen responses over rejected ones. "
            "Implemented in HuggingFace TRL's `DPOTrainer`. "
            "Most modern open-source models use SFT + DPO instead of SFT + RLHF.",
        ),
        (
            "Chat Templates",
            "Modern tokenizers include a `chat_template` attribute — a Jinja2 template "
            "that defines how to format messages for that specific model. "
            "Always use `tokenizer.apply_chat_template()` instead of manually formatting "
            "to ensure consistency between training and inference. "
            "Mismatched templates between training and inference is a common source of degraded performance.",
        ),
        (
            "Sequence Packing",
            "Instead of padding short examples to `max_length`, pack multiple short examples "
            "end-to-end into a single sequence. "
            "This increases GPU utilization and speeds up training significantly "
            "(no wasted compute on padding tokens). "
            "Enabled via `packing=True` in TRL's SFTTrainer.",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "You've completed all 4 Fine-tuning use cases. "
        "You now have the full workflow: UC1 (decide) → UC4 (prepare data) → "
        "UC2 (understand LoRA) → UC3 (write the code). "
        "You're ready to fine-tune your first model."
    )
