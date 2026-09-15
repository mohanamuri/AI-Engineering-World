"""
14_supervisor_agent.py - Supervisor Agent (Coordinator Pattern)
===============================================================
MUST REMEMBER:
✓ Supervisor: coordinates multiple agents
✓ Task delegation: assign work to specialists
✓ Result aggregation: combine responses
✓ Orchestration: manage workflow

KEY: Coordinator pattern, task delegation, result aggregation
"""

from anthropic import Anthropic

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class SpecialistAgent:
    """Specialist agent for specific domain"""

    def __init__(self, specialty: str, description: str):
        self.specialty = specialty
        self.description = description
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    def process(self, task: str) -> str:
        """Process task in specialty"""
        prompt = f"You are a {self.specialty} specialist. {self.description}\n\nTask: {task}"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        except Exception as e:
            return f"Error: {e}"


class SupervisorAgent:
    """Supervisor that coordinates specialist agents"""

    def __init__(self):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

        # MUST REMEMBER: Create specialist agents
        self.specialists = {
            "data_scientist": SpecialistAgent(
                "Data Scientist",
                "Focus on data analysis, statistics, and ML models"
            ),
            "software_engineer": SpecialistAgent(
                "Software Engineer",
                "Focus on code quality, architecture, and best practices"
            ),
            "domain_expert": SpecialistAgent(
                "Domain Expert",
                "Focus on business context and real-world applications"
            )
        }

    def _parse_delegation(self, delegation_text: str) -> dict:
        """Parse LLM delegation to experts"""
        # Simulated: in real case, parse structured output
        result = {}

        if "data" in delegation_text.lower() or "analysis" in delegation_text.lower():
            result["data_scientist"] = delegation_text

        if "code" in delegation_text.lower() or "engineer" in delegation_text.lower():
            result["software_engineer"] = delegation_text

        if "business" in delegation_text.lower() or "domain" in delegation_text.lower():
            result["domain_expert"] = delegation_text

        return result if result else {"data_scientist": delegation_text}

    def supervise(self, task: str) -> str:
        """Supervise and delegate to specialists"""
        print(f"\n🎯 Task: {task}")
        print("=" * 60)

        # Step 1: Analyze task and create delegation plan
        print("\n📋 Step 1: Creating Delegation Plan")
        delegation_prompt = f"""
Analyze this task and decide which specialists to involve: {task}

List specialists needed: data_scientist, software_engineer, domain_expert
Return simple list of needed specialists.
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": delegation_prompt}]
            )

            delegation_plan = response.content[0].text
            specialists_needed = self._parse_delegation(delegation_plan)

            print(f"📍 Specialists needed: {list(specialists_needed.keys())}")

        except Exception as e:
            print(f"⚠️ Delegation planning failed: {e}")
            specialists_needed = {"data_scientist": task}

        # Step 2: Get specialist responses
        print("\n🔄 Step 2: Getting Specialist Responses")
        specialist_responses = {}

        for specialist_name, subtask in specialists_needed.items():
            if specialist_name in self.specialists:
                print(f"   → {specialist_name}: processing...")
                response = self.specialists[specialist_name].process(subtask)
                specialist_responses[specialist_name] = response[:200]

        # Step 3: Aggregate results
        print("\n📊 Step 3: Aggregating Results")
        aggregation_prompt = f"""
Synthesize these specialist responses into a coherent answer:

{json.dumps(specialist_responses, indent=2)}

Original task: {task}

Provide final synthesized response.
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": aggregation_prompt}]
            )

            final_response = response.content[0].text
            print(f"✅ Final Response: {final_response[:100]}...")
            return final_response

        except Exception as e:
            return f"Error aggregating results: {e}"


def main():
    print("=" * 60)
    print("14: SUPERVISOR AGENT (Multi-Agent Orchestration)")
    print("=" * 60)

    supervisor = SupervisorAgent()

    # Example 1: Complex task requiring multiple specialists
    print("\n📝 Example 1: Complex Task")
    print("-" * 40)
    task = "How should we build an ML system for customer churn prediction?"
    result = supervisor.supervise(task)

    # Example 2: Another task
    print("\n📝 Example 2: Another Task")
    print("-" * 40)
    supervisor2 = SupervisorAgent()
    task2 = "Design a data pipeline for real-time analytics"
    result2 = supervisor2.supervise(task2)

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. SUPERVISOR PATTERN:
   - Analyze task
   - Delegate to specialists
   - Aggregate results
   - Provide final answer

2. SPECIALIST AGENTS:
   - Deep expertise in domain
   - Focused responsibilities
   - Consistent interface
   - Clear success criteria

3. DELEGATION:
   - Analyze task requirements
   - Match to specialist strengths
   - Provide context
   - Handle failures

4. AGGREGATION:
   - Synthesize responses
   - Resolve conflicts
   - Ensure coherence
   - Add final insights

5. SCALABILITY:
   - Add more specialists
   - Dynamic delegation
   - Load balancing
   - Async execution
    """)

    import json


if __name__ == "__main__":
    main()
