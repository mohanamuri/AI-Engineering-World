"""PEFT/LoRA code walkthrough — generates formatted code strings for st.code()."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PEFTDemoConfig:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    task_type: str = "CAUSAL_LM"  # "CAUSAL_LM", "SEQ_CLS", "SEQ_2_SEQ_LM"
    r: int = 8
    lora_alpha: int = 16
    target_modules: list[str] | None = None
    lora_dropout: float = 0.1
    batch_size: int = 4
    lr: float = 2e-4
    epochs: int = 3
    max_seq_len: int = 512


def generate_install_code() -> str:
    return """pip install transformers peft datasets accelerate bitsandbytes"""


def generate_lora_config_code(config: PEFTDemoConfig) -> str:
    targets = config.target_modules or ["q_proj", "v_proj"]
    targets_str = str(targets)
    return f'''from peft import LoraConfig, TaskType

lora_config = LoraConfig(
    task_type=TaskType.{config.task_type},
    r={config.r},                          # LoRA rank — lower = fewer params
    lora_alpha={config.lora_alpha},                  # scaling = alpha/r = {config.lora_alpha/config.r}
    target_modules={targets_str},  # which weight matrices to adapt
    lora_dropout={config.lora_dropout},
    bias="none",
)

# This alone reduces trainable params by ~{int(config.r * 2 * 4096 * 2 / (4096 * 4096) * 100 * 32)}× for a 7B model'''


def generate_model_wrap_code(config: PEFTDemoConfig) -> str:
    return f'''from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model

# Load the base model (frozen)
base_model = AutoModelForCausalLM.from_pretrained(
    "{config.base_model}",
    load_in_8bit=True,      # quantize to 8-bit to fit in GPU memory
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained("{config.base_model}")
tokenizer.pad_token = tokenizer.eos_token

# Wrap with LoRA adapters — only A and B matrices are trainable
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()
# Output: trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.0622'''


def generate_training_loop_code(config: PEFTDemoConfig) -> str:
    return f'''from transformers import TrainingArguments, Trainer
from datasets import load_dataset

# Load and tokenize your dataset
dataset = load_dataset("json", data_files={{"train": "train.jsonl"}})

def tokenize(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length={config.max_seq_len},
        padding="max_length",
    )

tokenized = dataset.map(tokenize, batched=True)

# Training config
training_args = TrainingArguments(
    output_dir="./lora-output",
    num_train_epochs={config.epochs},
    per_device_train_batch_size={config.batch_size},
    learning_rate={config.lr},
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    fp16=True,                  # mixed precision to save memory
    logging_steps=10,
    save_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
)
trainer.train()'''


def generate_inference_code(config: PEFTDemoConfig) -> str:
    return f'''from peft import PeftModel

# Load the base model + merge LoRA adapters for inference
base_model = AutoModelForCausalLM.from_pretrained("{config.base_model}")
model = PeftModel.from_pretrained(base_model, "./lora-output")

# Optional: merge adapters into base weights for faster inference
model = model.merge_and_unload()

# Use like a regular model
inputs = tokenizer("Your prompt here", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))'''


def generate_full_pipeline(config: PEFTDemoConfig) -> dict[str, str]:
    return {
        "1_install": generate_install_code(),
        "2_lora_config": generate_lora_config_code(config),
        "3_model_wrap": generate_model_wrap_code(config),
        "4_training_loop": generate_training_loop_code(config),
        "5_inference": generate_inference_code(config),
    }


def estimate_gpu_memory_gb(base_model_params_b: float, r: int, precision_bits: int = 16) -> dict[str, float]:
    """Rough GPU memory estimate for full fine-tune vs LoRA."""
    bytes_per_param = precision_bits / 8

    # Full fine-tune: params + gradients + optimizer states (Adam = 2x params)
    full_params_gb = (base_model_params_b * 1e9 * bytes_per_param) / 1e9
    full_gradients_gb = full_params_gb
    full_optimizer_gb = full_params_gb * 2  # Adam m and v states
    full_total_gb = full_params_gb + full_gradients_gb + full_optimizer_gb

    # LoRA: frozen base (inference only) + small adapter gradients
    # Base model in 8-bit = half memory
    lora_base_gb = (base_model_params_b * 1e9 * 1) / 1e9  # 8-bit = 1 byte
    # LoRA params: ~0.1% of base for r=8
    lora_adapter_params = base_model_params_b * 1e9 * 0.001 * (r / 8)
    lora_adapter_gb = (lora_adapter_params * bytes_per_param * 3) / 1e9  # params + grad + optim
    lora_total_gb = lora_base_gb + lora_adapter_gb

    return {
        "full_finetune_gb": round(full_total_gb, 1),
        "lora_gb": round(lora_total_gb, 1),
        "savings_pct": round((1 - lora_total_gb / full_total_gb) * 100, 1),
    }
