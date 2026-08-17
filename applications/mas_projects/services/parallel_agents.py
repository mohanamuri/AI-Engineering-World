"""
Parallel Agents — MAS UC2.

Three specialist agents tackle the same task from independent angles:
  • Facts Agent    — encyclopaedic facts via Wikipedia
  • Critic Agent   — challenges, limitations, counterpoints
  • Creative Agent — novel angles, analogies, broader implications

All three run independently (no shared intermediate state).
An Aggregator merges the three perspectives into one coherent answer.

Pattern: Fan-out (1 task → 3 agents) + Fan-in (3 outputs → 1 answer).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from applications.agent_projects.services.tools import ALL_TOOLS


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ParallelTrace:
    agent: str        # "facts" | "critic" | "creative" | "aggregator"
    perspective: str  # human-readable label
    output: str


@dataclass
class ParallelAgentsConfig:
    llm_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.2
    system_prompt: str = (
        "You are an expert synthesiser combining multiple independent expert "
        "perspectives into one comprehensive, balanced, and insightful response."
    )


@dataclass
class ParallelAgentsRun:
    task: str
    traces: list[ParallelTrace]
    answer: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class ParallelState(TypedDict):
    task: str
    facts_output: str
    critic_output: str
    creative_output: str
    answer: str
    traces: list[dict]


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

def build_parallel_graph(llm: ChatGroq, config: ParallelAgentsConfig):
    """Return a compiled Parallel Agents LangGraph graph."""

    def facts_node(state: ParallelState) -> dict:
        # Generate search query then retrieve
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Facts Agent. Return ONLY a short Wikipedia search query "
                "to find the most relevant factual information about the task."
            )),
            HumanMessage(content=f"Task: {state['task']}"),
        ])
        query = resp.content.strip().strip('"').strip("'")
        tool_result = ALL_TOOLS["wikipedia"].run(query)

        resp2 = llm.invoke([
            SystemMessage(content=(
                "You are a Facts Agent. Summarise the most important factual "
                "information relevant to the task in 3–5 clear sentences."
            )),
            HumanMessage(content=f"Task: {state['task']}\n\nSource material:\n{tool_result.tool_output}"),
        ])
        output = resp2.content.strip()
        trace = {"agent": "facts", "perspective": "Factual Analysis", "output": output}
        return {**state, "facts_output": output, "traces": state["traces"] + [trace]}

    def critic_node(state: ParallelState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Critical Analyst. Your job is to challenge assumptions, "
                "identify limitations, risks, or counterarguments related to the task. "
                "Provide 3–4 constructive but rigorous critical observations."
            )),
            HumanMessage(content=f"Task: {state['task']}"),
        ])
        output = resp.content.strip()
        trace = {"agent": "critic", "perspective": "Critical Analysis", "output": output}
        return {**state, "critic_output": output, "traces": state["traces"] + [trace]}

    def creative_node(state: ParallelState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Creative Thinker. Offer novel angles, unexpected analogies, "
                "broader implications, or creative insights about the task that others "
                "might overlook. Provide 3–4 creative perspectives."
            )),
            HumanMessage(content=f"Task: {state['task']}"),
        ])
        output = resp.content.strip()
        trace = {"agent": "creative", "perspective": "Creative Insights", "output": output}
        return {**state, "creative_output": output, "traces": state["traces"] + [trace]}

    def aggregator_node(state: ParallelState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=config.system_prompt),
            HumanMessage(content=(
                f"Task: {state['task']}\n\n"
                f"--- FACTS AGENT ---\n{state['facts_output']}\n\n"
                f"--- CRITICAL ANALYST ---\n{state['critic_output']}\n\n"
                f"--- CREATIVE THINKER ---\n{state['creative_output']}\n\n"
                "Synthesise these three independent perspectives into a single comprehensive "
                "answer. Preserve the depth of each perspective while creating a coherent whole."
            )),
        ])
        answer = resp.content.strip()
        trace = {"agent": "aggregator", "perspective": "Aggregated Answer", "output": answer}
        return {**state, "answer": answer, "traces": state["traces"] + [trace]}

    graph = StateGraph(ParallelState)
    graph.add_node("facts",      facts_node)
    graph.add_node("critic",     critic_node)
    graph.add_node("creative",   creative_node)
    graph.add_node("aggregator", aggregator_node)

    graph.set_entry_point("facts")
    graph.add_edge("facts",      "critic")
    graph.add_edge("critic",     "creative")
    graph.add_edge("creative",   "aggregator")
    graph.add_edge("aggregator", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_parallel_agents(task: str, config: ParallelAgentsConfig) -> ParallelAgentsRun:
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    graph = build_parallel_graph(llm, config)

    initial_state: ParallelState = {
        "task": task,
        "facts_output": "",
        "critic_output": "",
        "creative_output": "",
        "answer": "",
        "traces": [],
    }

    final_state = graph.invoke(initial_state)

    traces = [
        ParallelTrace(agent=t["agent"], perspective=t["perspective"], output=t["output"])
        for t in final_state["traces"]
    ]

    return ParallelAgentsRun(
        task=task,
        traces=traces,
        answer=final_state["answer"],
    )
