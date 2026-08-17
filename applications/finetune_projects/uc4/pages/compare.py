"""UC4 — Compare: Same example in all 3 formats side by side."""

import streamlit as st

from applications.finetune_projects.services.instruction_tuning import (
    SAMPLE_EXAMPLES,
    InstructExample,
    format_alpaca,
    format_chatml,
    format_sharegpt,
)

_SAMPLE_NAMES = [
    "Text summarization",
    "Sentiment classification",
    "Formal English translation",
    "Write a Python function",
]


def render() -> None:
    st.subheader("⚖️ Compare — All 3 Formats Side by Side")

    st.markdown(
        "The same instruction example formatted in Alpaca, ChatML, and ShareGPT. "
        "See exactly what the model receives during training for each format."
    )

    preset_name = st.selectbox(
        "Select a sample example",
        options=_SAMPLE_NAMES + ["— custom —"],
        key="finetune_uc4_cmp_preset",
    )

    if preset_name != "— custom —":
        idx = _SAMPLE_NAMES.index(preset_name)
        ex = SAMPLE_EXAMPLES[idx]
        instruction = ex.instruction
        input_text = ex.input
        output_text = ex.output
        system_text = ex.system
    else:
        instruction = ""
        input_text = ""
        output_text = ""
        system_text = ""

    with st.expander("Edit example (for custom mode)", expanded=(preset_name == "— custom —")):
        instruction = st.text_area("Instruction", value=instruction, key="finetune_uc4_cmp_instr")
        input_text = st.text_area("Input (optional)", value=input_text, key="finetune_uc4_cmp_input")
        output_text = st.text_area("Output", value=output_text, key="finetune_uc4_cmp_output")
        system_text = st.text_input(
            "System prompt (ChatML / ShareGPT)",
            value=system_text,
            key="finetune_uc4_cmp_system",
        )

    example = InstructExample(
        instruction=instruction,
        input=input_text,
        output=output_text,
        system=system_text,
    )

    if not instruction.strip():
        st.info("Select a preset or fill in the instruction field to see the comparison.")
        return

    st.divider()

    alpaca_result = format_alpaca(example)
    chatml_result = format_chatml(example)
    sharegpt_result = format_sharegpt(example)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Alpaca")
        st.caption("Stanford format — `### Instruction:` / `### Response:`")
        with st.container(border=True):
            st.code(alpaca_result["formatted_prompt"], language="text")
        st.metric(
            "Characters",
            len(alpaca_result["formatted_prompt"]),
            help="Total characters in the formatted prompt (affects tokenization)",
        )
        st.markdown("**Best for:**")
        st.markdown("- Simple single-turn tasks\n- Older model families\n- Human-readable format")

    with col2:
        st.markdown("### ChatML")
        st.caption("OpenAI format — `<|im_start|>` / `<|im_end|>` tokens")
        with st.container(border=True):
            st.code(chatml_result["formatted_prompt"], language="text")
        st.metric(
            "Characters",
            len(chatml_result["formatted_prompt"]),
        )
        st.markdown("**Best for:**")
        st.markdown("- Modern chat models\n- System prompt support\n- Widest ecosystem support")

    with col3:
        st.markdown("### ShareGPT")
        st.caption("Conversation format — `from: human` / `from: gpt`")
        with st.container(border=True):
            st.json(sharegpt_result["conversations"])
        total_chars = sum(len(c["value"]) for c in sharegpt_result["conversations"])
        st.metric("Characters (content only)", total_chars)
        st.markdown("**Best for:**")
        st.markdown("- Multi-turn conversations\n- Datasets scraped from ChatGPT\n- Community fine-tunes")

    st.divider()
    st.markdown("### Key Structural Differences")

    st.table({
        "Feature": [
            "Turn separator", "System prompt", "Multi-turn support",
            "Special tokens", "Template in prompt string",
        ],
        "Alpaca": [
            "### headers", "Not supported", "Not supported",
            "None required", "Yes — human readable",
        ],
        "ChatML": [
            "<|im_start|> / <|im_end|>", "Yes (role: system)", "Yes",
            "im_start, im_end required in tokenizer", "Yes — tokenizer-encoded",
        ],
        "ShareGPT": [
            "JSON keys (from/value)", "Yes (from: system)", "Yes — list of turns",
            "None in raw format (converted at training time)", "No — structure only",
        ],
    })

    st.markdown("### Which format should you choose?")
    with st.container(border=True):
        st.markdown(
            "**Decision guide:**\n\n"
            "1. Check your model's chat template: `tokenizer.chat_template`. "
            "If it mentions `<|im_start|>`, use **ChatML**.\n"
            "2. If your data is multi-turn conversations, use **ShareGPT** "
            "(TRL's SFTTrainer converts it to the model's native format).\n"
            "3. If you're starting fresh with a simple task and want maximum "
            "framework compatibility, use **Alpaca**.\n"
            "4. When in doubt: **ChatML** is the most widely supported format for models released after 2023."
        )
