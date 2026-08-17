"""UC3 — Compare: Full fine-tuning vs LoRA PEFT code side by side."""

import streamlit as st


_FULL_FINETUNE_CONFIG = """from transformers import AutoModelForCausalLM, AutoTokenizer

# Full fine-tune: load ALL weights in trainable mode
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# ALL 7 billion parameters are trainable
print(sum(p.numel() for p in model.parameters()))
# 6,738,415,616"""

_LORA_CONFIG = """from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, TaskType, get_peft_model

# Step 1: Load base model in 8-bit (frozen)
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    load_in_8bit=True,      # quantize to 8-bit — halves GPU memory
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

# Step 2: Define LoRA adapters
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
)

# Step 3: Wrap — only 4.2M adapter params are trainable
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.0622"""

_FULL_FINETUNE_TRAIN = """from transformers import TrainingArguments, Trainer

# Full fine-tune training args
training_args = TrainingArguments(
    output_dir="./full-finetune-output",
    num_train_epochs=3,
    per_device_train_batch_size=1,  # only 1 on A100 80GB!
    gradient_accumulation_steps=16, # simulate batch_size=16
    learning_rate=2e-5,             # lower LR for full fine-tune
    fp16=True,
    save_strategy="epoch",
)
# GPU memory needed: ~56 GB (A100 80GB required)
# Training time for 1000 examples: ~2-4 hours on A100"""

_LORA_TRAIN = """from transformers import TrainingArguments, Trainer

# LoRA training args — same API, different hardware requirements
training_args = TrainingArguments(
    output_dir="./lora-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,  # 4x larger batch fits in memory!
    learning_rate=2e-4,             # higher LR works for adapters
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    fp16=True,
    save_strategy="epoch",
)
# GPU memory needed: ~14 GB (RTX 3090 or free Colab T4)
# Training time for 1000 examples: ~20-40 minutes on T4"""

_FULL_FINETUNE_SAVE = """# Full fine-tune saves ALL weights
model.save_pretrained("./full-model")  # ~13 GB on disk
tokenizer.save_pretrained("./full-model")

# Sharing / deploying: upload the full 13 GB model
# Every task needs a separate full model copy"""

_LORA_SAVE = """# LoRA saves ONLY the adapter weights
trainer.save_model("./lora-output")  # ~8-30 MB on disk!
# (just the A and B matrices, not the 13 GB base)

# To load for inference:
from peft import PeftModel
base = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
model = PeftModel.from_pretrained(base, "./lora-output")

# Or merge adapters into base for zero inference overhead:
model = model.merge_and_unload()  # → 13 GB merged model"""


def render() -> None:
    st.subheader("⚖️ Compare — Full Fine-tuning vs LoRA PEFT")

    st.markdown(
        "The same training task, two different approaches. "
        "See exactly what changes when you switch from full fine-tuning to LoRA PEFT."
    )

    # Summary comparison table
    st.markdown("### At a Glance")
    st.table({
        "Dimension": [
            "Trainable parameters", "GPU memory (7B model)",
            "Batch size possible", "Learning rate", "Training time",
            "Saved model size", "Inference overhead", "Update when requirements change",
        ],
        "Full Fine-tune": [
            "7B (100%)", "~56 GB (A100 80GB required)",
            "1–2 per GPU", "1e-5 to 5e-5",
            "2–4 hours on A100", "~13 GB",
            "None (standard model)", "Retrain 7B params from scratch",
        ],
        "LoRA (r=8)": [
            "~4M (0.06%)", "~14 GB (RTX 3090 or free Colab T4)",
            "4–8 per GPU", "1e-4 to 5e-4",
            "20–40 min on T4", "~8–30 MB",
            "None after merge_and_unload()", "Retrain only 4M adapter params",
        ],
    })

    st.divider()

    # Side-by-side code comparison
    st.markdown("### Code Comparison — Model Setup")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Full Fine-tune**")
        st.code(_FULL_FINETUNE_CONFIG, language="python")
    with col2:
        st.markdown("**LoRA PEFT**")
        st.code(_LORA_CONFIG, language="python")

    st.markdown("### Code Comparison — Training Arguments")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Full Fine-tune**")
        st.code(_FULL_FINETUNE_TRAIN, language="python")
    with col2:
        st.markdown("**LoRA PEFT**")
        st.code(_LORA_TRAIN, language="python")

    st.markdown("### Code Comparison — Saving the Model")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Full Fine-tune**")
        st.code(_FULL_FINETUNE_SAVE, language="python")
    with col2:
        st.markdown("**LoRA PEFT**")
        st.code(_LORA_SAVE, language="python")

    st.divider()
    st.markdown("### When to choose each")
    col_full, col_lora = st.columns(2)
    with col_full:
        with st.container(border=True):
            st.markdown("**Use Full Fine-tune when:**")
            st.markdown(
                "- You have access to an A100 80GB+ cluster\n"
                "- You need maximum quality on a very large dataset (50k+ examples)\n"
                "- The task requires changing fundamental model capabilities\n"
                "- Budget and engineering time are not constraints"
            )
    with col_lora:
        with st.container(border=True):
            st.markdown("**Use LoRA when:**")
            st.markdown(
                "- You're on a consumer GPU, free Colab, or cloud with limited budget\n"
                "- You have a focused task with 500–10k examples\n"
                "- You want fast iteration (20 min vs 4 hours per experiment)\n"
                "- You need to serve multiple fine-tuned variants on one base model\n"
                "- **This covers 95% of real-world fine-tuning scenarios**"
            )

    st.success(
        "For the vast majority of ML engineering teams, LoRA is the right default. "
        "Reserve full fine-tuning for cases where you've validated LoRA's quality "
        "is insufficient and you have the GPU budget to justify it."
    )
