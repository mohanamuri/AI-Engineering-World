"""Shared Tier Guide page — shown in every LLM Evaluation UC."""

import streamlit as st


def render() -> None:
    st.subheader("📋 LLM Evaluation — Series Guide")

    st.markdown(
        """
        This project covers **4 production evaluation patterns** that every LLM engineer should know.
        Each use case answers a critical question: *"How do I know if my AI system is actually working?"*
        """
    )

    st.divider()
    st.markdown("### The 4 Evaluation Patterns at a Glance")
    st.markdown("*Each row answers one of the most-asked LLM quality assurance interview questions.*")

    rows = [
        {
            "uc": "UC1",
            "technique": "RAGAS Evaluation",
            "concern": "RAG Quality",
            "icon": "📊",
            "interview_q": "How do you measure whether a RAG system is giving good answers?",
            "one_line": "Score faithfulness, answer relevance, context recall, and context precision — all via LLM prompts.",
        },
        {
            "uc": "UC2",
            "technique": "LLM-as-Judge",
            "concern": "Output Quality",
            "icon": "⚖️",
            "interview_q": "How do you evaluate LLM outputs without expensive human labellers?",
            "one_line": "Use a second LLM as an objective judge — score responses 1–10 on custom criteria with reasoning.",
        },
        {
            "uc": "UC3",
            "technique": "Hallucination Detection",
            "concern": "Factual Accuracy",
            "icon": "🔍",
            "interview_q": "How do you detect when an LLM is making up facts?",
            "one_line": "Extract individual claims, verify each against source context, compute a hallucination rate.",
        },
        {
            "uc": "UC4",
            "technique": "Eval Pipeline",
            "concern": "Scale + Automation",
            "icon": "🔄",
            "interview_q": "How do you run systematic evaluation across a whole test dataset?",
            "one_line": "Build a test suite → run all metrics automatically → get a dashboard of pass/fail indicators.",
        },
    ]

    for r in rows:
        with st.container(border=True):
            col_badge, col_content = st.columns([1, 5])
            with col_badge:
                st.markdown(f"### {r['icon']}")
                st.markdown(f"**{r['uc']}**")
            with col_content:
                st.markdown(f"#### {r['technique']}")
                st.markdown(f"*Concern: {r['concern']}*")
                st.markdown(f"**{r['one_line']}**")
                st.caption(f"Interview question this answers: \"{r['interview_q']}\"")

    st.divider()
    st.markdown("### What Each UC Teaches — In Plain English")

    with st.expander("UC1 — RAGAS Evaluation", expanded=False):
        st.markdown(
            """
            **The problem:** You built a RAG app. Users ask questions, the system retrieves documents,
            and the LLM generates answers. But how do you know if the answers are *good*?
            Manual review doesn't scale. You need automated metrics.

            **The solution:** RAGAS (Retrieval-Augmented Generation Assessment) defines 4 metrics:
            - **Faithfulness** — did the LLM stay grounded in the retrieved context, or make up facts?
            - **Answer Relevance** — did it actually answer the question asked?
            - **Context Recall** — did the retriever find documents that contain the right information?
            - **Context Precision** — were the retrieved documents relevant, or mostly noise?

            **You will learn:**
            - How each RAGAS metric is defined and computed
            - Why faithfulness is the most important metric in production RAG
            - How to score all 4 metrics using just an LLM (no paid RAGAS library needed)
            - What scores indicate a healthy RAG system (faithfulness > 0.8 is a common target)
            """
        )

    with st.expander("UC2 — LLM-as-Judge", expanded=False):
        st.markdown(
            """
            **The problem:** Human evaluation of LLM outputs is expensive, slow, and doesn't scale.
            You can't hire annotators to score every response in production.

            **The solution:** Use a second, trusted LLM as your judge. Define criteria (accuracy,
            clarity, completeness, etc.) with explicit rubrics, then ask the judge LLM to score
            each response on a 1–10 scale with reasoning.

            **You will learn:**
            - How to write effective evaluation rubrics for an LLM judge
            - How to compare two responses pairwise (which answer is better?)
            - Why LLM judges are biased toward longer responses and how to counteract this
            - Position bias: always evaluate A vs B and B vs A to eliminate order effects
            - When LLM-as-judge is reliable (structured criteria) vs unreliable (subjective taste)
            """
        )

    with st.expander("UC3 — Hallucination Detection", expanded=False):
        st.markdown(
            """
            **The problem:** LLMs confidently state false information. In healthcare, legal, or
            finance applications, a hallucinated fact can cause real harm. You need to detect it
            before it reaches users.

            **The solution:** A two-step pipeline — (1) extract individual factual claims from the
            LLM response, then (2) verify each claim against the source context. Claims that are
            not supported by the source are flagged as potential hallucinations.

            **You will learn:**
            - The difference between NLI-based and LLM-based hallucination detection
            - How to extract verifiable claims from free-form text
            - How to compute a per-response hallucination rate
            - The "SUPPORTED / CONTRADICTED / UNVERIFIABLE" classification scheme
            - When hallucination detection is necessary (customer-facing apps, regulated domains)
            """
        )

    with st.expander("UC4 — Eval Pipeline", expanded=False):
        st.markdown(
            """
            **The problem:** Testing one response at a time tells you nothing about your system's
            average quality. You need to evaluate across a *representative test dataset* — dozens
            or hundreds of question/answer pairs — and track metrics over time.

            **The solution:** Build an eval pipeline that takes a test dataset (question, answer,
            contexts, ground truth), runs all metrics automatically, and produces a dashboard.
            Integrate it into CI/CD to catch regressions before they reach production.

            **You will learn:**
            - How to design a good eval dataset (diverse, representative, ground-truth labelled)
            - How to run RAGAS + hallucination detection across a full test suite
            - How to build a metrics dashboard with pass/fail thresholds
            - Eval-driven development: write tests first, then improve the RAG system
            - Cost estimation: how many LLM calls does evaluation require?
            """
        )

    st.divider()
    st.markdown("### Production Evaluation Checklist")
    st.markdown(
        """
        In a real production RAG system, you layer all four evaluation approaches:

        ```
        New RAG system version deployed
            ↓
        [UC4] Run eval pipeline on test dataset (automated, every deploy)
            ↓
        [UC1] RAGAS scores — faithfulness > 0.80? context precision > 0.70?
            ↓
        [UC3] Hallucination rate < 20%? Flag high-risk responses for human review.
            ↓
        [UC2] LLM judge comparison — new version better than previous? A/B test.
            ↓
        Promote to production or roll back
        ```

        Together, this evaluation stack catches:
        - **Retrieval regressions** (context recall drops → retriever broken)
        - **Generation regressions** (faithfulness drops → LLM ignoring context)
        - **New hallucination patterns** (model update introduced fabrications)
        - **Quality regressions vs previous version** (judge prefers old version)
        """
    )
