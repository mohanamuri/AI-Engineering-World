"""UC3 — Insights: When hallucination matters, production monitoring, interview Q&A."""

import streamlit as st

from applications.llm_evaluation.uc3.constants import HALLUC_HISTORY_KEY, HALLUC_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Hallucination Detection")

    history = st.session_state.get(HALLUC_HISTORY_KEY, [])
    result = st.session_state.get(HALLUC_RESULT_KEY)

    if history:
        st.markdown("#### Your session stats")
        avg_rate = sum(r.hallucination_rate for r in history) / len(history)
        high_risk = sum(1 for r in history if r.overall_verdict == "High Risk")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Checks run", len(history))
        c2.metric("Avg hallucination rate", f"{avg_rate:.0%}")
        c3.metric("High Risk responses", high_risk)
        c4.metric("Low Risk responses", sum(1 for r in history if r.overall_verdict == "Low Risk"))
        st.divider()

    st.markdown("#### When Hallucination Detection is Critical")
    st.table({
        "Domain": [
            "Medical information",
            "Legal documents",
            "Financial advice",
            "Customer support (policies)",
            "Creative writing",
            "General knowledge chatbot",
        ],
        "Detection needed?": ["✅ Critical", "✅ Critical", "✅ Critical", "✅ Yes", "❌ No", "⚠️ Optional"],
        "Why": [
            "Wrong drug info can harm patients",
            "Wrong legal statements are liabilities",
            "Fabricated market data causes losses",
            "Wrong policy info damages customer trust",
            "Factual accuracy is not the goal",
            "Acceptable risk for low-stakes queries",
        ],
    })

    st.divider()
    st.markdown("#### Production Checklist")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Do**")
            st.markdown(
                "- Run hallucination detection on high-stakes responses before showing to users\n"
                "- Set a hallucination rate threshold (e.g. > 30 % = flag for human review)\n"
                "- Log CONTRADICTED claims — these are the most dangerous\n"
                "- Ground the LLM in retrieved sources to reduce hallucination at the source\n"
                "- Use source attribution: always show which context chunk supports each claim"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Don't**")
            st.markdown(
                "- Run claim verification on every production response — it's expensive\n"
                "- Treat UNVERIFIABLE as safe — they may still be wrong\n"
                "- Use only faithfulness as a hallucination proxy — it's less precise\n"
                "- Skip the claim extraction step — verify whole paragraphs at once is unreliable\n"
                "- Deploy without a fallback message when hallucination rate is too high"
            )

    st.divider()
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions about hallucination in LLM engineering interviews.")

    qa_pairs = [
        (
            "What is the difference between hallucination and a factual error?",
            "All hallucinations are factual errors, but not all factual errors are hallucinations. "
            "A hallucination specifically refers to information that the model fabricated — "
            "generated plausible-sounding content that has no basis in its training data or the "
            "provided context. A factual error could also come from an outdated source, a "
            "misinterpretation of the context, or a reasoning mistake. "
            "In practice the distinction matters for remediation: hallucinations require better "
            "grounding (more context, stricter prompts); outdated facts require fresher retrieval; "
            "reasoning errors require chain-of-thought prompting or verification steps."
        ),
        (
            "What are the tradeoffs between NLI-based and LLM-based hallucination detection?",
            "NLI-based detection uses a small trained classifier (e.g. DeBERTa) that runs in <100 ms "
            "on CPU and costs nothing per call. It works well for short, direct claims but struggles "
            "with multi-hop reasoning, implicit contradictions, and claims requiring world knowledge "
            "beyond the source text. LLM-based detection is slower (~1–2 s per claim), costs API "
            "tokens, but handles nuanced language, provides explanations, and can reason about "
            "context that requires inference. In production, combine both: use NLI for fast first "
            "screening, then LLM-based verification only for claims that NLI flags as uncertain."
        ),
        (
            "How do you reduce hallucination rate in a RAG system?",
            "The most effective interventions in order of impact: "
            "(1) **Better retrieval** — if the context contains the right facts, the LLM is less "
            "likely to fill gaps from training. Improve embeddings and increase k. "
            "(2) **Stricter system prompt** — explicitly instruct: 'Only state facts found in the "
            "provided context. If the answer is not in the context, say so.' "
            "(3) **Lower temperature** — temperature=0 produces more deterministic, less creative "
            "(less hallucinatory) outputs. "
            "(4) **Source attribution** — ask the LLM to cite which document chunk supports each "
            "claim; claims that cannot be cited are likely hallucinations. "
            "(5) **Smaller, more grounded models** — for domain-specific tasks, a fine-tuned "
            "smaller model often hallucinates less than a large general model."
        ),
        (
            "How would you monitor hallucination rate in production?",
            "Running full claim-by-claim detection on every production request is too expensive "
            "(each response requires multiple LLM calls). Instead: "
            "(1) **Sample-based monitoring** — run detection on 2–5 % of requests, stratified by "
            "query type. Alert if the sampled rate exceeds your threshold (e.g. > 20 % for "
            "Low Risk threshold). "
            "(2) **Proxy metrics** — faithfulness score (UC1) is a cheaper proxy; flag responses "
            "with faithfulness < 0.65 for full hallucination check. "
            "(3) **User feedback signals** — thumbs down or 'report incorrect information' are "
            "free hallucination signals. Correlate them with your detection scores. "
            "(4) **CI/CD gating** — run on a fixed test set before every deploy; block if rate "
            "exceeds baseline."
        ),
        (
            "When is hallucination acceptable in an LLM application?",
            "Hallucination tolerance depends entirely on the stakes of being wrong. "
            "It is acceptable in: creative writing (fiction, marketing copy) where facts don't "
            "matter; brainstorming tools where users verify outputs themselves; and exploratory "
            "search where the goal is to surface ideas, not facts. "
            "It is unacceptable in: any application that presents information as authoritative — "
            "medical, legal, financial, or customer-facing product information. "
            "A useful heuristic: if a user could be harmed or misled by acting on the response "
            "without independent verification, hallucination detection is not optional."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        (
            "Self-RAG (Self-Reflective RAG)",
            "A technique where the LLM critiques its own response before returning it — checking "
            "whether each statement is supported by the retrieved context. This is essentially "
            "built-in hallucination detection at generation time, at the cost of a second LLM pass.",
        ),
        (
            "Groundedness in Azure AI / AWS Bedrock",
            "Both major cloud LLM platforms provide built-in groundedness scoring — their "
            "implementation uses NLI-style checks at the platform level. Our claim-by-claim "
            "LLM approach gives you more control and works across any provider.",
        ),
        (
            "Chain-of-Thought as a Mitigation",
            "Asking the LLM to reason step-by-step (chain-of-thought) before giving its final "
            "answer reduces hallucination rate by forcing the model to explicitly connect its "
            "response to the provided evidence. A simple addition to your system prompt: "
            "'Think step by step, citing relevant parts of the context before giving your answer.'",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC4 → Eval Pipeline:** You can now apply all 3 evaluation tools (RAGAS + Judge + Hallucination) "
        "across a full test dataset automatically. UC4 builds the pipeline that does this for you."
    )
