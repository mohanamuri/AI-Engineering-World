"""
ReAct Agent service for UC1.

LangGraph StateGraph implementing the classic Reason+Act loop:

    agent_node → tools_node → agent_node (loop) → END

The LLM uses Groq's tool-calling API to pick which tool to invoke and with
what input. Every tool call and LLM response is captured as a TraceStep so
the UI can show exactly what the agent was "thinking" at each iteration.

New concept: tool-use + transparent reasoning traces.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from applications.agent_projects.services.tools import (
    ALL_TOOLS,
    CalculatorTool,
    ToolResult,
    WikipediaTool,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TraceStep:
    """One step captured during agent execution."""
    step_type: str   # "thought" | "tool_call" | "tool_result" | "answer"
    content: str     # human-readable summary
    detail: str = "" # extra info (tool name, input/output, etc.)


@dataclass
class ReactConfig:
    """Tunable parameters for the ReAct agent."""
    llm_model: str = "compound-beta-mini"
    temperature: float = 0.0
    max_iterations: int = 6
    enabled_tools: list[str] = field(default_factory=lambda: ["calculator", "wikipedia"])
    system_prompt: str = (
        "You are a helpful assistant that reasons step-by-step and uses tools "
        "when needed. Always think before acting. After using a tool, incorporate "
        "the result into your reasoning before deciding the next step."
    )


@dataclass
class ReactRun:
    """One completed agent run."""
    task: str
    answer: str
    steps: list[TraceStep] = field(default_factory=list)
    iterations: int = 0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class ReactState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    steps: list[dict]       # serialised TraceStep dicts
    iterations: int


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
# Tool schema helpers (LangChain tool format for Groq)
# ---------------------------------------------------------------------------

def _build_tool_schemas(enabled: list[str]) -> list[dict]:
    """Return OpenAI-style function schemas for the enabled tools."""
    schemas = []
    tool_meta = {
        "calculator": {
            "name": "calculator",
            "description": CalculatorTool().description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, e.g. '2 ** 10'",
                    }
                },
                "required": ["expression"],
            },
        },
        "wikipedia": {
            "name": "wikipedia",
            "description": WikipediaTool().description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Short topic or search phrase",
                    }
                },
                "required": ["query"],
            },
        },
    }
    for name in enabled:
        if name in tool_meta:
            schemas.append({"type": "function", "function": tool_meta[name]})
    return schemas


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_react_graph(llm_with_tools, tools_map: dict, config: ReactConfig):
    """Return a compiled LangGraph ReAct graph."""

    def agent_node(state: ReactState) -> dict:
        response: AIMessage = llm_with_tools.invoke(state["messages"])
        steps = list(state["steps"])

        if response.tool_calls:
            for tc in response.tool_calls:
                steps.append({
                    "step_type": "thought",
                    "content": f"Decided to call tool: {tc['name']}",
                    "detail": f"Input: {tc['args']}",
                })
        else:
            steps.append({
                "step_type": "answer",
                "content": "Generated final answer",
                "detail": response.content[:120] + ("…" if len(response.content) > 120 else ""),
            })

        return {
            "messages": [response],
            "steps": steps,
            "iterations": state["iterations"] + 1,
        }

    def tools_node(state: ReactState) -> dict:
        last_msg: AIMessage = state["messages"][-1]
        tool_messages = []
        steps = list(state["steps"])

        for tc in last_msg.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool = tools_map.get(tool_name)

            if tool is None:
                result_str = f"Tool '{tool_name}' not available."
                success = False
            else:
                if tool_name == "calculator":
                    tr: ToolResult = tool.run(tool_args.get("expression", ""))
                elif tool_name == "wikipedia":
                    tr = tool.run(tool_args.get("query", ""))
                else:
                    tr = tool.run(str(tool_args))
                result_str = tr.tool_output
                success = tr.success

            steps.append({
                "step_type": "tool_call",
                "content": f"Called {tool_name}",
                "detail": f"Input: {tool_args}",
            })
            steps.append({
                "step_type": "tool_result",
                "content": f"Result from {tool_name}",
                "detail": result_str[:300] + ("…" if len(result_str) > 300 else ""),
            })

            tool_messages.append(
                ToolMessage(content=result_str, tool_call_id=tc["id"])
            )

        return {"messages": tool_messages, "steps": steps}

    def should_continue(state: ReactState) -> str:
        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            if state["iterations"] < config.max_iterations:
                return "tools"
        return "end"

    graph = StateGraph(ReactState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END},
    )
    graph.add_edge("tools", "agent")
    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_react_agent(task: str, config: ReactConfig) -> ReactRun:
    """Run the ReAct agent and return a fully traced result.

    Args:
        task:   The user's natural language task.
        config: ReactConfig with model and agent parameters.

    Returns:
        ReactRun with final answer, trace steps, and iteration count.
    """
    tools_map = {
        name: ALL_TOOLS[name]
        for name in config.enabled_tools
        if name in ALL_TOOLS
    }
    tool_schemas = _build_tool_schemas(config.enabled_tools)

    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    llm_with_tools = llm.bind_tools(tool_schemas) if tool_schemas else llm

    graph = build_react_graph(llm_with_tools, tools_map, config)

    initial_state: ReactState = {
        "messages": [
            SystemMessage(content=config.system_prompt),
            HumanMessage(content=task),
        ],
        "steps": [],
        "iterations": 0,
    }

    final_state = graph.invoke(initial_state)

    # Extract final answer from last AI message
    answer = ""
    for msg in reversed(final_state["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            answer = msg.content
            break

    steps = [
        TraceStep(
            step_type=s["step_type"],
            content=s["content"],
            detail=s.get("detail", ""),
        )
        for s in final_state["steps"]
    ]

    return ReactRun(
        task=task,
        answer=answer,
        steps=steps,
        iterations=final_state["iterations"],
    )
