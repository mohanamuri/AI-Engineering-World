"""UC2 — Insights: LLM-as-Judge best practices, production checklist, interview Q&A."""

import streamlit as st

from applications.llm_evaluation.uc2.constants import JUDGE_HISTORY_KEY, JUDGE_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — LLM-as-Judge")

    history = st.session_state.get(JUDGE_HISTORY_KEY, [])
    result = st.session_state.get(JUDGE_RESULT_KEY)

    if history:
        st.markdown("#### Your session stats")
        wins_a = sum(1 for h in history if h.winner == "A")
        wins_b = sum(1 for h in history if h.winner == "B")
        ties = sum(1 for h in history if h.winner == "Tie")
        avg_a = sum(h.weighted_avg_a for h in history) / len(history)
        avg_b = sum(h.weighted_avg_b for h in history) / len(history)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Evaluations run", len(history))
        c2.metric("A wins", wins_a)
        c3.metric("B wins", wins_b)
        c4.metric("Avg A score", f"{avg_a:.1f}")
        c5.metric("Avg B score", f"{avg_b:.1f}")
        st.divider()

    st.markdown("#### When to use LLM-as-Judge")
    st.table({
        "Scenario": [
            "A/B test two prompt templates",
            "Evaluate model upgrade (v1 vs v2)",
            "Monitor production response quality",
            "Judge creative writing quality",
            "Verify mathematical proofs",
        ],
        "LLM Judge?": ["✅ Excellent", "✅ Excellent", "✅ Yes (sample 1–5 %)", "⚠️ Caution", "❌ No"],
        "Note": [
            "Pairwise comparison is ideal here",
            "Run on regression test suite before deploy",
            "Use structured criteria for consistency",
            "Subjective — combine with human review",
            "LLMs can't verify formal proofs reliably",
        ],
    })

    st.divider()
    st.markdown("#### Production Checklist")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**✅ Do**")
            st.markdown(
                "- Use temperature=0 for the judge (deterministic scoring)\n"
                "- Swap response order in pairwise eval to detect position bias\n"
                "- Use a stronger model as judge than as generator\n"
                "- Define explicit rubrics for domain-specific criteria\n"
                "- Validate judge scores against 5 % human labels periodically"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**❌ Don't**")
            st.markdown(
                "- Use the same model as both generator and judge (self-preference)\n"
                "- Rely on a single judge call for critical decisions\n"
                "- Use LLM judge as the sole metric for regulated domains\n"
                "- Judge subjective quality (tone, style) without human validation\n"
                "- Skip reasoning — always ask the judge to explain its score"
            )

    st.divider()
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions about LLM evaluation in ML Engineering interviews.")

    qa_pairs = [
        (
            "What is LLM-as-Judge and why is it useful?",
            "LLM-as-Judge is a technique where a capable LLM is used to score or compare the "
            "outputs of another LLM, replacing human annotators for large-scale evaluation. "
            "It works by providing the judge with a question, the response(s) to evaluate, "
            "and a scoring rubric — then asking it to produce a score and a reason. "
            "Studies (e.g. Zheng et al. 2023, MT-Bench) show that GPT-4-level judges achieve "
            "~80 % agreement with human experts on structured criteria. It is particularly useful "
            "for open-ended generation tasks where BLEU/ROUGE are meaningless."
        ),
        (
            "What is position bias in LLM judges and how do you handle it?",
            "Position bias is the tendency for an LLM judge to prefer whichever response it sees "
            "first when doing pairwise comparison. It's caused by attention patterns in the model "
            "that give more weight to earlier context. The standard mitigation is to evaluate both "
            "orderings (A vs B and B vs A) and average the scores. If the judge flips its verdict "
            "when the order changes, declare a tie — the difference is not significant enough to "
            "trust. For single-response scoring (not pairwise), position bias is less of a concern."
        ),
        (
            "When is LLM-as-Judge more appropriate than RAGAS?",
            "RAGAS is specifically designed for RAG systems — it needs a question, retrieved context, "
            "and optionally a ground truth. It measures retrieval and generation quality for "
            "knowledge-grounded Q&A. LLM-as-Judge is more general — it works for any LLM output, "
            "with or without retrieval. Use LLM-as-Judge when: (1) there is no retrieval component, "
            "(2) you need domain-specific criteria (tone, safety, format compliance), or (3) you are "
            "doing A/B testing between two generative approaches. Use RAGAS when you specifically "
            "need to diagnose whether the retriever or generator is the bottleneck."
        ),
        (
            "How do you design custom evaluation criteria for a specific use case?",
            "Start by listing what matters most for your application. For a customer support bot: "
            "accuracy (no wrong information), empathy (appropriate tone), resolution (did it solve "
            "the problem?). For a code assistant: correctness (code runs), style (follows conventions), "
            "explanation (clear comments). For each criterion: (1) give it a clear name, (2) write a "
            "one-sentence definition, (3) provide a weight (higher = matters more), and optionally "
            "(4) provide anchor examples for 1/10 and 10/10. Validate the criteria against 50 human "
            "labels before using in production to ensure the judge agrees with your team's judgement."
        ),
        (
            "How much does it cost to run LLM-as-Judge at scale, and how do you manage that cost?",
            "Each evaluation call costs 1 LLM call per criterion. With 5 criteria and pairwise "
            "comparison (both orderings), that's 10 calls per evaluation pair — roughly 10× the "
            "cost of the original generation. At Groq free-tier rates this is negligible for "
            "evaluation datasets, but adds up for production monitoring. Cost management strategies: "
            "(1) sample 1–5 % of production traffic rather than evaluating everything; (2) use a "
            "smaller, cheaper judge model for batch criteria and reserve the best judge for close "
            "comparisons; (3) batch multiple criteria into a single prompt (trade accuracy for speed); "
            "(4) only invoke the judge when simple heuristics flag a potential issue."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        (
            "MT-Bench (Zheng et al., 2023)",
            "The paper that established LLM-as-Judge as a rigorous evaluation method. "
            "They used GPT-4 as judge on a multi-turn benchmark and showed ~80 % agreement "
            "with human experts. The position-bias and verbosity-bias findings in the paper "
            "are the source for the mitigations described in this app.",
        ),
        (
            "Constitutional AI (Anthropic)",
            "Anthropic's technique for aligning Claude used a form of LLM-as-Judge: the model "
            "critiques its own responses against a 'constitution' (a list of principles). "
            "This shows that self-evaluation, when structured carefully, can improve model behaviour.",
        ),
        (
            "Reward Models in RLHF",
            "Reward models in reinforcement learning from human feedback (RLHF) are trained "
            "classifiers that score LLM outputs. LLM-as-Judge is the inference-time equivalent "
            "of a reward model — it doesn't require training data, making it much easier to deploy "
            "for new domains.",
        ),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC3 → Hallucination Detection:** LLM-as-Judge scores overall quality. "
        "Hallucination Detection goes deeper — it verifies individual factual claims, "
        "giving you a precise hallucination rate per response."
    )
