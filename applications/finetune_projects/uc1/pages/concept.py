"""UC1 — Concept: Fine-tune vs RAG decision framework."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Fine-tune vs RAG")

    st.info(
        "**What you'll learn in this section**\n\n"
        "- The 3 key questions that determine whether to fine-tune or use RAG\n"
        "- Concrete scenarios where each approach wins\n"
        "- When to combine both in one system\n"
        "- Common mistakes engineers make when choosing between them"
    )

    st.markdown(
        "Two engineers are building an AI assistant for their company. "
        "Engineer A fine-tunes a model. Engineer B builds a RAG pipeline. "
        "Three months later, Engineer A's model is outdated and expensive to retrain. "
        "Engineer B's assistant can't match the brand voice the marketing team requires.\n\n"
        "**Both engineers chose without a framework.** "
        "This section gives you that framework — a set of questions that map your constraints "
        "to the right architectural decision before you write a single line of training code."
    )

    st.divider()
    st.markdown("### The 3 Key Questions")

    questions = [
        (
            "1️⃣ Does the knowledge change frequently?",
            "If your data is updated weekly, monthly, or by a live API — **RAG wins**. "
            "Fine-tuning bakes knowledge into weights at a fixed point in time. "
            "Keeping a fine-tuned model up to date requires constant retraining cycles "
            "(each one costs GPU hours and engineering time). "
            "RAG just requires re-indexing documents.",
            "Knowledge is stable (legal rules, style guides, domain vocab) → Fine-tuning viable\n"
            "Knowledge changes frequently (product catalog, news, prices) → RAG",
        ),
        (
            "2️⃣ Do you have 500+ labeled task-specific examples?",
            "Fine-tuning is supervised learning — it needs examples of input → desired output. "
            "Below ~100 examples, fine-tuning typically overfits and underperforms a well-prompted base model. "
            "The sweet spot is **500+ examples** for reliable fine-tuning results, "
            "with 10k+ for high-quality domain adaptation.",
            "< 100 examples → RAG or prompt engineering\n"
            "100–499 examples → borderline; consider few-shot prompting first\n"
            "500+ examples → fine-tuning becomes viable",
        ),
        (
            "3️⃣ Is latency critical (sub-200 ms)?",
            "RAG adds a retrieval step — vector search, document fetching, context assembly. "
            "This typically adds 50–300 ms on top of LLM inference time. "
            "For real-time applications (autocomplete, interactive UI, voice), "
            "a fine-tuned model's single forward pass wins on latency.",
            "Latency-critical + stable knowledge → Fine-tuning\n"
            "Latency flexible or knowledge changes → RAG",
        ),
    ]

    for title, explanation, rule in questions:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(explanation)
            st.caption(f"Decision rule: {rule}")

    st.divider()
    st.markdown("### When Fine-tuning Wins")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**✅ Best for Fine-tuning**")
            st.markdown(
                "- **Style transfer** — teach the model a brand voice, tone, or writing style\n"
                "- **Classification** — sentiment, intent, category labels with 500+ examples\n"
                "- **Domain-specific format** — structured outputs (JSON, XML) with custom schemas\n"
                "- **Latency-critical** — single GPU forward pass, no retrieval overhead\n"
                "- **Proprietary patterns** — confidential logic that shouldn't go in prompts\n"
                "- **Offline / air-gapped** — no external API calls permitted"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**✅ Best for RAG**")
            st.markdown(
                "- **Factual Q&A** — ask questions over a document corpus\n"
                "- **Knowledge changes** — product docs, policies, news, prices\n"
                "- **No labeled data** — you have documents but no (input, output) pairs\n"
                "- **Source citations** — users need to see where the answer came from\n"
                "- **No GPU budget** — RAG uses the base model without training\n"
                "- **Fast iteration** — update knowledge by re-indexing, not retraining"
            )

    st.divider()
    st.markdown("### When to Use BOTH")
    with st.container(border=True):
        st.markdown("**Brand voice + live knowledge = Fine-tune + RAG**")
        st.markdown(
            "Some systems need both consistent style AND up-to-date knowledge. "
            "A customer support bot that must speak in the company's tone "
            "AND answer questions from a live product documentation site "
            "benefits from combining both:\n\n"
            "1. **Fine-tune** the model on brand voice examples → consistent tone\n"
            "2. **RAG** the fine-tuned model on live docs → fresh, accurate answers\n\n"
            "Examples: customer support bots, enterprise assistants, medical chatbots.\n\n"
            "**Cost warning:** this is the most complex and expensive option. "
            "Start with RAG only, validate it, then add fine-tuning if brand voice is a real issue."
        )

    st.divider()
    st.markdown("### Decision Tree Overview")

    st.markdown(
        """
        ```
        Does knowledge change frequently?
        ├── YES → RAG (High confidence)
        └── NO
            ├── Task = factual_qa AND data not proprietary?
            │   ├── YES → RAG (High confidence)
            │   └── NO
            │       ├── Task in (style, classification) AND examples ≥ 500?
            │       │   ├── YES → Fine-tune (High confidence)
            │       │   └── NO
            │       │       ├── Latency critical?
            │       │       │   ├── YES → Fine-tune (Medium confidence)
            │       │       │   └── NO
            │       │       │       ├── Proprietary data AND examples ≥ 100?
            │       │       │       │   ├── YES → Both (Medium confidence)
            │       │       │       │   └── NO
            │       │       │       │       ├── examples < 100?
            │       │       │       │       │   ├── YES → RAG (Medium confidence)
            │       │       │       │       │   └── NO → RAG (Low — collect more data)
        ```
        """
    )

    st.divider()
    st.markdown("### Common Mistakes")

    st.table({
        "Mistake": [
            "Fine-tuning when data changes weekly",
            "Fine-tuning with < 100 examples",
            "Using RAG when latency is sub-200ms",
            "Skipping RAG to avoid infrastructure",
            "Building Both without validating RAG first",
        ],
        "Why it fails": [
            "Model knowledge becomes stale immediately",
            "Overfitting — model memorises examples, doesn't generalise",
            "Retrieval step adds 100–300ms, breaking latency SLA",
            "Fine-tuning knowledge requires retraining every time docs update",
            "Doubles complexity; RAG often achieves 80% of the quality at 20% of the cost",
        ],
        "Fix": [
            "Use RAG — re-index when docs change",
            "Collect more data or use few-shot prompting instead",
            "Fine-tune for latency-critical tasks with stable knowledge",
            "Set up a simple vector DB (ChromaDB) — it's 50 lines of code",
            "Start with RAG → measure quality → add fine-tuning only if needed",
        ],
    })

    st.success(
        "**Next → Playground:** Enter your scenario constraints and get a "
        "personalized recommendation from the decision engine."
    )
