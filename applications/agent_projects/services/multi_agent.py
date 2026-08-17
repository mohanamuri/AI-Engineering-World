"""
Multi-Agent Supervisor service for UC4.

LangGraph StateGraph with a Supervisor routing to specialist sub-agents:

    supervisor_node → researcher_node | analyst_node | writer_node → supervisor_node → … → END

New concept over UC3 (Reflection):
  UC3 is a single agent critiquing its own work.
  UC4 introduces multiple LLM agents, each with a distinct role:
    - Researcher: looks up factual information using Wikipedia
    - Analyst: performs calculations using the Calculator tool
    - Writer: synthesises findings into a polished final answer (no tools)
  A Supervisor decides which specialist to call next, or when to finish.

The Supervisor uses structured output (next: "researcher"|"analyst"|"writer"|"FINISH")
to make routing decisions explicit and auditable.
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

from applications.agent_projects.services.tools import ALL_TOOLS


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentTrace:
    """One action taken by one specialist agent."""
    agent_name: str   # "supervisor" | "researcher" | "analyst" | "writer"
    action: str       # short description of what it did
    output: str       # the output produced


@dataclass
class MultiAgentConfig:
    """Tunable parameters for the Multi-Agent Supervisor."""
    llm_model: str = "compound-beta-mini"
    temperature: float = 0.0
    max_rounds: int = 6   # max supervisor → specialist → supervisor cycles
    system_prompt: str = (
        "You are coordinating a team of specialist AI agents. "
        "Each specialist will contribute their expertise. "
        "The final answer should be accurate, well-structured, and complete."
    )


@dataclass
class MultiAgentRun:
    """One completed multi-agent run."""
    task: str
    agent_traces: list[AgentTrace]
    answer: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class MultiAgentState(TypedDict):
    task: str
    traces: list[dict]     # serialised AgentTrace dicts
    rounds: int
    answer: str
    next_agent: str        # "researcher" | "analyst" | "writer" | "FINISH"


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

def build_multi_agent_graph(llm: ChatGroq, config: MultiAgentConfig):
    """Return a compiled Multi-Agent Supervisor LangGraph graph."""

    def _context_from_traces(traces: list[dict]) -> str:
        """Format accumulated agent outputs for context injection."""
        if not traces:
            return ""
        parts = []
        for t in traces:
            if t["agent_name"] != "supervisor":
                parts.append(f"[{t['agent_name'].upper()}] {t['action']}: {t['output'][:400]}")
        return "\n\n".join(parts)

    def supervisor_node(state: MultiAgentState) -> dict:
        """Decide which specialist to call next, or FINISH."""
        context = _context_from_traces(state["traces"])
        context_block = f"\n\nWork done so far:\n{context}" if context else ""

        response = llm.invoke([
            SystemMessage(content=(
                "You are a supervisor coordinating three specialist agents:\n"
                "- researcher: looks up factual/encyclopaedic information\n"
                "- analyst: performs numerical calculations and data analysis\n"
                "- writer: synthesises findings into a polished final answer\n\n"
                "Decide which specialist to call next, or FINISH if the task is complete.\n"
                "Reply with EXACTLY one word: researcher, analyst, writer, or FINISH.\n"
                "Do NOT add explanation — only the single word."
            )),
            HumanMessage(content=f"Task: {state['task']}{context_block}"),
        ])
        decision = response.content.strip().lower().split()[0]
        if decision not in ("researcher", "analyst", "writer"):
            decision = "FINISH" if state["rounds"] >= config.max_rounds else "writer"

        trace = {
            "agent_name": "supervisor",
            "action": f"Routed to {decision}",
            "output": f"Next: {decision}",
        }
        return {
            **state,
            "traces": state["traces"] + [trace],
            "rounds": state["rounds"] + 1,
            "next_agent": decision,
        }

    def researcher_node(state: MultiAgentState) -> dict:
        """Use Wikipedia to look up information relevant to the task."""
        # Ask the LLM what to search for
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a research assistant. Given a task, formulate the single best "
                "Wikipedia search query to find relevant information. "
                "Return ONLY the search query — no explanation."
            )),
            HumanMessage(content=f"Task: {state['task']}"),
        ])
        query = resp.content.strip().strip('"').strip("'")
        tool_result = ALL_TOOLS["wikipedia"].run(query)
        output = tool_result.tool_output

        trace = {
            "agent_name": "researcher",
            "action": f"Wikipedia search: '{query}'",
            "output": output,
        }
        return {**state, "traces": state["traces"] + [trace]}

    def analyst_node(state: MultiAgentState) -> dict:
        """Use the Calculator for any numerical analysis the task requires."""
        # Ask the LLM what to calculate
        resp = llm.invoke([
            SystemMessage(content=(
                "You are a numerical analyst. Given a task, extract the most important "
                "calculation to perform. Return ONLY a safe Python math expression "
                "(e.g. '2 ** 32' or '(1.05 ** 10 - 1) * 100'). "
                "If no calculation is needed, return 'N/A'."
            )),
            HumanMessage(content=f"Task: {state['task']}"),
        ])
        expr = resp.content.strip().strip('"').strip("'")

        if expr.upper() == "N/A" or not expr:
            output = "No numerical calculation required for this task."
            action = "No calculation needed"
        else:
            tool_result = ALL_TOOLS["calculator"].run(expr)
            output = f"Expression: {expr}\nResult: {tool_result.tool_output}"
            action = f"Calculated: {expr}"

        trace = {
            "agent_name": "analyst",
            "action": action,
            "output": output,
        }
        return {**state, "traces": state["traces"] + [trace]}

    def writer_node(state: MultiAgentState) -> dict:
        """Synthesise all findings into a final, polished answer."""
        context = _context_from_traces(state["traces"])
        response = llm.invoke([
            SystemMessage(content=config.system_prompt),
            HumanMessage(content=(
                f"Task: {state['task']}\n\n"
                f"Research and analysis gathered by your team:\n{context}\n\n"
                "Write a clear, well-structured final answer that directly addresses the task. "
                "Incorporate the team's findings naturally."
            )),
        ])
        answer = response.content.strip()
        trace = {
            "agent_name": "writer",
            "action": "Wrote final answer",
            "output": answer[:200] + ("…" if len(answer) > 200 else ""),
        }
        return {
            **state,
            "traces": state["traces"] + [trace],
            "answer": answer,
        }

    def route_supervisor(state: MultiAgentState) -> str:
        na = state.get("next_agent", "")
        if na == "FINISH" or state["rounds"] >= config.max_rounds:
            return "finish"
        return na if na in ("researcher", "analyst", "writer") else "finish"

    graph = StateGraph(MultiAgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst",    analyst_node)
    graph.add_node("writer",     writer_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "analyst":    "analyst",
            "writer":     "writer",
            "finish":     END,
        },
    )
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("analyst",    "supervisor")
    graph.add_edge("writer",     END)   # writer is always the final step

    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_multi_agent(task: str, config: MultiAgentConfig) -> MultiAgentRun:
    """Run the Multi-Agent Supervisor and return a fully traced result.

    Args:
        task:   The user's natural language task.
        config: MultiAgentConfig with model and routing parameters.

    Returns:
        MultiAgentRun with agent_traces, final answer, and timestamp.
    """
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    graph = build_multi_agent_graph(llm, config)

    initial_state: MultiAgentState = {
        "task": task,
        "traces": [],
        "rounds": 0,
        "answer": "",
        "next_agent": "",
    }

    final_state = graph.invoke(initial_state)

    agent_traces = [
        AgentTrace(
            agent_name=t["agent_name"],
            action=t["action"],
            output=t["output"],
        )
        for t in final_state["traces"]
    ]

    answer = final_state["answer"]
    if not answer:
        # Extract from writer trace if graph ended without explicit answer
        for t in reversed(agent_traces):
            if t.agent_name == "writer":
                answer = t.output
                break

    return MultiAgentRun(
        task=task,
        agent_traces=agent_traces,
        answer=answer,
    )
