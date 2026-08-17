"""UC3 — Concept: PEFT — Parameter-Efficient Fine-Tuning with HuggingFace."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — PEFT with HuggingFace")

    st.info(
        "**What you'll learn in this section**\n\n"
        "- What PEFT is and which methods it covers (LoRA, Prefix Tuning, Adapters, IA³)\n"
        "- Why HuggingFace PEFT library is the standard implementation tool\n"
        "- The 5-step pipeline from base model to trained adapter\n"
        "- GPU memory comparison: full fine-tune vs LoRA vs QLoRA"
    )

    st.markdown(
        "You know LoRA's math. Now let's translate it into working code. "
        "HuggingFace's `peft` library wraps LoRA (and other methods) in a clean API "
        "that integrates directly with `transformers`, `datasets`, and `Trainer`. "
        "The same 5-step pattern works for any model from GPT-2 to LLaMA-70B."
    )

    st.divider()
    st.markdown("### What is PEFT?")

    st.markdown(
        "**PEFT** (Parameter-Efficient Fine-Tuning) is an umbrella term for techniques "
        "that adapt a pre-trained model to a new task by training only a tiny fraction "
        "of the total parameters. HuggingFace's `peft` library provides a unified API "
        "for the four most important PEFT methods:"
    )

    peft_methods = [
        {
            "method": "LoRA",
            "how": "Adds two low-rank matrices (A, B) in parallel with frozen weight matrices",
            "trainable": "< 0.1% of params",
            "inference_overhead": "Zero (merge and unload)",
            "best_for": "Most fine-tuning tasks — instruction following, classification, style",
        },
        {
            "method": "Prefix Tuning",
            "how": "Prepends learned 'virtual tokens' to the input sequence",
            "trainable": "< 0.1% of params",
            "inference_overhead": "Increases effective context length used",
            "best_for": "Text generation, summarization",
        },
        {
            "method": "Adapters (Houlsby)",
            "how": "Inserts small MLP bottleneck modules between transformer layers",
            "trainable": "1–5% of params",
            "inference_overhead": "~10–30% slower inference (extra layers)",
            "best_for": "When you need to swap tasks at runtime without merging",
        },
        {
            "method": "IA³",
            "how": "Scales attention keys/values and MLP activations with learned vectors",
            "trainable": "< 0.01% of params",
            "inference_overhead": "Zero (element-wise scaling merged in)",
            "best_for": "Extreme memory constraint, simple task adaptation",
        },
    ]

    for m in peft_methods:
        with st.container(border=True):
            col_name, col_details = st.columns([1, 4])
            with col_name:
                st.markdown(f"**{m['method']}**")
                st.caption(f"~{m['trainable']}")
            with col_details:
                st.markdown(f"*How:* {m['how']}")
                st.markdown(f"*Inference overhead:* {m['inference_overhead']}")
                st.caption(f"Best for: {m['best_for']}")

    st.divider()
    st.markdown("### The 5-Step PEFT Pipeline")

    steps = [
        (
            "Step 1: Install dependencies",
            "Four libraries cover the full pipeline:",
            "pip install transformers peft datasets accelerate bitsandbytes",
            "bash",
            "`transformers` — model + tokenizer | `peft` — LoRA API | "
            "`datasets` — data loading | `accelerate` — distributed training | "
            "`bitsandbytes` — 8-bit / 4-bit quantization",
        ),
        (
            "Step 2: Define LoraConfig",
            "Specify rank, alpha, target modules, and task type:",
            """from peft import LoraConfig, TaskType

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
)""",
            "python",
            "This is the only place you configure LoRA. "
            "`task_type` tells PEFT how to set up the output layer. "
            "Use `CAUSAL_LM` for GPT-style, `SEQ_CLS` for classification, "
            "`SEQ_2_SEQ_LM` for T5-style models.",
        ),
        (
            "Step 3: Load base model and wrap with get_peft_model()",
            "Load the base model (frozen) and wrap it with the LoRA config:",
            """from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    load_in_8bit=True,      # 8-bit quantization to halve GPU memory
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.0622""",
            "python",
            "`get_peft_model()` freezes all base weights and adds the LoRA adapter matrices. "
            "`print_trainable_parameters()` confirms the setup — always run this to verify.",
        ),
        (
            "Step 4: Train with standard Trainer",
            "Use HuggingFace Trainer exactly as you would for full fine-tuning:",
            """from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./lora-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-4,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)
trainer.train()""",
            "python",
            "Standard Trainer API — no PEFT-specific changes needed here. "
            "Only the LoRA adapter weights are updated during training; "
            "base model gradients are never computed.",
        ),
        (
            "Step 5: Merge adapters and deploy",
            "Merge LoRA adapters back into base weights for zero-overhead inference:",
            """from peft import PeftModel

# Load base + adapter
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
model = PeftModel.from_pretrained(base_model, "./lora-output")

# Merge for production (zero inference overhead)
model = model.merge_and_unload()

# Use like a normal model
inputs = tokenizer("Your prompt here", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))""",
            "python",
            "`merge_and_unload()` mathematically merges W' = W + (α/r)×BA into a single matrix. "
            "The result behaves identically to the fine-tuned model but with no extra parameters.",
        ),
    ]

    for i, (title, description, code, lang, note) in enumerate(steps, 1):
        with st.container(border=True):
            st.markdown(f"**{i}. {title}**")
            st.write(description)
            st.code(code, language=lang)
            st.caption(note)

    st.divider()
    st.markdown("### GPU Memory: Full Fine-tune vs LoRA vs QLoRA")

    st.table({
        "Method": ["Full fine-tune (fp16)", "LoRA (fp16 base)", "LoRA + 8-bit (bitsandbytes)", "QLoRA (4-bit base)"],
        "7B model GPU RAM": ["~56 GB", "~28 GB", "~14 GB", "~8 GB"],
        "13B model GPU RAM": ["~104 GB", "~52 GB", "~26 GB", "~14 GB"],
        "Accessible on": [
            "A100 80 GB (expensive)",
            "A100 40 GB",
            "RTX 3090 24 GB",
            "RTX 3060 12 GB",
        ],
    })

    st.success(
        "**Next → Playground:** Configure your base model, task type, LoRA settings, "
        "and generate the complete 5-step pipeline code."
    )
