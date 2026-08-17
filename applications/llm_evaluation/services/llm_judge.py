"""LLM-as-Judge: score outputs 1–10 on custom criteria."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq


@dataclass
class JudgeConfig:
    llm_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.0


@dataclass
class JudgeCriteria:
    name: str
    description: str
    weight: float = 1.0  # relative weight for weighted average


@dataclass
class JudgeScore:
    criterion: str
    score: float     # 1-10
    reasoning: str


@dataclass
class JudgeResult:
    response_a: str
    response_b: str
    scores_a: list[JudgeScore]
    scores_b: list[JudgeScore]
    weighted_avg_a: float
    weighted_avg_b: float
    winner: str  # "A", "B", or "Tie"
    overall_reasoning: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


DEFAULT_CRITERIA = [
    JudgeCriteria("Accuracy", "Is the information factually correct?", weight=2.0),
    JudgeCriteria("Relevance", "Does the response address what was asked?", weight=2.0),
    JudgeCriteria("Clarity", "Is it easy to read and understand?", weight=1.0),
    JudgeCriteria("Completeness", "Does it cover all important aspects?", weight=1.5),
    JudgeCriteria("Conciseness", "Is it appropriately brief without losing substance?", weight=1.0),
]


def _get_llm(config: JudgeConfig) -> ChatGroq:
    try:
        import streamlit as st
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")
    return ChatGroq(model=config.llm_model, temperature=config.temperature, api_key=api_key)


def _score_response(
    llm, question: str, response: str, criteria: list[JudgeCriteria]
) -> list[JudgeScore]:
    import re
    scores = []
    for c in criteria:
        resp = llm.invoke([
            SystemMessage(content=(
                f"You are an objective AI judge. Rate the response on '{c.name}': {c.description}\n"
                "Output a single integer score from 1 (very poor) to 10 (excellent), then a one-sentence reason. "
                "Format: SCORE: N\nREASON: ..."
            )),
            HumanMessage(content=f"Question: {question}\n\nResponse: {response}"),
        ])
        text = resp.content.strip()
        nums = re.findall(r'\b([1-9]|10)\b', text)
        score = float(nums[0]) if nums else 5.0
        reason = text.split("REASON:")[-1].strip() if "REASON:" in text else text
        scores.append(JudgeScore(criterion=c.name, score=score, reasoning=reason))
    return scores


def run_llm_judge(
    question: str,
    response_a: str,
    response_b: str,
    criteria: list[JudgeCriteria],
    config: JudgeConfig,
) -> JudgeResult:
    llm = _get_llm(config)
    scores_a = _score_response(llm, question, response_a, criteria)
    scores_b = _score_response(llm, question, response_b, criteria)

    total_weight = sum(c.weight for c in criteria)
    avg_a = sum(s.score * c.weight for s, c in zip(scores_a, criteria)) / total_weight
    avg_b = sum(s.score * c.weight for s, c in zip(scores_b, criteria)) / total_weight

    if abs(avg_a - avg_b) < 0.5:
        winner = "Tie"
    elif avg_a > avg_b:
        winner = "A"
    else:
        winner = "B"

    reasoning = (
        f"Response {winner} {'wins' if winner != 'Tie' else '(tied)'} — "
        f"A: {avg_a:.1f}/10, B: {avg_b:.1f}/10."
    )

    return JudgeResult(
        response_a=response_a,
        response_b=response_b,
        scores_a=scores_a,
        scores_b=scores_b,
        weighted_avg_a=avg_a,
        weighted_avg_b=avg_b,
        winner=winner,
        overall_reasoning=reasoning,
    )
