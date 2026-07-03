"""
LangGraph ReAct agent for loan eligibility decisions.

Architecture:
  Human message (application) → ReAct loop → Final decision text

The agent uses LangGraph's prebuilt create_react_agent which implements
the ReAct (Reasoning + Acting) pattern:
  1. Think: LLM decides which tool to call
  2. Act: Call the tool
  3. Observe: Receive tool output
  4. Repeat until the LLM produces a final answer (no more tool calls)

Why LangGraph over raw LangChain?
-----------------------------------
LangChain chains are static — you define the steps up front. LangGraph
builds a stateful graph where the agent can loop, branch, and decide
at runtime how many tool calls to make. This mirrors how a real loan
officer thinks: they don't follow a fixed checklist — they investigate
until they have enough evidence.

Why ReAct for T5?
------------------
ReAct is the simplest useful agent pattern: one LLM, multiple tools,
iterative refinement. T6 (Multi-Agent) will show how to split this into
specialist sub-agents (underwriter, fraud detector, compliance) that each
run their own ReAct loop and then report to a supervisor.

Interview note — agent vs pipeline
------------------------------------
A pipeline (T1–T3) runs the same steps for every input.
An agent dynamically decides which steps to run based on what it finds.
For a loan with an excellent credit score, the agent might skip the
policy lookup for minimum scores. For a borderline case, it might call
the risk tool multiple times with different assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from applications.loan_agent.services.agent_tools import AGENT_TOOLS


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentStep:
    """One tool call + response in the agent's reasoning chain."""
    tool_name: str
    tool_input: str
    tool_output: str


@dataclass
class AgentRunResult:
    """Full result of one agent run."""
    application: dict
    steps: list[AgentStep] = field(default_factory=list)
    final_answer: str = ""
    decision: str = "UNKNOWN"       # APPROVED / DECLINED / MANUAL_REVIEW
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class AgentConfig:
    """Tunable agent parameters."""
    llm_model: str = "llama3.1"
    temperature: float = 0.0


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a FinCorp Bank automated loan eligibility agent.

Your task is to evaluate the loan application provided and produce a structured decision.

REQUIRED STEPS (always follow this sequence):
1. Call validate_application to check all eligibility criteria.
2. Call compute_risk_metrics to calculate DTI, EMI, and credit band.
3. Call lookup_policy_rule if you need to clarify a specific rule.
4. Based on tool results, produce your final decision.

FINAL RESPONSE FORMAT (use exactly this structure):
DECISION: [APPROVED / DECLINED / MANUAL_REVIEW]
REASON: [2-3 sentence explanation citing specific numbers from tool results]
KEY METRICS:
  - Credit Score: [score] ([band])
  - DTI Ratio: [%]
  - Estimated EMI: $[amount]
CONDITIONS: [any conditions, or "None" if clean approval]

Rules:
- DECLINED if any auto-decline flag is triggered.
- MANUAL_REVIEW if DTI is 37-43% or credit score is 580-619.
- APPROVED otherwise with appropriate conditions.
- Never approve if validation failed.
"""


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_agent(application: dict, config: AgentConfig) -> AgentRunResult:
    """Run the LangGraph ReAct agent on a single loan application.

    Args:
        application: Dict with all application fields.
        config:      AgentConfig (model, temperature).

    Returns:
        AgentRunResult with step trace and structured decision.
    """
    import json

    llm = ChatOllama(model=config.llm_model, temperature=config.temperature)
    agent = create_react_agent(llm, AGENT_TOOLS, prompt=_SYSTEM_PROMPT)

    user_message = (
        "Please evaluate the following loan application:\n\n"
        + json.dumps(application, indent=2)
    )

    result = agent.invoke({"messages": [HumanMessage(content=user_message)]})

    # Parse message history into steps
    messages = result["messages"]
    steps: list[AgentStep] = []
    pending_tool_calls: dict[str, tuple[str, str]] = {}  # call_id → (tool_name, input)

    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                pending_tool_calls[tc["id"]] = (tc["name"], str(tc["args"]))
        elif isinstance(msg, ToolMessage):
            if msg.tool_call_id in pending_tool_calls:
                tool_name, tool_input = pending_tool_calls.pop(msg.tool_call_id)
                steps.append(AgentStep(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_output=msg.content,
                ))

    # Extract final answer (last AIMessage with no tool calls)
    final_answer = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            final_answer = msg.content
            break

    decision = _extract_decision(final_answer)

    return AgentRunResult(
        application=application,
        steps=steps,
        final_answer=final_answer,
        decision=decision,
    )


def _extract_decision(text: str) -> str:
    """Parse DECISION: line from the agent's final response."""
    for line in text.splitlines():
        stripped = line.strip().upper()
        if stripped.startswith("DECISION:"):
            rest = stripped.replace("DECISION:", "").strip()
            if "APPROVED" in rest:
                return "APPROVED"
            if "DECLINED" in rest:
                return "DECLINED"
            if "MANUAL" in rest or "REVIEW" in rest:
                return "MANUAL_REVIEW"
    return "UNKNOWN"
