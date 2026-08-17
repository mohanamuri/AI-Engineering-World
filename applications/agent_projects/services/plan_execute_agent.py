"""
Plan-and-Execute Agent service for UC2.

LangGraph StateGraph with three phases:

    planner_node → executor_node (loops per step) → responder_node → END

New concept over UC1 (ReAct):
  UC1 reacts step-by-step without a plan — it decides what to do one action at a time.
  UC2 separates planning from execution:
    - The Planner creates a numbered multi-step plan upfront.
    - The Executor runs each step in order, calling tools as needed.
    - The Responder synthesises all step results into a final answer.

This separation makes complex multi-step reasoning more transparent and controllable.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from applications.agent_projects.services.tools import ALL_TOOLS, ToolResult


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class StepResult:
    """Result of executing one plan step."""
    step_number: int
    instruction: str
    result: str
    tool_used: str = ""


@dataclass
class PlanExecuteConfig:
    """Tunable parameters for the Plan-and-Execute agent."""
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.0
    max_plan_steps: int = 5
    enabled_tools: list[str] = field(default_factory=lambda: ["calculator", "wikipedia"])
    system_prompt: str = (
        "You are a methodical assistant that breaks complex tasks into clear steps, "
        "executes each step using available tools, and synthesises results into "
        "a well-structured final answer."
    )


@dataclass
class PlanExecuteRun:
    """One completed plan-and-execute agent run."""
    task: str
    plan: list[str]
    step_results: list[StepResult]
    answer: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class PlanExecuteState(TypedDict):
    task: str
    plan: list[str]            # ordered list of step instructions
    current_step: int
    step_results: list[dict]   # serialised StepResult dicts
    answer: str


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
# Helper: pick best tool for a step instruction
# ---------------------------------------------------------------------------

_MATH_KEYWORDS = ("calculate", "compute", "how many", "what is", "=", "+", "-", "*", "/",
                  "percent", "%", "sum", "multiply", "divide", "squared", "cubed", "power")
_WIKI_KEYWORDS = ("what is", "who is", "where is", "when was", "history",
                  "explain", "define", "tell me about", "information about")


def _pick_tool(instruction: str, enabled: list[str]) -> tuple[str, str]:
    """Return (tool_name, tool_input) for the given step instruction."""
    low = instruction.lower()

    if "calculator" in enabled:
        # Extract a math expression if the instruction looks like a calculation
        expr_match = re.search(
            r"[\d\s\.\+\-\*/\^\(\)%]+", instruction
        )
        if any(kw in low for kw in _MATH_KEYWORDS) and expr_match:
            expr = expr_match.group().strip()
            if len(expr) >= 3:
                return "calculator", expr

    if "wikipedia" in enabled:
        if any(kw in low for kw in _WIKI_KEYWORDS) or len(instruction) < 80:
            # Strip leading "What is / Who is" etc. for cleaner Wikipedia query
            query = re.sub(
                r"^(what is|who is|where is|when was|explain|define|tell me about"
                r"|information about|search for|look up)\s+",
                "",
                low,
            ).strip(" ?.,")
            return "wikipedia", query or instruction

    return "", ""


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_plan_execute_graph(llm: ChatGroq, config: PlanExecuteConfig):
    """Return a compiled Plan-and-Execute LangGraph graph."""

    def planner_node(state: PlanExecuteState) -> dict:
        """Generate a numbered multi-step plan for the task."""
        response = llm.invoke([
            SystemMessage(content=(
                "You are a planning assistant. Given a task, create a concise numbered plan. "
                "Each step should be a single, actionable instruction. "
                f"Use at most {config.max_plan_steps} steps. "
                "Format: '1. ...\\n2. ...\\n3. ...' — no extra commentary."
            )),
            HumanMessage(content=f"Task: {state['task']}"),
        ])
        text = response.content.strip()
        # Parse numbered lines
        plan = []
        for line in text.splitlines():
            line = line.strip()
            m = re.match(r"^\d+[\.\)]\s*(.+)$", line)
            if m:
                plan.append(m.group(1).strip())
        if not plan:
            plan = [state["task"]]
        return {**state, "plan": plan[:config.max_plan_steps], "current_step": 0}

    def executor_node(state: PlanExecuteState) -> dict:
        """Execute the current plan step using a tool or the LLM."""
        idx = state["current_step"]
        instruction = state["plan"][idx]
        step_results = list(state["step_results"])

        tool_name, tool_input = _pick_tool(instruction, config.enabled_tools)
        tool_used = ""

        if tool_name and tool_name in ALL_TOOLS:
            tr: ToolResult = ALL_TOOLS[tool_name].run(tool_input)
            result = tr.tool_output
            tool_used = tool_name
        else:
            # Fallback: ask the LLM directly, incorporating prior results
            prior = "\n".join(
                f"Step {r['step_number']}: {r['result'][:200]}"
                for r in step_results
            )
            context_msg = f"\nPrevious steps:\n{prior}\n\n" if prior else ""
            resp = llm.invoke([
                SystemMessage(content=config.system_prompt),
                HumanMessage(content=f"{context_msg}Current step: {instruction}"),
            ])
            result = resp.content.strip()

        step_results.append({
            "step_number": idx + 1,
            "instruction": instruction,
            "result": result,
            "tool_used": tool_used,
        })
        return {**state, "step_results": step_results, "current_step": idx + 1}

    def responder_node(state: PlanExecuteState) -> dict:
        """Synthesise all step results into a final answer."""
        steps_summary = "\n".join(
            f"Step {r['step_number']} ({r['instruction']}):\n{r['result']}"
            for r in state["step_results"]
        )
        response = llm.invoke([
            SystemMessage(content=config.system_prompt),
            HumanMessage(content=(
                f"Original task: {state['task']}\n\n"
                f"Results from each step:\n{steps_summary}\n\n"
                "Write a clear, complete final answer that directly addresses the task."
            )),
        ])
        return {**state, "answer": response.content.strip()}

    def should_continue_executing(state: PlanExecuteState) -> str:
        if state["current_step"] < len(state["plan"]):
            return "execute"
        return "respond"

    graph = StateGraph(PlanExecuteState)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor",
        should_continue_executing,
        {"execute": "executor", "respond": "responder"},
    )
    graph.add_edge("responder", END)
    return graph.compile()


# ---------------------------------------------------------------------------
# Public runner
# ---------------------------------------------------------------------------

def run_plan_execute_agent(task: str, config: PlanExecuteConfig) -> PlanExecuteRun:
    """Run the Plan-and-Execute agent and return a fully traced result.

    Args:
        task:   The user's natural language task.
        config: PlanExecuteConfig with model and agent parameters.

    Returns:
        PlanExecuteRun with plan, per-step results, and final synthesised answer.
    """
    llm = ChatGroq(
        model=config.llm_model,
        temperature=config.temperature,
        api_key=_get_groq_api_key(),
    )
    graph = build_plan_execute_graph(llm, config)

    initial_state: PlanExecuteState = {
        "task": task,
        "plan": [],
        "current_step": 0,
        "step_results": [],
        "answer": "",
    }

    final_state = graph.invoke(initial_state)

    step_results = [
        StepResult(
            step_number=r["step_number"],
            instruction=r["instruction"],
            result=r["result"],
            tool_used=r.get("tool_used", ""),
        )
        for r in final_state["step_results"]
    ]

    return PlanExecuteRun(
        task=task,
        plan=final_state["plan"],
        step_results=step_results,
        answer=final_state["answer"],
    )
