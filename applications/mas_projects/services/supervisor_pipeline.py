"""
Supervisor Pipeline — MAS UC1.

Fixed sequential pipeline orchestrated by a Supervisor:
  Collector → Processor → Writer → Supervisor (summary) → END

Each stage passes its output directly to the next (chained context).
The Supervisor closes with an executive summary.

Architectural difference from Agent Projects UC4:
  Agent UC4 — Supervisor dynamically routes to any specialist at any step.
  MAS UC1   — Fixed sequential pipeline; agents are chained (A → B → C).
              The Supervisor's role is orchestration at handoffs, not routing.
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
class PipelineTrace:
    """One stage in the pipeline."""
    stage: str   # "collector" | "processor" | "writer" | "supervisor"
    action: str
    output: str


@dataclass
class SupervisorPipelineConfig:
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.0
    system_prompt: str = (
        "You are a senior analyst coordinating a research pipeline. "
        "Your team collects facts, processes them, and writes clear reports. "
        "Ensure the final summary is accurate, concise, and actionable."
    )


@dataclass
class SupervisorPipelineRun:
    task: str
    traces: list[PipelineTrace]
    summary: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class PipelineState(TypedDict):
    task: str
    collector_output: str
    processor_output: str
    writer_output: str
    summary: str
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

def build_pipeline_graph(llm: ChatGroq, config: SupervisorPipelineConfig):
    """Return a compiled Supervisor Pipeline LangGraph graph."""

    def collector_node(state: PipelineState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Fact Collector. Given a task, formulate the best Wikipedia "
                "search query to gather relevant factual information. "
                "Return ONLY the search query — no explanation."
            )),
            HumanMessage(content=f"Task: {state['task']}"),
        ])
        query = resp.content.strip().strip('"').strip("'")
        tool_result = ALL_TOOLS["wikipedia"].run(query)
        output = tool_result.tool_output
        trace = {
            "stage": "collector",
            "action": f"Wikipedia: '{query}'",
            "output": output,
        }
        return {**state, "collector_output": output, "traces": state["traces"] + [trace]}

    def processor_node(state: PipelineState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Data Processor. Analyse the raw facts provided and extract: "
                "1) Key facts (3–5 bullet points) "
                "2) Important numbers or statistics "
                "3) Main themes or patterns. "
                "Be concise and structured."
            )),
            HumanMessage(content=(
                f"Task: {state['task']}\n\n"
                f"Raw facts from Collector:\n{state['collector_output']}"
            )),
        ])
        output = resp.content.strip()
        trace = {
            "stage": "processor",
            "action": "Extracted key insights from collected facts",
            "output": output,
        }
        return {**state, "processor_output": output, "traces": state["traces"] + [trace]}

    def writer_node(state: PipelineState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a Content Writer. Write a clear, well-structured response "
                "to the task based on the processed analysis. "
                "Use natural prose, not bullet points."
            )),
            HumanMessage(content=(
                f"Task: {state['task']}\n\n"
                f"Processed analysis:\n{state['processor_output']}"
            )),
        ])
        output = resp.content.strip()
        trace = {
            "stage": "writer",
            "action": "Wrote structured response from analysis",
            "output": output,
        }
        return {**state, "writer_output": output, "traces": state["traces"] + [trace]}

    def supervisor_node(state: PipelineState) -> dict:
        resp = llm.invoke([
            SystemMessage(content=config.system_prompt),
            HumanMessage(content=(
                f"Task: {state['task']}\n\n"
                f"Your pipeline has completed.\n\n"
                f"Writer's response:\n{state['writer_output']}\n\n"
                "Write a concise executive summary (2–3 sentences) capturing "
                "the most important insight."
            )),
        ])
        summary = resp.content.strip()
        trace = {
            "stage": "supervisor",
            "action": "Wrote executive summary",
            "output": summary,
        }
        return {**state, "summary": summary, "traces": state["traces"] + [trace]}

    graph = StateGraph(PipelineState)
    graph.add_node("collector",  collector_node)
    graph.add_node("processor",  processor_node)
    graph.add_node("writer",     writer_node)
    graph.add_node("supervisor", supervisor_node)

    graph.set_entry_point("collector")
    graph.add_edge("collector",  "processor")
    graph.add_edge("processor",  "writer")
    graph.add_edge("writer",     "supervisor")
    graph.add_edge("supervisor", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_supervisor_pipeline(task: str, config: SupervisorPipelineConfig) -> SupervisorPipelineRun:
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    graph = build_pipeline_graph(llm, config)

    initial_state: PipelineState = {
        "task": task,
        "collector_output": "",
        "processor_output": "",
        "writer_output": "",
        "summary": "",
        "traces": [],
    }

    final_state = graph.invoke(initial_state)

    traces = [
        PipelineTrace(stage=t["stage"], action=t["action"], output=t["output"])
        for t in final_state["traces"]
    ]

    return SupervisorPipelineRun(
        task=task,
        traces=traces,
        summary=final_state["summary"] or final_state["writer_output"],
    )
