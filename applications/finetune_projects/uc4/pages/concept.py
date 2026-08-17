"""UC4 — Concept: Instruction Tuning — teaching models to follow instructions."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Instruction Tuning")

    st.info(
        "**What you'll learn in this section**\n\n"
        "- What instruction tuning is and why base models need it\n"
        "- The 3 dataset formats: Alpaca, ChatML, ShareGPT — when to use each\n"
        "- Why data quality matters more than quantity\n"
        "- Data collection methods: annotation, self-instruct, distillation\n"
        "- The quality checklist before you start training"
    )

    st.markdown(
        "A base language model (e.g. LLaMA-2-7b) is trained to predict the next token — "
        "it's a text completion machine. Ask it *'Summarize this article'* and it might "
        "continue the text with more article content instead of a summary. "
        "It's not broken; it just wasn't trained to follow instructions.\n\n"
        "**Instruction tuning** solves this by fine-tuning the model on thousands of "
        "(instruction, response) pairs. After training, the model learns to switch from "
        "'continue the text' mode to 'follow this instruction' mode. "
        "This is how ChatGPT, Claude, and Llama-Chat models are created from their base models."
    )

    st.divider()
    st.markdown("### Why Base Models Need Instruction Tuning")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Base model behavior (without instruction tuning)**")
            st.code(
                'Input: "Summarize: The Amazon rainforest covers..."\n\n'
                'Output: "Summarize: The Amazon rainforest covers an area\n'
                'of approximately 5.5 million km². The forest plays a\n'
                'crucial role in... [continues the text]"',
                language="text",
            )
            st.caption("The model completes the text — it doesn't understand 'Summarize' as a command.")

    with col2:
        with st.container(border=True):
            st.markdown("**After instruction tuning**")
            st.code(
                'Input: "Summarize: The Amazon rainforest covers..."\n\n'
                'Output: "The Amazon rainforest is the world\'s largest\n'
                'tropical forest, covering 5.5M km² and producing\n'
                '20% of global oxygen."',
                language="text",
            )
            st.caption("The model recognizes the instruction format and responds appropriately.")

    st.divider()
    st.markdown("### The 3 Dataset Formats")

    st.markdown(
        "Three formats have emerged as standards. Each has a specific use case "
        "and is supported by different model families and training frameworks."
    )

    formats = [
        {
            "name": "Alpaca (Stanford, 2023)",
            "when": "Simple single-turn instruction following",
            "models": "LLaMA-1, Alpaca, Vicuna (early generations)",
            "structure": "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}",
            "pros": "Simple, human-readable, well-supported by older frameworks",
            "cons": "Single-turn only, no system prompt support, verbose template",
        },
        {
            "name": "ChatML (OpenAI-style)",
            "when": "Chat/conversation models, most modern LLMs",
            "models": "Mistral-Instruct, Qwen, Yi, Phi-3, OpenHermes",
            "structure": "<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>",
            "pros": "System prompt support, clean role separation, multi-turn ready, most widely adopted",
            "cons": "Tokenizer must support `<|im_start|>` and `<|im_end|>` special tokens",
        },
        {
            "name": "ShareGPT (Community format)",
            "when": "Multi-turn conversations, conversation distillation datasets",
            "models": "Vicuna, WizardLM, many community fine-tunes",
            "structure": '{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}',
            "pros": "Supports multi-turn naturally, widely used for datasets scraped from ChatGPT",
            "cons": "Requires conversion to the model's native chat template at training time",
        },
    ]

    for f in formats:
        with st.container(border=True):
            col_name, col_details = st.columns([1, 3])
            with col_name:
                st.markdown(f"**{f['name']}**")
                st.caption(f"Use when: {f['when']}")
            with col_details:
                st.markdown(f"*Models:* {f['models']}")
                st.code(f['structure'], language="text")
                st.caption(f"Pros: {f['pros']}")
                st.caption(f"Cons: {f['cons']}")

    st.divider()
    st.markdown("### Data Quality > Data Quantity")

    st.markdown(
        "The LIMA paper (Zhou et al., 2023) showed that **1,000 carefully curated examples** "
        "fine-tuned from LLaMA-65B matched the quality of models trained on 52,000 examples. "
        "The key finding: data quality and diversity matter far more than volume.\n\n"
        "**What makes a high-quality instruction tuning example?**"
    )

    quality_criteria = [
        ("Clear instruction", "The instruction unambiguously specifies what the model should do. Bad: 'Write something about dogs.' Good: 'Write a 3-sentence description of Border Collies for a children's encyclopedia.'"),
        ("Correct output", "The response is factually accurate, well-formatted, and demonstrates the desired behavior."),
        ("Appropriate difficulty", "Mix of easy, medium, and hard tasks. Too many simple tasks → model doesn't generalize to complex queries."),
        ("Format consistency", "All examples use the same template throughout. Inconsistent formatting confuses the model."),
        ("Output length variety", "Mix of short responses (1 sentence) and long ones (paragraphs). Prevents the model from always generating the same length."),
        ("Instruction diversity", "At least 50% unique instruction patterns. 'Summarize this' appearing 1000 times → overfitting to that phrasing."),
    ]

    for criterion, explanation in quality_criteria:
        with st.container(border=True):
            st.markdown(f"**{criterion}**")
            st.write(explanation)

    st.divider()
    st.markdown("### Data Collection Methods")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("**Human Annotation**")
            st.markdown(
                "Hire annotators to write instructions and responses.\n\n"
                "Cost: $0.10–$1.00 per example\n"
                "Quality: Highest\n"
                "Scale: Limited by budget\n\n"
                "Best for: High-stakes tasks (medical, legal), brand voice consistency"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**Self-Instruct / Distillation**")
            st.markdown(
                "Use GPT-4 or Claude to generate (instruction, response) pairs from seed examples.\n\n"
                "Cost: $0.01–$0.05 per example\n"
                "Quality: Good (GPT-4 quality)\n"
                "Scale: Tens of thousands easily\n\n"
                "Best for: Most use cases, fast dataset creation"
            )
    with col3:
        with st.container(border=True):
            st.markdown("**Open Datasets**")
            st.markdown(
                "Public instruction datasets: Alpaca-52k, Dolly-15k, OpenHermes, FLAN.\n\n"
                "Cost: Free\n"
                "Quality: Varies (filter carefully)\n"
                "Scale: Unlimited\n\n"
                "Best for: General instruction following, bootstrapping"
            )

    st.divider()
    st.markdown("### Dataset Quality Checklist")
    st.markdown("Apply this checklist before starting any instruction tuning run:")

    from applications.finetune_projects.services.instruction_tuning import get_dataset_quality_checklist
    checklist = get_dataset_quality_checklist()
    st.table({
        "Criterion": [c["criterion"] for c in checklist],
        "Target": [c["target"] for c in checklist],
        "Why it matters": [c["why"] for c in checklist],
    })

    st.success(
        "**Next → Playground:** Enter your own instruction, input, and output. "
        "Select a format and see the live preview of how your example would be formatted for training."
    )
