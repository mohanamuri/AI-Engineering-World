"""
10_agent_tools.py - Agent with Tool Use
========================================
MUST REMEMBER:
✓ Tool definitions: name, description, input_schema
✓ Tool execution: safely call defined functions
✓ Error handling: LLM doesn't know actual capabilities
✓ Tool validation: check inputs before execution

KEY: Tool definition, execution, schema validation
"""

from anthropic import Anthropic
import json

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class ToolAgent:
    """Agent that can use defined tools"""

    def __init__(self):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        self.tools = self._define_tools()
        self.conversation_history = []

    def _define_tools(self):
        """Define available tools with schemas"""
        return [
            {
                "name": "calculator",
                "description": "Simple calculator for math operations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                            "description": "Math operation"
                        },
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["operation", "a", "b"]
                }
            },
            {
                "name": "search",
                "description": "Search for information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "database_query",
                "description": "Query a database",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "filter": {"type": "string", "description": "Where clause"}
                    },
                    "required": ["table"]
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute tool (simulated)"""
        if tool_name == "calculator":
            op = tool_input["operation"]
            a, b = tool_input["a"], tool_input["b"]

            if op == "add":
                result = a + b
            elif op == "subtract":
                result = a - b
            elif op == "multiply":
                result = a * b
            elif op == "divide":
                result = a / b if b != 0 else "Error: division by zero"
            else:
                result = "Unknown operation"

            return f"Result: {result}"

        elif tool_name == "search":
            query = tool_input["query"]
            return f"Search results for '{query}': Found 5 relevant results"

        elif tool_name == "database_query":
            table = tool_input["table"]
            return f"Query on '{table}': Retrieved 10 rows"

        else:
            return "Unknown tool"

    def run(self, task: str) -> str:
        """Run agent with tool use"""
        print(f"\n🎯 Task: {task}")

        self.conversation_history = [{
            "role": "user",
            "content": task
        }]

        for iteration in range(5):
            print(f"\n🔄 Iteration {iteration + 1}")

            # MUST REMEMBER: Send tools to LLM
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                tools=self.tools,
                messages=self.conversation_history
            )

            # Check for tool use
            if response.stop_reason == "tool_use":
                print("🔧 Tool use detected")

                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute all tool calls
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"   → Using: {block.name}")
                        result = self._execute_tool(block.name, block.input)
                        print(f"   → Result: {result[:50]}...")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                # Add tool results to conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

            else:
                # Agent finished (no tool use)
                final_response = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response = block.text
                        break

                print(f"✅ Agent response: {final_response[:100]}...")
                return final_response

        return "Completed"


def main():
    print("=" * 60)
    print("10: AGENT WITH TOOLS")
    print("=" * 60)

    agent = ToolAgent()

    # Example 1: Calculator tool
    print("\n📝 Example 1: Using Calculator")
    print("-" * 40)
    result = agent.run("What is 25 * 4?")

    # Example 2: Multiple tools
    print("\n📝 Example 2: Multiple Tools")
    print("-" * 40)
    agent2 = ToolAgent()
    result = agent2.run("Calculate 100 / 5 and search for machine learning")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. TOOL DEFINITION:
   - Name, description, input_schema
   - Schema must be valid JSON Schema
   - Clear descriptions help LLM choose tools

2. TOOL EXECUTION:
   - Validate inputs against schema
   - Handle errors gracefully
   - Return clear results

3. LOOP:
   - LLM reasons and calls tools
   - Execute tools, send results back
   - Repeat until stop_reason != "tool_use"

4. SAFETY:
   - Whitelist tools
   - Validate inputs
   - Limit execution time
   - Log all tool calls
    """)


if __name__ == "__main__":
    main()
