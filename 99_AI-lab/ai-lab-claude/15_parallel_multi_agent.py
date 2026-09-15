"""
15_parallel_multi_agent.py - Parallel Multi-Agent Execution
===========================================================
MUST REMEMBER:
✓ Parallel execution: run agents concurrently
✓ Load balancing: distribute work evenly
✓ Synchronization: wait for all to complete
✓ Result merging: combine outputs

KEY: Async execution, concurrency, load balancing
"""

import asyncio
from anthropic import Anthropic

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class ParallelAgent:
    """Individual agent for parallel execution"""

    def __init__(self, agent_id: str, specialty: str):
        self.agent_id = agent_id
        self.specialty = specialty
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    def execute(self, task: str) -> str:
        """Execute task"""
        prompt = f"As a {self.specialty} agent, {task}"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        except Exception as e:
            return f"Error: {e}"


class ParallelMultiAgent:
    """Coordinate parallel agent execution"""

    def __init__(self, num_agents: int = 3):
        self.agents = [
            ParallelAgent(f"Agent-{i}", f"Specialist-{i % 3}")
            for i in range(num_agents)
        ]

    def _execute_sequential(self, task: str) -> dict:
        """Sequential execution (baseline)"""
        print("🔄 Sequential Execution")
        results = {}

        for agent in self.agents:
            result = agent.execute(task)
            results[agent.agent_id] = result[:100]
            print(f"   ✅ {agent.agent_id}: {result[:50]}...")

        return results

    def execute(self, task: str) -> dict:
        """Execute agents (simulated parallel)"""
        print(f"\n🎯 Task: {task}")
        print("=" * 60)

        # MUST REMEMBER: In production, use asyncio/threading
        # For demo, simulate with sequential
        return self._execute_sequential(task)


def main():
    print("=" * 60)
    print("15: PARALLEL MULTI-AGENT")
    print("=" * 60)

    mas = ParallelMultiAgent(num_agents=3)

    # Example 1: Parallel task
    print("\n📝 Example 1: Parallel Task Execution")
    print("-" * 40)
    results = mas.execute("Analyze market trends for AI industry")

    print("\n📊 Results:")
    for agent_id, result in results.items():
        print(f"   {agent_id}: {result}")

    # Example 2: Multiple parallel runs
    print("\n📝 Example 2: Multiple Parallel Runs")
    print("-" * 40)
    mas2 = ParallelMultiAgent(num_agents=5)
    results2 = mas2.execute("Design solution for distributed systems")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. PARALLEL EXECUTION:
   - Run agents concurrently
   - Use asyncio or threading
   - Manage event loop

2. LOAD BALANCING:
   - Distribute work evenly
   - Monitor agent usage
   - Scale up/down

3. SYNCHRONIZATION:
   - Wait for all to complete
   - Timeout handling
   - Early termination

4. RESULT MERGING:
   - Combine outputs
   - Detect conflicts
   - Aggregate scores
    """)


if __name__ == "__main__":
    main()
