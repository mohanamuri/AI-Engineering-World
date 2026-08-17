"""
Debate & Judge — MAS UC3.

Adversarial multi-agent debate:
  Proponent (argues FOR) ↔ Opponent (argues AGAINST) — N rounds — Judge

After N rounds a neutral Judge evaluates both sides and declares a winner.

Pattern: Adversarial / deliberative multi-agent with neutral arbitration.
"""

from __future__ import annotations

import os
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
class DebateRound:
    agent: str      # "proponent" | "opponent" | "judge"
    round_num: int
    argument: str


@dataclass
class DebateConfig:
    llm_model: str = "gemma2-9b-it"
    temperature: float = 0.3
    num_rounds: int = 2
    proponent_persona: str = "You are arguing strongly in FAVOUR of the proposition."
    opponent_persona: str = "You are arguing strongly AGAINST the proposition."


@dataclass
class DebateRun:
    topic: str
    rounds: list[DebateRound]
    judgment: str
    winner: str   # "proponent" | "opponent" | "draw"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class DebateState(TypedDict):
    topic: str
    current_round: int
    max_rounds: int
    debate_history: list[dict]   # {agent, round_num, argument}
    judgment: str
    winner: str


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
# Graph builder
# ---------------------------------------------------------------------------

def build_debate_graph(llm: ChatGroq, config: DebateConfig):
    """Return a compiled Debate & Judge LangGraph graph."""

    def _format_history(history: list[dict]) -> str:
        parts = []
        for h in history:
            label = "PROPONENT" if h["agent"] == "proponent" else "OPPONENT"
            parts.append(f"[Round {h['round_num']} — {label}]\n{h['argument']}")
        return "\n\n".join(parts)

    def proponent_node(state: DebateState) -> dict:
        history = _format_history(state["debate_history"])
        context = f"\n\nDebate so far:\n{history}" if history else ""
        instruction = (
            "Make your opening argument."
            if not state["debate_history"]
            else "Respond to your opponent's last argument and strengthen your position."
        )
        resp = llm.invoke([
            SystemMessage(content=(
                f"{config.proponent_persona} "
                "Keep your argument focused (3–4 sentences). Be persuasive and specific."
            )),
            HumanMessage(content=f"Topic: {state['topic']}{context}\n\n{instruction}"),
        ])
        argument = resp.content.strip()
        entry = {"agent": "proponent", "round_num": state["current_round"], "argument": argument}
        return {**state, "debate_history": state["debate_history"] + [entry]}

    def opponent_node(state: DebateState) -> dict:
        history = _format_history(state["debate_history"])
        resp = llm.invoke([
            SystemMessage(content=(
                f"{config.opponent_persona} "
                "Keep your argument focused (3–4 sentences). Be persuasive and specific."
            )),
            HumanMessage(content=(
                f"Topic: {state['topic']}\n\nDebate so far:\n{history}\n\n"
                "Respond to the proponent and argue your opposing position."
            )),
        ])
        argument = resp.content.strip()
        entry = {"agent": "opponent", "round_num": state["current_round"], "argument": argument}
        return {
            **state,
            "debate_history": state["debate_history"] + [entry],
            "current_round": state["current_round"] + 1,
        }

    def judge_node(state: DebateState) -> dict:
        history = _format_history(state["debate_history"])
        resp = llm.invoke([
            SystemMessage(content=(
                "You are an impartial Judge evaluating a debate. "
                "Assess which side made stronger arguments based on evidence, logic, and persuasion. "
                "Provide your evaluation in 2–3 sentences, then declare a winner. "
                "End your response with EXACTLY one of: WINNER: proponent  |  WINNER: opponent  |  WINNER: draw"
            )),
            HumanMessage(content=f"Topic: {state['topic']}\n\nFull debate:\n{history}"),
        ])
        judgment_text = resp.content.strip()

        winner = "draw"
        lower = judgment_text.lower()
        if "winner: proponent" in lower:
            winner = "proponent"
        elif "winner: opponent" in lower:
            winner = "opponent"

        return {**state, "judgment": judgment_text, "winner": winner}

    def route_after_opponent(state: DebateState) -> str:
        if state["current_round"] > state["max_rounds"]:
            return "judge"
        return "proponent"

    graph = StateGraph(DebateState)
    graph.add_node("proponent", proponent_node)
    graph.add_node("opponent",  opponent_node)
    graph.add_node("judge",     judge_node)

    graph.set_entry_point("proponent")
    graph.add_edge("proponent", "opponent")
    graph.add_conditional_edges(
        "opponent",
        route_after_opponent,
        {"judge": "judge", "proponent": "proponent"},
    )
    graph.add_edge("judge", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_debate(topic: str, config: DebateConfig) -> DebateRun:
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    graph = build_debate_graph(llm, config)

    initial_state: DebateState = {
        "topic": topic,
        "current_round": 1,
        "max_rounds": config.num_rounds,
        "debate_history": [],
        "judgment": "",
        "winner": "",
    }

    final_state = graph.invoke(initial_state)

    rounds = [
        DebateRound(
            agent=h["agent"],
            round_num=h["round_num"],
            argument=h["argument"],
        )
        for h in final_state["debate_history"]
    ]

    return DebateRun(
        topic=topic,
        rounds=rounds,
        judgment=final_state["judgment"],
        winner=final_state["winner"],
    )
