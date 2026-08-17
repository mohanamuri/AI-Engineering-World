"""
Reflection Agent service for UC3.

LangGraph StateGraph with a Generate → Critique → Revise loop:

    generator_node → critic_node → reviser_node → critic_node → … → END

New concept over UC2 (Plan-and-Execute):
  UC2 executes a plan with external tools — it doesn't evaluate its own output.
  UC3 adds a self-critique step after every draft:
    - The generator writes an initial response.
    - The critic scores it on three dimensions (Clarity, Accuracy, Completeness) 1–5.
    - If any score is below threshold, a reviser rewrites the draft.
    - This loop continues until quality passes or max_revisions is reached.

No external tools are needed — the quality loop is pure LLM reasoning.
Mirrors the Self-RAG concept but applied to general-purpose generation.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class DraftRecord:
    """One draft + its critique scores."""
    draft_number: int
    content: str
    clarity: int       # 1–5
    accuracy: int      # 1–5
    completeness: int  # 1–5

    @property
    def avg(self) -> float:
        return round((self.clarity + self.accuracy + self.completeness) / 3, 2)

    def scores_ok(self, threshold: int) -> bool:
        return (self.clarity >= threshold
                and self.accuracy >= threshold
                and self.completeness >= threshold)


@dataclass
class ReflectionConfig:
    """Tunable parameters for the Reflection agent."""
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.3
    max_revisions: int = 3
    quality_threshold: int = 4    # 1–5; all dimensions must reach this to pass
    system_prompt: str = (
        "You are a thoughtful writer who produces clear, accurate, and complete responses. "
        "When given feedback, you revise your work to address every critique point specifically."
    )


@dataclass
class ReflectionRun:
    """One completed reflection agent run."""
    task: str
    drafts: list[DraftRecord]
    final_answer: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class ReflectionState(TypedDict):
    task: str
    current_draft: str
    drafts: list[dict]    # serialised DraftRecord dicts (without final draft)
    revision_count: int
    passed: bool


# ---------------------------------------------------------------------------
# Groq key helper
# ---------------------------------------------------------------------------

def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


# ---------------------------------------------------------------------------
# Score parsing helper
# ---------------------------------------------------------------------------

def _parse_scores(text: str) -> tuple[int, int, int]:
    """Extract Clarity, Accuracy, Completeness scores (1–5) from critic output."""
    def extract(label: str) -> int:
        pattern = rf"{label}[:\s]+(\d)"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return max(1, min(5, int(m.group(1))))
        # fallback: find any digit after the label
        idx = text.lower().find(label.lower())
        if idx >= 0:
            snippet = text[idx:idx+20]
            digits = re.findall(r"\d", snippet)
            if digits:
                return max(1, min(5, int(digits[0])))
        return 3  # neutral default

    return (
        extract("clarity"),
        extract("accuracy"),
        extract("completeness"),
    )


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_reflection_graph(llm: ChatGroq, config: ReflectionConfig):
    """Return a compiled Reflection LangGraph graph."""

    def generator_node(state: ReflectionState) -> dict:
        """Produce the initial draft (or a revision incorporating prior critique)."""
        if state["revision_count"] == 0:
            # First draft — no prior context
            response = llm.invoke([
                SystemMessage(content=config.system_prompt),
                HumanMessage(content=state["task"]),
            ])
        else:
            # Revision — include the critique of the last draft
            last_draft_dict = state["drafts"][-1] if state["drafts"] else {}
            critique_summary = (
                f"Clarity: {last_draft_dict.get('clarity', '?')}/5  "
                f"Accuracy: {last_draft_dict.get('accuracy', '?')}/5  "
                f"Completeness: {last_draft_dict.get('completeness', '?')}/5"
            )
            prev_draft = last_draft_dict.get("content", "")
            response = llm.invoke([
                SystemMessage(content=config.system_prompt),
                HumanMessage(content=(
                    f"Original task: {state['task']}\n\n"
                    f"Your previous draft:\n{prev_draft}\n\n"
                    f"Critique scores — {critique_summary}\n\n"
                    "Rewrite the response to improve the lowest-scoring dimensions. "
                    "Be specific, accurate, and complete."
                )),
            ])
        return {**state, "current_draft": response.content.strip()}

    def critic_node(state: ReflectionState) -> dict:
        """Score the current draft and record the result."""
        draft = state["current_draft"]
        response = llm.invoke([
            SystemMessage(content=(
                "You are a strict quality evaluator. Score the response on three dimensions, "
                "each on a scale of 1–5:\n"
                "- Clarity (1=very unclear, 5=perfectly clear)\n"
                "- Accuracy (1=many errors, 5=fully accurate)\n"
                "- Completeness (1=very incomplete, 5=fully complete)\n\n"
                "Format your response EXACTLY as:\n"
                "Clarity: N\nAccuracy: N\nCompleteness: N\n\n"
                "Then one sentence of feedback."
            )),
            HumanMessage(content=(
                f"Task: {state['task']}\n\nResponse to evaluate:\n{draft}"
            )),
        ])
        clarity, accuracy, completeness = _parse_scores(response.content)
        draft_num = state["revision_count"] + 1
        draft_record = {
            "draft_number": draft_num,
            "content": draft,
            "clarity": clarity,
            "accuracy": accuracy,
            "completeness": completeness,
        }
        passed = (
            clarity >= config.quality_threshold
            and accuracy >= config.quality_threshold
            and completeness >= config.quality_threshold
        )
        return {
            **state,
            "drafts": state["drafts"] + [draft_record],
            "revision_count": draft_num,
            "passed": passed,
        }

    def should_revise(state: ReflectionState) -> str:
        if state["passed"]:
            return "end"
        if state["revision_count"] >= config.max_revisions:
            return "end"
        return "revise"

    graph = StateGraph(ReflectionState)
    graph.add_node("generator", generator_node)
    graph.add_node("critic",    critic_node)

    graph.set_entry_point("generator")
    graph.add_edge("generator", "critic")
    graph.add_conditional_edges(
        "critic",
        should_revise,
        {"revise": "generator", "end": END},
    )
    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_reflection_agent(task: str, config: ReflectionConfig) -> ReflectionRun:
    """Run the Reflection agent and return all drafts + the final answer.

    Args:
        task:   The user's natural language task.
        config: ReflectionConfig with model and quality parameters.

    Returns:
        ReflectionRun with all drafts, critique scores, and final answer.
    """
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    graph = build_reflection_graph(llm, config)

    initial_state: ReflectionState = {
        "task": task,
        "current_draft": "",
        "drafts": [],
        "revision_count": 0,
        "passed": False,
    }

    final_state = graph.invoke(initial_state)

    drafts = [
        DraftRecord(
            draft_number=d["draft_number"],
            content=d["content"],
            clarity=d["clarity"],
            accuracy=d["accuracy"],
            completeness=d["completeness"],
        )
        for d in final_state["drafts"]
    ]

    final_answer = drafts[-1].content if drafts else ""

    return ReflectionRun(
        task=task,
        drafts=drafts,
        final_answer=final_answer,
    )
