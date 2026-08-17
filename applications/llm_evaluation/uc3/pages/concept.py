"""UC3 — Concept: What is hallucination, how to detect it, and why it matters."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Hallucination Detection")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- What hallucination is and why LLMs do it (it's not a bug, it's how they work)\n"
        "- The 3 types of hallucination and which is most dangerous in production\n"
        "- Two detection approaches: NLI-based (fast) vs LLM-based (flexible)\n"
        "- How the claim extraction + verification pipeline works step by step\n"
        "- How to compute a hallucination rate for any LLM response"
    )

    st.markdown(
        "LLMs are trained to produce fluent, confident-sounding text. They do not know "
        "what they don't know — when the model lacks information, it generates plausible-sounding "
        "text rather than saying 'I don't know'. The result is **hallucination**: confidently "
        "stated facts that are fabricated, outdated, or contradicted by the source material.\n\n"
        "In a customer support chatbot, this might mean wrong return policy details. "
        "In a medical assistant, it could mean a dangerous drug interaction that doesn't exist. "
        "**Detecting hallucinations before they reach users is a safety requirement** "
        "in any high-stakes LLM application."
    )

    st.markdown(
        """
        ### The 3 Types of Hallucination

        Not all hallucinations are equal. Understanding the type helps you choose the right mitigation.
        """
    )

    types = [
        (
            "1. Factual Hallucination",
            "The LLM states a fact that is simply wrong — not just missing from the source, "
            "but actively incorrect. The model may cite a non-existent study, attribute a quote "
            "to the wrong person, or state a date/number incorrectly.\n\n"
            "**Example:** 'The Eiffel Tower was built in 1901' (correct: 1889)\n\n"
            "**Risk level:** High — wrong facts are stated with confidence\n"
            "**Mitigation:** Ground the LLM in retrieved context; verify with authoritative sources",
        ),
        (
            "2. Contextual Hallucination",
            "The fact may be true in general, but it is not supported by the specific source "
            "context provided. The LLM adds its training knowledge rather than staying grounded "
            "in the retrieved documents.\n\n"
            "**Example:** User asks about a company's return policy. The LLM states a 30-day "
            "return window because that's common industry practice — but the actual policy says 14 days.\n\n"
            "**Risk level:** Very high in RAG systems — the specific answer matters\n"
            "**Mitigation:** Faithfulness checks (RAGAS UC1) + this hallucination detector",
        ),
        (
            "3. Temporal Hallucination",
            "The fact was true at training time but is now outdated. LLMs have a knowledge "
            "cutoff date — any information that changed after that date may be hallucinated.\n\n"
            "**Example:** An LLM states a politician is 'currently serving as Prime Minister' "
            "when they left office after the model's training cutoff.\n\n"
            "**Risk level:** Medium — depends on how time-sensitive the domain is\n"
            "**Mitigation:** Always retrieve fresh documents for time-sensitive queries; "
            "add the current date to the system prompt",
        ),
    ]

    for type_title, type_body in types:
        with st.container(border=True):
            st.markdown(f"**{type_title}**")
            st.write(type_body)

    st.divider()
    st.markdown("### Two Detection Approaches")

    col_nli, col_llm = st.columns(2)
    with col_nli:
        with st.container(border=True):
            st.markdown("**NLI-Based Detection (fast, no LLM)**")
            st.markdown(
                "Natural Language Inference (NLI) models are trained to classify whether a "
                "*premise* entails, contradicts, or is neutral towards a *hypothesis*.\n\n"
                "**How it works:** For each claim, run a small NLI model (e.g. `cross-encoder/nli-deberta-v3-small`) "
                "against the source context. Get ENTAILMENT / CONTRADICTION / NEUTRAL.\n\n"
                "**Pros:** Very fast (<100 ms per claim), no API cost, works offline\n"
                "**Cons:** Struggles with complex reasoning, multi-hop claims, or claims "
                "requiring world knowledge not in the premise\n\n"
                "**Best for:** High-volume production monitoring at low cost"
            )
    with col_llm:
        with st.container(border=True):
            st.markdown("**LLM-Based Detection (flexible, this app)**")
            st.markdown(
                "Use a capable LLM as the verifier: 'Is this claim supported, contradicted, "
                "or unverifiable given this context?'\n\n"
                "**How it works:** Extract claims → for each claim, ask the LLM to verify "
                "against the source and provide a verdict + evidence.\n\n"
                "**Pros:** Handles nuanced language, implicit contradictions, multi-step "
                "reasoning; returns explanations (audit trail)\n"
                "**Cons:** Slower (~1–2 s per claim), costs API tokens\n\n"
                "**Best for:** Spot checks, audits, and cases where explanation is required"
            )

    st.divider()
    st.markdown("### The Claim Extraction + Verification Pipeline")

    steps = [
        (
            "1️⃣ Receive the LLM response",
            "Start with the full text of the LLM's response — this is what you want to check for hallucinations.",
        ),
        (
            "2️⃣ Extract individual claims",
            "Ask a claim-extraction LLM to break the response into atomic, verifiable statements. "
            "Each claim should be a single fact that can be independently verified. "
            "Skip obvious facts ('water is wet') and opinions ('this is a great approach'). "
            "Target 3–8 claims per response.",
        ),
        (
            "3️⃣ Verify each claim",
            "For each claim, ask the verifier LLM: 'Given this source context, is this claim "
            "SUPPORTED, CONTRADICTED, or UNVERIFIABLE?' "
            "SUPPORTED = context confirms the claim. "
            "CONTRADICTED = context directly says otherwise. "
            "UNVERIFIABLE = context doesn't address this claim at all.",
        ),
        (
            "4️⃣ Compute hallucination rate",
            "Hallucination rate = (claims not supported) / (total claims). "
            "CONTRADICTED claims are high risk (active misinformation). "
            "UNVERIFIABLE claims are medium risk (added without grounding).",
        ),
        (
            "5️⃣ Assign overall verdict",
            "Low Risk: hallucination rate < 20 %. "
            "Medium Risk: 20–50 %. "
            "High Risk: > 50 %. "
            "Flag High Risk responses for human review before showing to users.",
        ),
    ]

    for step_title, step_body in steps:
        with st.container(border=True):
            st.markdown(f"**{step_title}**")
            st.write(step_body)

    st.divider()
    st.markdown("### Worked Example")
    st.markdown(
        "**Source context:** *'Aspirin was developed by Bayer chemist Felix Hoffmann in 1897. "
        "The active ingredient is acetylsalicylic acid. It is used as an analgesic and anti-inflammatory.'*"
    )
    st.markdown("**LLM response:** *'Aspirin was invented in 1899 by a team at Bayer. It contains "
                "acetylsalicylic acid and is commonly used for pain relief and fever reduction.'*")

    claims = [
        ("Aspirin was invented in 1899", "CONTRADICTED", "Source says 1897"),
        ("It was invented by a team at Bayer", "CONTRADICTED", "Source says Felix Hoffmann individually"),
        ("It contains acetylsalicylic acid", "SUPPORTED", "Directly stated in source"),
        ("It is used for pain relief", "SUPPORTED", "Source says 'analgesic' = pain relief"),
        ("It is used for fever reduction", "UNVERIFIABLE", "Source doesn't mention fever reduction"),
    ]

    for claim, verdict, evidence in claims:
        col_claim, col_verdict, col_evidence = st.columns([3, 1, 3])
        color = {"SUPPORTED": "🟢", "CONTRADICTED": "🔴", "UNVERIFIABLE": "🟡"}[verdict]
        col_claim.markdown(f'"{claim}"')
        col_verdict.markdown(f"{color} {verdict}")
        col_evidence.markdown(f"*{evidence}*")

    st.markdown(
        "**Hallucination rate: 3/5 = 60 % → High Risk**  \n"
        "2 claims are directly contradicted, 1 is unverifiable. "
        "This response should not be shown to users without correction."
    )

    st.success(
        "**Next → Playground:** Paste any LLM response + the source context, "
        "and see every claim extracted and verified automatically."
    )
