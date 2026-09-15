"""
09_basic_agent.py - Basic Agentic Loop (Think → Act → Observe)
==============================================================
MUST REMEMBER:
✓ Agent loop: Query → Reasoning → Action → Result → Loop
✓ State: maintain context across iterations
✓ Termination: stop when goal achieved
✓ Safety: validate actions before execution

KEY: Agentic loop, state management, action execution
"""

from anthropic import Anthropic

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class BasicAgent:
    """Simple agent with ReAct pattern: Reason, Act, Observe"""

    def __init__(self):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        self.conversation_history = []
        self.action_count = 0
        self.max_iterations = 5

    def _format_history(self) -> str:
        """Format conversation for context"""
        return "\n".join([
            f"{msg['role'].upper()}: {msg['content'][:100]}"
            for msg in self.conversation_history[-10:]
        ])

    def run(self, task: str) -> str:
        """Run agent loop until completion"""
        print(f"\n🎯 Task: {task}")
        print("=" * 60)

        self.conversation_history = [{
            "role": "user",
            "content": f"Help me with: {task}\n\nThink step by step. You can use actions like [ACTION: search], [ACTION: calculate], [ACTION: retrieve]"
        }]

        for iteration in range(self.max_iterations):
            print(f"\n🔄 Iteration {iteration + 1}/{self.max_iterations}")

            # MUST REMEMBER: Agent thinks
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=self.conversation_history
            )

            agent_response = response.content[0].text
            print(f"💭 Agent: {agent_response[:200]}...")

            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })

            # Check if agent wants to perform action
            if "[ACTION:" in agent_response:
                # MUST REMEMBER: Execute action (simulated)
                action = agent_response.split("[ACTION:")[1].split("]")[0]
                result = self._execute_action(action)
                print(f"⚙️  Action: {action} → {result}")

                self.conversation_history.append({
                    "role": "user",
                    "content": f"Action '{action}' result: {result}"
                })

            # Check termination
            if "DONE" in agent_response or "COMPLETE" in agent_response:
                print(f"\n✅ Agent completed task")
                return agent_response

        print(f"\n⚠️ Max iterations reached")
        return agent_response

    def _execute_action(self, action: str) -> str:
        """Simulate action execution"""
        actions = {
            "search": "Found results for your query",
            "calculate": "2 + 2 = 4",
            "retrieve": "Retrieved document from database"
        }

        for key, value in actions.items():
            if key in action.lower():
                return value

        return "Action executed"


def main():
    print("=" * 60)
    print("09: BASIC AGENT")
    print("=" * 60)

    agent = BasicAgent()

    # Example 1: Simple task
    print("\n📝 Example 1: Simple Task")
    print("-" * 40)
    result = agent.run("What is 2+2? Do a calculation action and confirm")

    # Example 2: Multi-step task
    print("\n\n📝 Example 2: Multi-Step Task")
    print("-" * 40)
    agent2 = BasicAgent()
    result = agent2.run("Search for information about machine learning")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. AGENT LOOP:
   1. Agent reasons about task
   2. Agent decides action
   3. Action executed
   4. Observe result
   5. Loop until DONE

2. TERMINATION:
   - Goal achieved
   - Max iterations reached
   - Agent says DONE/COMPLETE

3. SAFETY:
   - Validate actions before execution
   - Limit iterations
   - Whitelist allowed actions
   - Log all actions

4. STATE MANAGEMENT:
   - Keep conversation history
   - Include action results
   - Maintain task context
    """)


if __name__ == "__main__":
    main()
