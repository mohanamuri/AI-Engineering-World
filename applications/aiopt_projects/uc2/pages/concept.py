"""UC2 — Concept: What is Model Routing and why it reduces costs."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Model Routing")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why using a powerful (expensive) AI for every question is wasteful\n"
        "- How a quick classifier decides which model to use for each query\n"
        "- What SIMPLE vs COMPLEX means for an AI query\n"
        "- How to watch routing decisions happen in real time in the Playground"
    )

    st.markdown(
        "Think of it like a hospital triage system. "
        "Not every patient needs a specialist surgeon — "
        "most can be handled by a general practitioner.\n\n"
        "Similarly, not every AI query needs the most powerful (and expensive) model. "
        "*'What is the capital of France?'* doesn't need the same model as "
        "*'Write a 5-year business strategy for entering the Asian market.'*\n\n"
        "**Model routing** automatically sends each query to the right model — "
        "saving money on simple queries while preserving quality on complex ones."
    )

    st.markdown(
        """
        ### The Cost Problem

        Large LLMs are expensive. A 70B parameter model is 5–10× more costly per token
        than an 8B model. But most production queries don't need a 70B model:

        - *"What is Python?"* → 8B model handles it perfectly
        - *"Analyse these 5 competing architectures and recommend one for a real-time fraud system"* → needs 70B

        **Model routing** uses a cheap classifier call to decide which model to invoke,
        saving 60–80 % of API cost on typical traffic mixes.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Without routing**")
            st.markdown(
                "Every query → 70B model\n\n"
                "- Consistent quality ✅\n"
                "- Maximum cost ❌\n"
                "- Slower for simple tasks ❌\n"
                "- Overkill for 70 % of queries ❌"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**With routing**")
            st.markdown(
                "Classifier → 8B or 70B per query\n\n"
                "- Quality preserved for complex tasks ✅\n"
                "- 60–80 % cost reduction ✅\n"
                "- Faster on simple tasks ✅\n"
                "- Small classifier overhead (~50 ms) ⚠️"
            )

    st.divider()
    st.markdown("### Routing Architecture")

    steps = [
        ("1️⃣ Classifier call (8B, 5 tokens max)",
         "Send the query to the small model with a complexity-classification prompt. "
         "Ask for ONE word: `SIMPLE` or `COMPLEX`. This costs ~50 tokens and ~50 ms."),
        ("2️⃣ Route decision",
         "- `SIMPLE` → `compound-beta-mini` (fast, cheap)\n"
         "- `COMPLEX` → `compound-beta-mini` (slower, high quality)"),
        ("3️⃣ Run the selected model",
         "Send the original query to the chosen model. User gets the answer; "
         "metadata (complexity, model chosen, latencies) is logged for monitoring."),
    ]
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.markdown("### Classifier Prompt Design")
    st.code(
        """You are a query complexity classifier.

Classify the query as SIMPLE or COMPLEX based on these rules:
- SIMPLE: factual lookup, single-step calculation, yes/no question,
  basic definition, short creative task, common knowledge.
- COMPLEX: multi-step reasoning, deep analysis, code generation,
  research synthesis, nuanced judgment, long-form content.

Respond with ONLY one word: SIMPLE or COMPLEX.""",
        language="text",
    )

    st.markdown("### SIMPLE vs COMPLEX — Examples")
    st.table({
        "Query": [
            "What is the capital of France?",
            "Convert 100 USD to EUR",
            "What is recursion?",
            "Debug this Python function and explain each bug",
            "Write a business case for migrating from monolith to microservices",
            "Summarise and compare three competing ML frameworks for production",
        ],
        "Classification": ["SIMPLE", "SIMPLE", "SIMPLE", "COMPLEX", "COMPLEX", "COMPLEX"],
        "Model": ["8B", "8B", "8B", "70B", "70B", "70B"],
    })

    st.success(
        "**Next → Playground:** Type any query and watch the classifier decide in real time "
        "which model should handle it."
    )
