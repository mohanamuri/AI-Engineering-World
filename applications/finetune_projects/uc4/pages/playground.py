"""UC4 — Playground: Interactive instruction format preview and download."""

import json
import streamlit as st

from applications.finetune_projects.services.instruction_tuning import (
    SAMPLE_EXAMPLES,
    InstructExample,
    format_alpaca,
    format_as_json_download,
    format_chatml,
    format_sharegpt,
)
from applications.finetune_projects.uc4.constants import DATASET_FORMAT_KEY

_SAMPLE_NAMES = [
    "— custom —",
    "Text summarization",
    "Sentiment classification",
    "Formal English translation",
    "Write a Python function",
]

_FORMAT_DESCRIPTIONS = {
    "Alpaca": "Stanford Alpaca format — `### Instruction:` / `### Input:` / `### Response:`",
    "ChatML": "OpenAI ChatML — `<|im_start|>role` ... `<|im_end|>` tokens",
    "ShareGPT": "ShareGPT multi-turn — `{from: human, value: ...}` / `{from: gpt, value: ...}`",
}


def render() -> None:
    st.subheader("🧪 Playground — Instruction Format Preview")

    st.markdown(
        "Build an instruction example and see it formatted in Alpaca, ChatML, or ShareGPT. "
        "Use the pre-built examples to explore the formats instantly."
    )

    col_preset, col_fmt = st.columns([2, 1])

    with col_preset:
        preset_name = st.selectbox(
            "Load a sample example",
            options=_SAMPLE_NAMES,
            key="finetune_uc4_sample",
        )

    preset_idx = _SAMPLE_NAMES.index(preset_name) - 1  # -1 for "custom" option

    if preset_name != "— custom —" and 0 <= preset_idx < len(SAMPLE_EXAMPLES):
        loaded = SAMPLE_EXAMPLES[preset_idx]
    else:
        loaded = InstructExample(instruction="", input="", output="", system="")

    with col_fmt:
        fmt = st.selectbox(
            "Output format",
            options=["Alpaca", "ChatML", "ShareGPT"],
            help="Select the training dataset format to preview.",
            key=DATASET_FORMAT_KEY,
        )
        st.caption(_FORMAT_DESCRIPTIONS[fmt])

    st.divider()
    st.markdown("#### Your Example")

    col_inputs, col_preview = st.columns([1, 1])

    with col_inputs:
        instruction = st.text_area(
            "Instruction",
            value=loaded.instruction,
            height=80,
            placeholder="e.g. Summarize the following text in one sentence.",
            key="finetune_uc4_instruction",
        )
        input_text = st.text_area(
            "Input (optional — leave blank if instruction is self-contained)",
            value=loaded.input,
            height=80,
            placeholder="e.g. The article text to summarize...",
            key="finetune_uc4_input",
        )
        output_text = st.text_area(
            "Expected output",
            value=loaded.output,
            height=80,
            placeholder="e.g. The article is about...",
            key="finetune_uc4_output",
        )
        system_text = st.text_input(
            "System prompt (ChatML / ShareGPT only)",
            value=loaded.system,
            placeholder="e.g. You are a helpful assistant.",
            key="finetune_uc4_system",
        )

    example = InstructExample(
        instruction=instruction,
        input=input_text,
        output=output_text,
        system=system_text,
    )

    with col_preview:
        st.markdown(f"**Formatted as {fmt}**")

        if not instruction.strip():
            st.caption("Fill in the Instruction field to see the formatted output.")
        else:
            if fmt == "Alpaca":
                result = format_alpaca(example)
                st.code(result["formatted_prompt"], language="text")
                with st.expander("JSON representation"):
                    st.json(result["data"])

            elif fmt == "ChatML":
                result = format_chatml(example)
                st.code(result["formatted_prompt"], language="text")
                with st.expander("Messages list (for API)"):
                    st.json(result["messages"])

            elif fmt == "ShareGPT":
                result = format_sharegpt(example)
                st.json(result["conversations"])

    st.divider()

    if instruction.strip() and output_text.strip():
        col_dl, _ = st.columns([1, 3])
        with col_dl:
            json_str = format_as_json_download(example, fmt)
            st.download_button(
                label=f"Download as {fmt} JSON",
                data=json_str,
                file_name=f"example_{fmt.lower()}.json",
                mime="application/json",
            )

    st.divider()
    st.markdown("#### Dataset size guide")
    st.table({
        "Examples": ["< 100", "100–499", "500–2,000", "2,000–10,000", "10,000+"],
        "Recommendation": [
            "Too few — use few-shot prompting instead",
            "Borderline — fine-tune only if base model + prompting clearly fails",
            "Viable for focused tasks (classification, style, single skill)",
            "Good for multi-skill instruction following",
            "Strong general instruction following; diminishing returns beyond 50k",
        ],
        "Data collection method": [
            "—", "Human annotation", "GPT-4 distillation or human annotation",
            "GPT-4 distillation", "Mix of distillation + open datasets",
        ],
    })

    st.info(
        "**Try it:** Load each preset and switch between formats to see exactly "
        "how the same example looks in Alpaca, ChatML, and ShareGPT."
    )
