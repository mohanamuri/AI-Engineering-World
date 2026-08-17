"""UC4 — Insights: Eval-driven development, CI/CD integration, interview Q&A."""

import streamlit as st

from applications.llm_evaluation.uc4.constants import PIPELINE_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Eval Pipeline")

    result = st.session_state.get(PIPELINE_RESULT_KEY)

    if result:
        st.markdown("#### Your last pipeline run")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Test cases", len(result.cases))
        c2.metric("Avg Faithfulness", f"{result.avg_faithfulness:.2f}")
        c3.metric("Avg Relevance", f"{result.avg_relevance:.2f}")
        c4.metric("Avg Recall", f"{result.avg_recall:.2f}")
        c5.metric("Avg Precision", f"{result.avg_precision:.2f}")
        c6.metric("Avg Hall. Rate", f"{result.avg_hallucination_rate:.0%}")
        st.divider()

    st.markdown("#### When to run the Eval Pipeline")
    st.table({
        "Trigger": [
            "New model version deployed",
            "Prompt template changed",
            "Embedding model updated",
            "Document corpus refreshed",
            "Weekly health check",
        ],
        "Run pipeline?": ["✅ Always", "✅ Always", "✅ Always", "✅ Yes", "✅ Yes (sample)"],
        "Why": [
            "Model updates can silently change response quality",
            "Even minor prompt changes can shift faithfulness",
            "New embeddings may retrieve different documents",
            "New documents may introduce context drift",
            "Gradual degradation is not caught by event-based triggers",
        ],
    })

    st.divider()
    st.markdown("#### Production Checklist")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Do**")
            st.markdown(
                "- Version your eval dataset alongside your code (commit it to the repo)\n"
                "- Set numeric thresholds: faithfulness > 0.75, hallucination rate < 0.25\n"
                "- Store eval results with timestamps to track trends over time\n"
                "- Use the eval pipeline as a deploy gate in CI/CD\n"
                "- Grow the dataset: add any production failure as a new test case"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Don't**")
            st.markdown(
                "- Use a static dataset forever — it goes stale as user queries evolve\n"
                "- Run eval only when there's a problem — it should be proactive\n"
                "- Ignore individual failing cases — they reveal systemic weaknesses\n"
                "- Use identical test and training data — this masks real performance\n"
                "- Skip context recall — low recall means the retriever is silently broken"
            )

    st.divider()
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Questions on systematic LLM evaluation in ML Engineering interviews.")

    qa_pairs = [
        (
            "What should be in a good LLM evaluation dataset?",
            "A good eval dataset is representative, diverse, and labelled with ground truth. "
            "Representative means it reflects the real distribution of production queries — "
            "if 60 % of real questions are 'how do I' questions, 60 % of your test cases should be too. "
            "Diverse means it covers different difficulty levels (easy, medium, hard), different "
            "question types (factual, reasoning, multi-hop), and includes adversarial examples "
            "(questions the system is likely to fail). "
            "Labelled means every test case has a ground truth answer capturing the key facts "
            "the response must include. Size: 20–50 cases is a starting minimum; "
            "100+ is production-grade.",
        ),
        (
            "How often should you run evaluation in production?",
            "There are two evaluation cadences: event-based and time-based. "
            "Event-based evaluation runs on every significant change: model update, prompt change, "
            "embedding update, or corpus refresh — triggered automatically in CI/CD. "
            "Time-based evaluation runs on a schedule regardless of changes: weekly or monthly "
            "on a sample of production traffic to detect gradual degradation. "
            "Gradual drift — where no single change causes a problem but quality slowly declines "
            "over months — is only caught by time-based evaluation. Both cadences are necessary "
            "in production.",
        ),
        (
            "What is eval-driven development and how does it work in practice?",
            "Eval-driven development (EDD) applies test-driven development (TDD) principles to "
            "LLM systems: write your evaluation dataset before making changes, not after. "
            "Workflow: (1) identify a quality problem (e.g. faithfulness < 0.70 on medical queries); "
            "(2) add specific failing examples to the eval dataset; (3) make changes to the "
            "system (prompt, retrieval, model); (4) run the pipeline and verify the failing cases "
            "now pass without regressing others; (5) merge only if all thresholds are met. "
            "This prevents the common pattern of fixing a visible problem while introducing "
            "invisible regressions elsewhere.",
        ),
        (
            "How would you integrate the eval pipeline into a CI/CD system?",
            "The eval pipeline becomes a CI/CD job with these steps: "
            "(1) store the test dataset as JSON in the repository, versioned with the code; "
            "(2) on pull request, trigger the eval job automatically; "
            "(3) run the pipeline against the new code/prompt version; "
            "(4) a threshold-checking script reads the results JSON and exits with code 1 if "
            "any metric fails (faithfulness < 0.75, hallucination_rate > 0.25, etc.); "
            "(5) GitHub Actions / GitLab CI marks the PR as failed, blocking merge; "
            "(6) store eval result artefacts per commit for trend dashboards. "
            "The key insight: eval gates must have numeric thresholds, not just visual dashboards, "
            "otherwise the gate is not automated.",
        ),
        (
            "How do you estimate the cost of running evals at scale?",
            "Each test case requires: RAGAS = 4 LLM calls (one per metric). "
            "Hallucination detection = 1 call (claim extraction) + N calls (one per claim, ~4–8 claims). "
            "So per test case: ~4 + ~6 = ~10 LLM calls. "
            "For 100 test cases: ~1,000 LLM calls per eval run. "
            "At Groq free tier (effectively free for development): no cost barrier. "
            "At OpenAI GPT-4o mini rates (~$0.15/1M input tokens): 100 test cases × ~800 tokens/call "
            "× 10 calls = ~$0.12 per eval run. Running weekly for a year = ~$6. "
            "Cost optimisation: use a smaller judge model for batch eval (only run the best model "
            "for close-call cases), and cache repeated calls with identical inputs.",
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        (
            "DeepEval (open source)",
            "DeepEval is an open-source Python library that implements eval pipelines with "
            "RAGAS-style metrics, hallucination detection, and CI/CD integration out of the box. "
            "It is a good choice for production teams. Our Streamlit implementation teaches "
            "the underlying logic you need to understand to use tools like DeepEval effectively.",
        ),
        (
            "BenchmarkBench / HELM",
            "Academic benchmark frameworks that evaluate LLMs on standardised tasks. "
            "HELM (Holistic Evaluation of Language Models, Stanford) covers 42 scenarios and "
            "7 metric categories. These differ from your eval pipeline in that they evaluate "
            "general capability; your pipeline evaluates your specific RAG application's performance.",
        ),
        (
            "The Evals Framework (OpenAI)",
            "OpenAI's open-source Evals framework (github.com/openai/evals) allows defining "
            "custom evaluations as code. It uses a similar test-case JSON format to what we "
            "implemented here. The principles are identical — the framework handles the plumbing.",
        ),
        (
            "Continuous Evaluation vs Continuous Training",
            "MLOps frameworks distinguish between continuous training (retraining the model on "
            "new data) and continuous evaluation (running evals on the same model against new "
            "queries). For LLM applications using API-hosted models, continuous evaluation is "
            "more relevant than training — you control the prompts and retrieval, not the weights.",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "You have now completed all 4 LLM Evaluation use cases. "
        "The complete evaluation stack: RAGAS (retrieval quality) + LLM Judge (response quality) "
        "+ Hallucination Detection (factual safety) + Eval Pipeline (systematic monitoring) "
        "gives you full coverage of what matters in production LLM applications."
    )
