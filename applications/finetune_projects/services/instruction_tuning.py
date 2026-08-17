"""Instruction tuning dataset formats: Alpaca, ChatML, ShareGPT."""
from __future__ import annotations
from dataclasses import dataclass, field
import json


@dataclass
class InstructExample:
    instruction: str
    input: str = ""
    output: str = ""
    system: str = ""
    history: list[tuple[str, str]] | None = None


SAMPLE_EXAMPLES = [
    InstructExample(
        instruction="Summarize the following text in one sentence.",
        input="Remote work has increased flexibility for employees but also created challenges around work-life balance, communication, and team cohesion.",
        output="Remote work boosts flexibility but challenges balance, communication, and team cohesion.",
    ),
    InstructExample(
        instruction="Classify the sentiment of this review.",
        input="The product arrived on time and works perfectly. Highly recommended!",
        output="Positive",
    ),
    InstructExample(
        instruction="Translate to formal English.",
        input="hey can u pls send me the report asap thx",
        output="Could you please send me the report at your earliest convenience? Thank you.",
    ),
    InstructExample(
        instruction="Write a Python function that checks if a number is prime.",
        input="",
        output="def is_prime(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0: return False\n    return True",
    ),
]


def format_alpaca(example: InstructExample) -> dict:
    """Stanford Alpaca format."""
    entry = {
        "instruction": example.instruction,
        "input": example.input,
        "output": example.output,
    }
    if example.input:
        prompt = f"### Instruction:\n{example.instruction}\n\n### Input:\n{example.input}\n\n### Response:\n{example.output}"
    else:
        prompt = f"### Instruction:\n{example.instruction}\n\n### Response:\n{example.output}"
    return {"data": entry, "formatted_prompt": prompt}


def format_chatml(example: InstructExample) -> dict:
    """OpenAI ChatML format used by many modern models."""
    messages = []
    if example.system:
        messages.append({"role": "system", "content": example.system})
    user_content = f"{example.instruction}\n\n{example.input}".strip() if example.input else example.instruction
    messages.append({"role": "user", "content": user_content})
    messages.append({"role": "assistant", "content": example.output})

    formatted = ""
    if example.system:
        formatted += f"<|im_start|>system\n{example.system}<|im_end|>\n"
    formatted += f"<|im_start|>user\n{user_content}<|im_end|>\n"
    formatted += f"<|im_start|>assistant\n{example.output}<|im_end|>"

    return {"messages": messages, "formatted_prompt": formatted}


def format_sharegpt(example: InstructExample) -> dict:
    """ShareGPT multi-turn format."""
    conversations = []
    if example.system:
        conversations.append({"from": "system", "value": example.system})
    user_content = f"{example.instruction}\n\n{example.input}".strip() if example.input else example.instruction
    conversations.append({"from": "human", "value": user_content})
    conversations.append({"from": "gpt", "value": example.output})
    return {"conversations": conversations}


def get_dataset_quality_checklist() -> list[dict]:
    """Quality criteria for instruction tuning datasets."""
    return [
        {"criterion": "Diversity", "target": "> 50% unique instruction patterns", "why": "Prevents overfitting to specific phrasings"},
        {"criterion": "Length balance", "target": "Mix of short and long outputs", "why": "Ensures model learns to be concise AND detailed"},
        {"criterion": "Difficulty spread", "target": "Easy / Medium / Hard examples", "why": "Generalises across query complexity"},
        {"criterion": "No contamination", "target": "No test set leakage", "why": "Prevents falsely inflated benchmarks"},
        {"criterion": "Output quality", "target": "Human-reviewed samples", "why": "Garbage in, garbage out"},
        {"criterion": "Format consistency", "target": "Same template throughout", "why": "Model learns the format, not noise"},
    ]


def format_as_json_download(example: InstructExample, fmt: str) -> str:
    """Return formatted example as a JSON string for download."""
    if fmt == "Alpaca":
        data = format_alpaca(example)["data"]
    elif fmt == "ChatML":
        data = {"messages": format_chatml(example)["messages"]}
    elif fmt == "ShareGPT":
        data = format_sharegpt(example)
    else:
        data = {}
    return json.dumps(data, indent=2)
