"""RAGAS-inspired evaluation metrics via LLM prompts (no paid RAGAS library)."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


@dataclass
class RAGASConfig:
    llm_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.0


@dataclass
class RAGASResult:
    question: str
    answer: str
    contexts: list[str]
    faithfulness: float       # 0-1: answer supported by context
    answer_relevance: float   # 0-1: answer addresses the question
    context_recall: float     # 0-1: context covers the ground truth
    context_precision: float  # 0-1: context is relevant (not noisy)
    overall_score: float      # mean of all four
    faithfulness_reason: str = ""
    relevance_reason: str = ""
    recall_reason: str = ""
    precision_reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _get_llm(config: RAGASConfig) -> ChatGroq:
    try:
        import streamlit as st
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")
    return ChatGroq(model=config.llm_model, temperature=config.temperature, api_key=api_key)


def _score_metric(llm, system_prompt: str, user_prompt: str) -> tuple[float, str]:
    """Ask LLM to score 0-10, return (score/10, reason)."""
    resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    text = resp.content.strip()
    import re
    nums = re.findall(r'\b(\d+(?:\.\d+)?)\b', text)
    score = float(nums[0]) / 10.0 if nums else 0.5
    score = max(0.0, min(1.0, score))
    return score, text


def run_ragas_eval(
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: str,
    config: RAGASConfig,
) -> RAGASResult:
    llm = _get_llm(config)
    context_text = "\n---\n".join(contexts)

    # Faithfulness: is the answer supported by the context?
    faith_score, faith_reason = _score_metric(
        llm,
        "You are an evaluation assistant. Rate from 0-10 how well the answer is supported by the "
        "provided context. 10 = fully grounded in context, 0 = contradicts or ignores context. "
        "Output the score first, then a brief reason.",
        f"Context:\n{context_text}\n\nAnswer: {answer}\n\nScore (0-10):",
    )

    # Answer Relevance: does the answer address the question?
    rel_score, rel_reason = _score_metric(
        llm,
        "Rate from 0-10 how well the answer addresses the question asked. "
        "10 = directly and completely answers the question, 0 = off-topic. "
        "Score first, then brief reason.",
        f"Question: {question}\n\nAnswer: {answer}\n\nScore (0-10):",
    )

    # Context Recall: does the context contain the information in the ground truth?
    recall_score, recall_reason = _score_metric(
        llm,
        "Rate from 0-10 how much of the ground truth information is covered by the retrieved context. "
        "10 = all ground truth facts are present in context, 0 = none are. "
        "Score first, then brief reason.",
        f"Ground truth: {ground_truth}\n\nContext:\n{context_text}\n\nScore (0-10):",
    )

    # Context Precision: is the context relevant (not noisy)?
    prec_score, prec_reason = _score_metric(
        llm,
        "Rate from 0-10 how relevant and precise the retrieved context is for answering this question. "
        "10 = all context chunks are highly relevant, 0 = context is mostly irrelevant noise. "
        "Score first, then brief reason.",
        f"Question: {question}\n\nContext:\n{context_text}\n\nScore (0-10):",
    )

    overall = (faith_score + rel_score + recall_score + prec_score) / 4
    return RAGASResult(
        question=question,
        answer=answer,
        contexts=contexts,
        faithfulness=faith_score,
        answer_relevance=rel_score,
        context_recall=recall_score,
        context_precision=prec_score,
        overall_score=overall,
        faithfulness_reason=faith_reason,
        relevance_reason=rel_reason,
        recall_reason=recall_reason,
        precision_reason=prec_reason,
    )
