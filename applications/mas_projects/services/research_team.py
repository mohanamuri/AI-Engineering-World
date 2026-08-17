"""
Research Team — MAS UC4.

A coordinated research crew:
  Planner → Researcher (× N questions) → Analyst → Writer → END

The Planner breaks the query into specific research questions.
The Researcher looks up each question (Wikipedia), called once per question.
The Analyst synthesises all findings.
The Writer produces a comprehensive final report.

Pattern: Multi-role pipeline with iterative research phase and memory passing.
Most complex MAS pattern in the platform.
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
class ResearchTrace:
    role: str    # "planner" | "researcher" | "analyst" | "writer"
    action: str
    output: str


@dataclass
class ResearchTeamConfig:
    llm_model: str = "mixtral-8x7b-32768"
    temperature: float = 0.0
    max_questions: int = 3
    system_prompt: str = (
        "You are a research director overseeing a team of expert agents. "
        "Ensure the final report is comprehensive, accurate, and well-structured."
    )


@dataclass
class ResearchTeamRun:
    query: str
    traces: list[ResearchTrace]
    report: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class ResearchState(TypedDict):
    query: str
    research_questions: list[str]
    current_idx: int
    findings: list[dict]   # {question: str, finding: str}
    analysis: str
    report: str
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

def build_research_graph(llm: ChatGroq, config: ResearchTeamConfig):
    """Return a compiled Research Team LangGraph graph."""
    max_q = config.max_questions

    def planner_node(state: ResearchState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=(
                f"You are a Research Planner. Break the query into exactly {max_q} "
                "specific, focused research questions that together fully answer it. "
                f"Return exactly {max_q} questions, one per line, numbered 1. 2. 3."
            )),
            HumanMessage(content=f"Query: {state['query']}"),
        ])
        lines = [l.strip() for l in resp.content.strip().split("\n") if l.strip()]
        questions = []
        for line in lines:
            cleaned = line.lstrip("0123456789.)- ").strip()
            if cleaned:
                questions.append(cleaned)
        questions = questions[:max_q]

        trace = {
            "role": "planner",
            "action": f"Created {len(questions)} research questions",
            "output": "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions)),
        }
        return {
            **state,
            "research_questions": questions,
            "current_idx": 0,
            "traces": state["traces"] + [trace],
        }

    def researcher_node(state: ResearchState) -> dict:
        idx = state["current_idx"]
        question = state["research_questions"][idx]

        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Researcher. Formulate the best Wikipedia search query "
                "to answer this specific research question. Return ONLY the query."
            )),
            HumanMessage(content=f"Question: {question}"),
        ])
        search_query = resp.content.strip().strip('"').strip("'")
        tool_result = ALL_TOOLS["wikipedia"].run(search_query)

        finding = {"question": question, "finding": tool_result.tool_output}
        trace = {
            "role": "researcher",
            "action": f"Q{idx+1}: '{search_query}'",
            "output": tool_result.tool_output[:300] + ("…" if len(tool_result.tool_output) > 300 else ""),
        }
        return {
            **state,
            "findings": state["findings"] + [finding],
            "current_idx": idx + 1,
            "traces": state["traces"] + [trace],
        }

    def analyst_node(state: ResearchState) -> dict:
        findings_text = "\n\n".join(
            f"Q: {f['question']}\nA: {f['finding'][:500]}"
            for f in state["findings"]
        )
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Research Analyst. Synthesise the research findings, "
                "identifying key themes, connections, and insights. "
                "Structure your analysis with: Key Findings, Connections, and Implications."
            )),
            HumanMessage(content=(
                f"Original query: {state['query']}\n\n"
                f"Research findings:\n{findings_text}"
            )),
        ])
        analysis = resp.content.strip()
        trace = {
            "role": "analyst",
            "action": f"Synthesised {len(state['findings'])} research findings",
            "output": analysis[:300] + ("…" if len(analysis) > 300 else ""),
        }
        return {**state, "analysis": analysis, "traces": state["traces"] + [trace]}

    def writer_node(state: ResearchState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=config.system_prompt),
            HumanMessage(content=(
                f"Query: {state['query']}\n\n"
                f"Research analysis:\n{state['analysis']}\n\n"
                "Write a comprehensive, well-structured final report that fully answers "
                "the query. Use clear headings and natural prose."
            )),
        ])
        report = resp.content.strip()
        trace = {
            "role": "writer",
            "action": "Wrote final research report",
            "output": report[:300] + ("…" if len(report) > 300 else ""),
        }
        return {**state, "report": report, "traces": state["traces"] + [trace]}

    def route_researcher(state: ResearchState) -> str:
        if state["current_idx"] < len(state["research_questions"]):
            return "researcher"
        return "analyst"

    graph = StateGraph(ResearchState)
    graph.add_node("planner",    planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst",    analyst_node)
    graph.add_node("writer",     writer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_conditional_edges(
        "researcher",
        route_researcher,
        {"researcher": "researcher", "analyst": "analyst"},
    )
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer",  END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_research_team(query: str, config: ResearchTeamConfig) -> ResearchTeamRun:
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    graph = build_research_graph(llm, config)

    initial_state: ResearchState = {
        "query": query,
        "research_questions": [],
        "current_idx": 0,
        "findings": [],
        "analysis": "",
        "report": "",
        "traces": [],
    }

    final_state = graph.invoke(initial_state)

    traces = [
        ResearchTrace(role=t["role"], action=t["action"], output=t["output"])
        for t in final_state["traces"]
    ]

    return ResearchTeamRun(
        query=query,
        traces=traces,
        report=final_state["report"],
    )
