"""UC2 — Insights: Key takeaways, interview Q&A, and connected concepts."""

import streamlit as st

from applications.aiopt_projects.uc2.constants import ROUTED_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Model Routing")

    result = st.session_state.get(ROUTED_RESULT_KEY)
    if result:
        st.markdown("#### Your last run")
        c1, c2, c3 = st.columns(3)
        c1.metric("Query classified as", result.routing.complexity)
        c2.metric("Model selected", result.routing.model_selected.split("-")[0] + "...")
        c3.metric("Routing overhead", f"{result.routing.routing_latency_ms:.0f} ms")
        st.divider()

    st.markdown("#### When routing is worth the overhead")
    st.table({
        "Traffic pattern": [
            "Mostly simple queries (FAQ, search)",
            "Mostly complex queries (code, analysis)",
            "Mixed traffic (typical)",
            "All queries are similar in complexity",
            "Latency is critical (< 200 ms SLA)",
        ],
        "Worth routing?": ["✅ Yes", "⚠️ Marginal", "✅ Yes", "❌ No", "⚠️ Measure first"],
        "Expected saving": ["60–80 %", "10–20 %", "40–60 %", "< 5 %", "May add 50 ms overhead"],
    })

    st.divider()

    # ── Interview Q&A ────────────────────────────────────────────────────────
    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common questions in ML Engineering / LLM system design interviews.")

    qa_pairs = [
        (
            "How does LLM-based model routing work at a high level?",
            "A lightweight classifier — often the small model itself with a targeted prompt "
            "asking for one word — reads each incoming query and classifies it as SIMPLE or COMPLEX "
            "(or a 1–5 scale). Based on the label, the query is forwarded to the appropriate model. "
            "The classifier call uses max_tokens=5, so overhead is ~50 ms and ~50 tokens — "
            "negligible compared to the full LLM call saved on cheaper models."
        ),
        (
            "What are alternative approaches to model routing beyond an LLM classifier?",
            "Three alternatives: (1) **Rule-based routing** — check for keywords ('code', 'analyse', "
            "'debug') or query length heuristics. Fast but brittle. "
            "(2) **Fine-tuned binary classifier** — train a small BERT/DistilBERT model on labelled "
            "query examples. No LLM call needed, < 5 ms inference. "
            "(3) **Confidence-based routing** — run the small model first; if its confidence score "
            "is below a threshold, escalate to the large model. Adaptive but adds latency on escalation."
        ),
        (
            "How would you measure whether your routing classifier is accurate?",
            "Build a labelled evaluation set of 200–500 queries manually classified as SIMPLE/COMPLEX "
            "by domain experts. Run your classifier on them and measure: "
            "(1) precision and recall for COMPLEX (false negatives hurt quality), "
            "(2) precision and recall for SIMPLE (false positives waste cost savings). "
            "Track routing accuracy in production with a sample of user feedback "
            "(e.g. thumbs up/down) segmented by routed model."
        ),
        (
            "What happens if the routing classifier misclassifies a complex query as SIMPLE?",
            "The small model handles a query it's not suited for — quality degrades. "
            "Mitigations: (1) Err on the side of COMPLEX for borderline cases (recall over precision). "
            "(2) Add a confidence threshold — if the classifier output contains hedging language, "
            "route to COMPLEX. "
            "(3) Implement a fallback: if the small model's response is very short or contains "
            "'I don't know', re-route to the large model."
        ),
        (
            "How does model routing fit into the broader LLM cost-optimisation strategy?",
            "Model routing is one of three main levers: "
            "(1) **Semantic caching** — avoid LLM calls entirely for repeated queries. "
            "(2) **Model routing** — use cheaper models for simple queries. "
            "(3) **Prompt compression** — reduce tokens sent to the LLM. "
            "In production, layer all three: cache first, route second, compress third. "
            "Together they typically reduce API spend by 60–85 % for typical enterprise workloads."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()

    # ── Connected Concepts ───────────────────────────────────────────────────
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("Mixture of Experts (MoE)", "Model routing at inference time is architecturally similar "
         "to Mixture-of-Experts at training time. In MoE models (e.g. Mixtral), a gating network "
         "activates only a subset of 'expert' layers per token — same principle: route to the right "
         "component, skip the rest. MoE gives similar quality to a dense 70B model at the cost "
         "of a 12B model."),
        ("Cost-Per-Token Pricing", "Cloud LLM APIs charge per input and output token. "
         "Routing 70 % of queries to an 8B model (10× cheaper than 70B) and only 30 % to 70B "
         "reduces average cost by ~67 %. Knowing your traffic's complexity distribution is critical "
         "for cost modelling."),
        ("Retrieval-Augmented Generation (RAG)", "RAG provides context that can itself determine "
         "routing. If retrieved context is comprehensive, a small model may suffice; if context "
         "is sparse or conflicting, route to the large model to reason over ambiguity."),
        ("Prompt Compression (LLMLingua, etc.)", "Prompt compression reduces the number of tokens "
         "sent to the LLM by compressing context. Combined with routing, it reduces both per-call "
         "cost AND the model tier needed — doubly effective for long-context queries."),
        ("SLA-Driven Routing", "Production systems often route based on both complexity and "
         "latency SLA: if the SLA is < 200 ms, always use 8B regardless of complexity. "
         "If SLA is > 5 s, use 70B. This ensures SLAs are met while still optimising cost."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC3 → Memory Patterns:** Routing controls which model runs. Memory controls "
        "what context the model sees across turns. Combine routing + memory for "
        "cost-efficient, context-aware multi-turn applications."
    )
