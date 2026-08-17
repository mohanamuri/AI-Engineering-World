"""UC1 — Insights: When to use RAGAS, production checklist, interview Q&A."""

import streamlit as st

from applications.llm_evaluation.uc1.constants import RAGAS_HISTORY_KEY, RAGAS_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — RAGAS Evaluation")

    history = st.session_state.get(RAGAS_HISTORY_KEY, [])
    result = st.session_state.get(RAGAS_RESULT_KEY)

    if history:
        st.markdown("#### Your session stats")
        avg_faith = sum(r.faithfulness for r in history) / len(history)
        avg_rel = sum(r.answer_relevance for r in history) / len(history)
        avg_overall = sum(r.overall_score for r in history) / len(history)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Evaluations run", len(history))
        c2.metric("Avg Faithfulness", f"{avg_faith:.2f}")
        c3.metric("Avg Relevance", f"{avg_rel:.2f}")
        c4.metric("Avg Overall", f"{avg_overall:.2f}")
        st.divider()

    st.markdown("#### When to use RAGAS Evaluation")
    st.table({
        "Scenario": [
            "RAG chatbot for customer support",
            "Document Q&A over internal policies",
            "Medical / legal information retrieval",
            "Creative writing assistant",
            "General-purpose chat (no retrieval)",
        ],
        "Use RAGAS?": ["✅ Yes", "✅ Yes", "✅ Critical", "❌ No", "❌ No"],
        "Why": [
            "Faithfulness critical — wrong answers damage trust",
            "Context recall measures if all policy facts are retrieved",
            "Hallucination detection is mandatory in regulated domains",
            "No ground truth answers; output is subjective",
            "No retrieval component to evaluate",
        ],
    })

    st.divider()
    st.markdown("#### Production Checklist")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Do**")
            st.markdown(
                "- Run RAGAS on a held-out test dataset before every production deploy\n"
                "- Set alert thresholds: faithfulness < 0.75 = block deploy\n"
                "- Track all 4 metrics over time to detect regressions\n"
                "- Include diverse questions: simple, complex, edge cases\n"
                "- Use domain-specific ground truth answers, not generic ones"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Don't**")
            st.markdown(
                "- Evaluate only on cherry-picked 'good' examples\n"
                "- Use RAGAS as the sole measure — add human eval for 5 % spot checks\n"
                "- Ignore context metrics — low recall/precision means retriever is broken\n"
                "- Run evaluation on every request in production (too expensive)\n"
                "- Conflate faithfulness with correctness — a faithful answer can still be wrong if context is wrong"
            )

    st.divider()
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions in ML Engineering and LLM application interviews about RAG evaluation.")

    qa_pairs = [
        (
            "What does RAGAS measure and why can't you just use accuracy?",
            "RAGAS measures 4 dimensions of RAG quality: faithfulness (LLM grounded in context), "
            "answer relevance (response on-topic), context recall (retriever found the right docs), "
            "and context precision (retrieved docs are relevant). Traditional accuracy metrics require "
            "exact-match answers, which fails for open-ended generation. RAGAS uses LLM-based scoring "
            "to handle natural language variation. It also separates retriever quality (recall/precision) "
            "from generator quality (faithfulness/relevance), letting you diagnose *which* component "
            "is failing — something accuracy alone cannot do."
        ),
        (
            "What is the difference between faithfulness and hallucination detection?",
            "Faithfulness is a soft 0–1 score measuring how well-grounded the overall response is. "
            "Hallucination detection (UC3) is harder and more granular — it extracts individual factual "
            "claims from the response and verifies each one against the source, producing a binary "
            "SUPPORTED / CONTRADICTED / UNVERIFIABLE verdict per claim. "
            "Faithfulness is faster and cheaper; hallucination detection is more precise. "
            "In production, you might use faithfulness as a fast first pass and hallucination "
            "detection only when faithfulness drops below a threshold, to save costs."
        ),
        (
            "How do you improve a RAG system with low context recall?",
            "Low context recall means the retriever is not finding the documents that contain the "
            "answer. Fixes to try in order: (1) increase the number of documents retrieved (k) — "
            "a larger k gives more coverage but increases noise; (2) improve chunking strategy — "
            "chunks that are too large dilute the semantic signal; (3) improve the embedding model — "
            "a better model produces more accurate semantic representations; (4) add metadata "
            "filtering — if you know the answer is in a specific category, pre-filter the vector "
            "search; (5) use hybrid search (BM25 + vector) for queries that rely on keyword matching."
        ),
        (
            "How do you balance context precision vs context recall in a RAG system?",
            "Precision and recall are in tension: retrieving more documents (high k) increases recall "
            "but reduces precision. The right balance depends on your use case. For high-stakes "
            "applications (medical, legal), prioritise recall — it is better to include too much "
            "context than to miss a critical fact. For chatbots with token budget constraints, "
            "prioritise precision — too much noisy context confuses the LLM and increases cost. "
            "A re-ranking step (cross-encoder or LLM-based re-ranker) is the best of both worlds: "
            "retrieve broadly for high recall, then re-rank for high precision."
        ),
        (
            "How would you monitor RAGAS metrics in production?",
            "You cannot run RAGAS on every production request — it costs 4 LLM calls per evaluation. "
            "Instead: (1) sample 1–5 % of production traffic daily and run RAGAS on the sample; "
            "(2) run full RAGAS evaluation on every new model or retriever deploy via CI/CD; "
            "(3) set up alerting: if sampled faithfulness drops below 0.70 for 3 consecutive days, "
            "trigger a review; (4) build a trend dashboard so you can spot gradual degradation — "
            "this is common when the underlying document corpus is updated but embeddings are not "
            "refreshed. Additionally, track user feedback (thumbs up/down) as a free proxy signal."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        (
            "RAGAS (the library)",
            "The original RAGAS library (pip install ragas) uses OpenAI or HuggingFace models. "
            "Our implementation replicates the metric definitions using Groq-hosted LLMs — "
            "the scoring logic is the same, just delivered via a different API, making it "
            "free-tier friendly.",
        ),
        (
            "LangSmith / Weights & Biases / Arize",
            "Production MLOps platforms that can automate eval tracking. LangSmith captures "
            "LangChain traces and lets you define custom evaluators. W&B Prompts and Arize "
            "offer similar dashboards. Our Streamlit implementation teaches the underlying logic "
            "before you adopt a platform.",
        ),
        (
            "Retrieval Metrics (MRR, NDCG, Hit Rate)",
            "These information retrieval metrics measure whether the correct document is "
            "ranked highly. They require knowing which document contains the answer (a 'gold label'). "
            "Context recall in RAGAS approximates this without requiring document-level gold labels.",
        ),
        (
            "Human Evaluation as Ground Truth",
            "RAGAS scores correlate well with human judgements but are not perfect. For "
            "high-stakes applications, complement RAGAS with periodic human reviews — "
            "especially for faithfulness, where subtle nuance can fool LLM judges.",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC2 → LLM-as-Judge:** RAGAS evaluates RAG-specific quality. "
        "LLM-as-Judge lets you score any LLM output on custom criteria — "
        "useful even when there is no retrieval component."
    )
