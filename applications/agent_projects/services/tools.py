"""
Shared tool implementations for Agent Projects.

Three tools, zero extra packages — only stdlib + requests (already in requirements):

  CalculatorTool  — safe math eval using Python ast module
  WikipediaTool   — Wikipedia REST API via requests
  PythonREPLTool  — exec() with captured stdout/stderr

Each tool exposes:
  .name          str
  .description   str
  .run(input)    str  (always returns a string, never raises)
"""

from __future__ import annotations

import ast
import io
import operator
import sys
import textwrap
import traceback
from dataclasses import dataclass

import requests


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class ToolResult:
    """Returned by every tool run — always a string output, plus metadata."""
    tool_name: str
    tool_input: str
    tool_output: str
    success: bool = True


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------

_SAFE_OPERATORS = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.Pow:  operator.pow,
    ast.Mod:  operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported literal: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return _SAFE_OPERATORS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary op: {op_type.__name__}")
        return _SAFE_OPERATORS[op_type](_safe_eval(node.operand))
    raise ValueError(f"Unsupported AST node: {type(node).__name__}")


class CalculatorTool:
    name = "calculator"
    description = (
        "Evaluates a mathematical expression and returns the numeric result. "
        "Supports +, -, *, /, **, %, //. Input must be a plain math expression "
        "like '2 ** 10' or '(3.14 * 5 ** 2)'. Do NOT include units or text."
    )

    def run(self, expression: str) -> ToolResult:
        expr = expression.strip()
        try:
            tree = ast.parse(expr, mode="eval")
            value = _safe_eval(tree.body)
            output = str(value)
        except Exception as exc:
            output = f"Calculator error: {exc}"
            return ToolResult(tool_name=self.name, tool_input=expr,
                              tool_output=output, success=False)
        return ToolResult(tool_name=self.name, tool_input=expr, tool_output=output)


# ---------------------------------------------------------------------------
# Wikipedia
# ---------------------------------------------------------------------------

_WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
_WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
_TIMEOUT = 8  # seconds


class WikipediaTool:
    name = "wikipedia"
    description = (
        "Looks up factual information on Wikipedia. "
        "Input should be a short topic or search phrase (e.g. 'Python programming language' "
        "or 'Mount Everest'). Returns a concise summary paragraph."
    )

    def run(self, query: str) -> ToolResult:
        query = query.strip()
        try:
            # Step 1: Search for the best matching page title
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 1,
                "format": "json",
            }
            resp = requests.get(_WIKI_SEARCH_URL, params=params, timeout=_TIMEOUT)
            resp.raise_for_status()
            results = resp.json().get("query", {}).get("search", [])
            if not results:
                output = f"No Wikipedia article found for '{query}'."
                return ToolResult(tool_name=self.name, tool_input=query,
                                  tool_output=output, success=False)

            title = results[0]["title"]

            # Step 2: Fetch the summary for that title
            summary_url = _WIKI_SUMMARY_URL.format(
                title=requests.utils.quote(title, safe="")
            )
            resp2 = requests.get(summary_url, timeout=_TIMEOUT)
            resp2.raise_for_status()
            data = resp2.json()
            extract = data.get("extract", "").strip()
            if not extract:
                output = f"Wikipedia page '{title}' exists but has no summary."
                return ToolResult(tool_name=self.name, tool_input=query,
                                  tool_output=output, success=False)

            # Trim to ~600 chars so it's scannable
            if len(extract) > 600:
                extract = extract[:600].rsplit(" ", 1)[0] + "…"
            output = f"**{title}**\n\n{extract}"
        except requests.RequestException as exc:
            output = f"Wikipedia lookup failed: {exc}"
            return ToolResult(tool_name=self.name, tool_input=query,
                              tool_output=output, success=False)
        return ToolResult(tool_name=self.name, tool_input=query, tool_output=output)


# ---------------------------------------------------------------------------
# Python REPL
# ---------------------------------------------------------------------------

_REPL_TIMEOUT_MSG = "Execution timed out (5 s)."
_MAX_OUTPUT_CHARS = 2000


class PythonREPLTool:
    name = "python_repl"
    description = (
        "Executes a Python code snippet and returns stdout output. "
        "Use for data analysis, calculations, list processing, or any logic "
        "that benefits from running code. The snippet runs in an isolated "
        "namespace — import statements are supported. "
        "Always use print() to produce output."
    )

    def run(self, code: str) -> ToolResult:
        code = textwrap.dedent(code).strip()
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        namespace: dict = {}
        try:
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = stdout_capture, stderr_capture
            try:
                exec(compile(code, "<repl>", "exec"), namespace)  # noqa: S102
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

            stdout_val = stdout_capture.getvalue()
            stderr_val = stderr_capture.getvalue()
            output = stdout_val
            if stderr_val:
                output += (("\n" if output else "") + f"[stderr] {stderr_val}")
            if not output:
                output = "(no output)"
            if len(output) > _MAX_OUTPUT_CHARS:
                output = output[:_MAX_OUTPUT_CHARS] + "\n…[output truncated]"
            success = True
        except Exception:
            output = traceback.format_exc(limit=5)
            success = False

        return ToolResult(tool_name=self.name, tool_input=code,
                          tool_output=output, success=success)


# ---------------------------------------------------------------------------
# Registry — easy lookup by name
# ---------------------------------------------------------------------------

ALL_TOOLS: dict[str, CalculatorTool | WikipediaTool | PythonREPLTool] = {
    "calculator":   CalculatorTool(),
    "wikipedia":    WikipediaTool(),
    "python_repl":  PythonREPLTool(),
}
