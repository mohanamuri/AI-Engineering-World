"""UC1 — Concept: What is RAGAS and why does RAG quality measurement matter."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — RAGAS Evaluation")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why RAG systems need automated quality measurement — human review doesn't scale\n"
        "- What the 4 RAGAS metrics measure and what a 'good' score looks like\n"
        "- How LLM-based scoring works (no paid RAGAS library needed)\n"
        "- How to interpret low scores and which part of your RAG pipeline to fix"
    )

    st.markdown(
        "You built a RAG app. Users ask questions, your system retrieves documents from a vector "
        "database, and the LLM generates an answer. It *seems* to work — but how do you know?\n\n"
        "**RAGAS (Retrieval-Augmented Generation Assessment)** is a framework that measures RAG "
        "quality across 4 dimensions — automatically, using an LLM as the evaluator."
    )

    st.markdown(
        """
        ### The Problem: RAG Systems Can Fail in 4 Distinct Ways

        A RAG system has two components: the **retriever** (finds documents) and the **generator**
        (writes the answer). Each can fail independently:

        | Failure mode | Symptom | Which metric catches it |
        |---|---|---|
        | LLM ignores retrieved context | Answer fabricates facts | Faithfulness |
        | LLM answers the wrong question | Answer is off-topic | Answer Relevance |
        | Retriever missed the right document | Answer lacks key facts | Context Recall |
        | Retriever returned irrelevant docs | Answer is confused or noisy | Context Precision |

        Without metrics, you might fix the wrong thing — tuning the LLM when the retriever is broken,
        or vice versa.
        """
    )

    st.divider()
    st.markdown("### The 4 RAGAS Metrics — Explained Simply")

    metrics = [
        (
            "1️⃣ Faithfulness (0–1)",
            "**Did the LLM make up facts not in the context?**",
            "The LLM should only state things it can find in the retrieved documents. If it adds "
            "information from its training data or just invents facts, faithfulness drops.\n\n"
            "- Score **1.0** = every statement in the answer is backed by the context\n"
            "- Score **0.5** = roughly half the claims are grounded; half are invented\n"
            "- Score **0.0** = the answer ignores the context entirely\n\n"
            "**Target in production: > 0.80** — below this, users are receiving fabricated information.",
        ),
        (
            "2️⃣ Answer Relevance (0–1)",
            "**Did the answer actually address the question?**",
            "A faithful answer isn't always relevant. The LLM might accurately quote the documents "
            "but talk about a completely different topic than what was asked.\n\n"
            "- Score **1.0** = the answer directly and completely addresses the question\n"
            "- Score **0.5** = partially answers, but drifts off-topic\n"
            "- Score **0.0** = the answer is unrelated to what was asked\n\n"
            "**Target in production: > 0.75** — relevance below this means the prompt or retrieval needs work.",
        ),
        (
            "3️⃣ Context Recall (0–1)",
            "**Did the retriever find the right documents?**",
            "This metric checks whether the retrieved context contains enough information to answer "
            "the question. If the ground-truth answer requires 5 facts and your context only "
            "contains 2 of them, recall is 0.4.\n\n"
            "- Score **1.0** = all ground-truth information is present in the retrieved context\n"
            "- Score **0.5** = about half the needed information was retrieved\n"
            "- Score **0.0** = the retrieved documents contain none of the required information\n\n"
            "**Low recall = fix the retriever** (embeddings, chunking strategy, or number of docs retrieved).",
        ),
        (
            "4️⃣ Context Precision (0–1)",
            "**Were the retrieved documents relevant — or mostly noise?**",
            "You might retrieve 10 documents but only 2 are relevant. The other 8 add noise that "
            "confuses the LLM and may cause it to generate a less accurate answer.\n\n"
            "- Score **1.0** = every retrieved chunk is directly useful for this question\n"
            "- Score **0.5** = roughly half the context is relevant; half is irrelevant noise\n"
            "- Score **0.0** = all retrieved documents are irrelevant\n\n"
            "**Low precision = too many documents retrieved**, or the similarity threshold is too permissive.",
        ),
    ]

    for title, subtitle, body in metrics:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.markdown(subtitle)
            st.markdown(body)

    st.divider()
    st.markdown("### How RAGAS Works — Step by Step")

    steps = [
        (
            "1️⃣ Prepare your evaluation data",
            "For each test case you need: the **question**, the **RAG-generated answer**, "
            "the **retrieved context passages**, and the **ground truth answer** (what the correct "
            "answer should be). Ground truth is needed only for Context Recall — the other three "
            "metrics don't require it.",
        ),
        (
            "2️⃣ Faithfulness check",
            "The judge LLM is asked: *'Given this context, is each statement in the answer "
            "supported?'* It scores 0–10 based on how well the answer is grounded. We divide by 10 "
            "to get a 0–1 score.",
        ),
        (
            "3️⃣ Relevance check",
            "The judge LLM is asked: *'Does the answer actually address the question?'* "
            "It considers whether all parts of the question were answered and whether the response "
            "stayed on topic.",
        ),
        (
            "4️⃣ Recall check",
            "The judge LLM is asked: *'Does the context contain all the information from the "
            "ground truth answer?'* Low recall means the retriever missed important documents.",
        ),
        (
            "5️⃣ Precision check",
            "The judge LLM is asked: *'Are the retrieved context chunks actually useful for "
            "answering this question?'* High noise = low precision.",
        ),
        (
            "6️⃣ Compute overall score",
            "The four scores are averaged: `overall = (faithfulness + relevance + recall + precision) / 4`. "
            "You can weight them differently based on what matters most for your application.",
        ),
    ]

    for step_title, step_body in steps:
        with st.container(border=True):
            st.markdown(f"**{step_title}**")
            st.write(step_body)

    st.divider()
    st.markdown("### Metric Summary Table")
    st.table({
        "Metric": ["Faithfulness", "Answer Relevance", "Context Recall", "Context Precision"],
        "What it measures": [
            "LLM grounded in context?",
            "Answer on-topic?",
            "Retriever found right docs?",
            "Retrieved docs relevant?",
        ],
        "Which component it diagnoses": [
            "Generator (LLM)",
            "Generator (LLM) + Prompt",
            "Retriever (vector search)",
            "Retriever (k / threshold)",
        ],
        "Good score": ["> 0.80", "> 0.75", "> 0.70", "> 0.70"],
        "Requires ground truth?": ["No", "No", "Yes", "No"],
    })

    with st.expander("Show the scoring formula (optional)"):
        st.markdown(
            r"""
            Each metric is scored 0–10 by the judge LLM, then normalised to 0–1:

            $$\text{metric\_score} = \frac{\text{LLM score (0-10)}}{10}$$

            The overall RAGAS score is the arithmetic mean:

            $$\text{overall} = \frac{\text{faithfulness} + \text{relevance} + \text{recall} + \text{precision}}{4}$$

            In the original RAGAS paper, recall uses token-level F1 against the ground truth.
            Our LLM-based version approximates this without requiring token-level annotation.
            """
        )

    st.success(
        "**Next → Playground:** Paste in a real RAG question, answer, and context — "
        "then see all 4 RAGAS scores with the judge's reasoning."
    )
