"""UC1 — Insights: Interview Q&A and connected concepts for Fine-tune vs RAG."""

import streamlit as st


def render() -> None:
    st.subheader("💡 Insights — Fine-tune vs RAG")

    st.markdown("#### When to use each approach — quick reference")
    st.table({
        "Scenario": [
            "Customer FAQ chatbot",
            "Legal document classifier (500+ examples)",
            "Medical Q&A assistant (live guidelines)",
            "Brand voice / tone rewriter",
            "Real-time product catalog assistant",
            "Code completion for internal DSL",
        ],
        "Approach": ["RAG", "Fine-tune", "RAG", "Fine-tune", "RAG", "Fine-tune"],
        "Key reason": [
            "Questions overlap, answers are stable",
            "Classification with labeled data is fine-tuning's sweet spot",
            "Medical guidelines update — RAG keeps answers current",
            "Style is a training signal, not a retrieval problem",
            "Catalog changes daily — RAG re-indexes, fine-tuning can't keep up",
            "Private DSL semantics can't be in a public base model",
        ],
    })

    st.divider()

    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions asked in ML Engineering and LLM application interviews.")

    qa_pairs = [
        (
            "When should you fine-tune a model instead of using RAG?",
            "Fine-tuning is the right choice when: (1) you have 500+ labeled examples of the task, "
            "(2) the knowledge is stable (won't require frequent updates), "
            "(3) you need consistent output style or format that can't be reliably achieved with prompting, "
            "or (4) latency is critical (< 200 ms) and you can't afford the retrieval overhead. "
            "Classic fine-tuning wins: text classification, style transfer, domain-specific output formats. "
            "Classic RAG wins: factual Q&A over a document corpus, anything with frequently changing knowledge."
        ),
        (
            "How much training data do you need for fine-tuning?",
            "The rule of thumb: "
            "- < 100 examples: fine-tuning typically overfits and underperforms a well-prompted base model. "
            "Use few-shot prompting instead. "
            "- 100–499 examples: borderline. Test both approaches; few-shot + RAG often beats fine-tuning here. "
            "- 500–5000 examples: reliable fine-tuning for classification and style tasks. "
            "- 5000–50k examples: strong domain adaptation. "
            "- 50k+ examples: significant capability changes, similar to full pre-training data volumes. "
            "Quality matters more than quantity — 500 well-curated examples > 10k noisy ones."
        ),
        (
            "Why is RAG often the preferred default over fine-tuning?",
            "RAG has lower risk and faster iteration: "
            "(1) No GPU required — add documents, re-index, done. "
            "(2) Knowledge is always up-to-date — no retraining cycle needed. "
            "(3) Sources are traceable — users can verify where answers come from. "
            "(4) Easier to debug — you can see which documents were retrieved. "
            "Fine-tuning is a higher-commitment bet: it costs GPU time, requires quality labeled data, "
            "and becomes technical debt when requirements change. "
            "Start with RAG, measure quality, and only add fine-tuning when RAG's limitations are clear."
        ),
        (
            "Can you combine fine-tuning and RAG in the same system?",
            "Yes — this is called 'fine-tune + RAG' or 'RAG with a specialized model'. "
            "The pattern: fine-tune the model to adopt a specific style or format, "
            "then use RAG to inject up-to-date knowledge at inference time. "
            "Example: fine-tune on 1000 examples of your brand's support voice (consistent tone), "
            "then RAG over live product docs (fresh knowledge). "
            "When to use it: customer support bots, enterprise assistants, medical chatbots. "
            "Warning: this is the most complex and expensive option. "
            "Validate RAG alone first; add fine-tuning only if style or format is a measurable problem."
        ),
        (
            "How do you calculate the ROI of fine-tuning vs RAG?",
            "ROI comparison framework:\n\n"
            "Fine-tuning costs: GPU time (e.g. A100 at $3/hr × 10 hours = $30/run) "
            "+ engineer time to curate data + retraining cost when requirements change. "
            "Fine-tuning savings: faster inference (no retrieval), potentially smaller model "
            "(specialized model can be smaller than a general model with complex RAG prompts).\n\n"
            "RAG costs: vector DB hosting ($50–200/mo for managed), embedding API calls, "
            "retrieval latency (~50–200ms overhead). "
            "RAG savings: no training cost, always-fresh knowledge, no retraining cycles.\n\n"
            "Rule: if the domain knowledge changes more than once per month, "
            "RAG's operational cost is almost always lower than fine-tuning's retraining cost."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        (
            "Retrieval-Augmented Generation (RAG)",
            "A pattern where relevant documents are retrieved from a vector store at inference time "
            "and injected into the model's context. The model then generates an answer grounded in "
            "the retrieved documents. Key components: embedding model, vector store, retrieval, "
            "context assembly, generation.",
        ),
        (
            "Parameter-Efficient Fine-Tuning (PEFT)",
            "An umbrella term for methods that fine-tune only a small subset of model parameters "
            "rather than all weights. LoRA, Prefix Tuning, and Adapters are all PEFT methods. "
            "Reduces GPU memory requirements by 90%+ while achieving comparable quality to full fine-tuning.",
        ),
        (
            "Catastrophic Forgetting",
            "When a neural network trained on a new task 'forgets' how to do previously learned tasks. "
            "Fine-tuning on domain-specific data can cause the model to lose general capabilities. "
            "Mitigations: low learning rate, LoRA (frozen base weights), mixed training data.",
        ),
        (
            "Few-Shot Prompting",
            "Providing 3–10 examples directly in the prompt. Often outperforms fine-tuning when "
            "data is scarce (< 100 examples). When the model is large enough and examples are "
            "well-chosen, few-shot prompting can match fine-tuning quality without any training.",
        ),
        (
            "Vector Store / Embedding Index",
            "A database optimized for nearest-neighbour search over high-dimensional vectors. "
            "ChromaDB (in-memory, free), Pinecone (managed), Weaviate (open source), "
            "pgvector (Postgres extension). Core infrastructure for any RAG system.",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC2 → LoRA Architecture:** Now that you know when to fine-tune, "
        "learn how LoRA makes it feasible without expensive GPU hardware."
    )
