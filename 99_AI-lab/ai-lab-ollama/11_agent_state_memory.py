"""
11_agent_state_memory.py - Agent State Management + Memory
===========================================================
MUST REMEMBER:
✓ State: maintain context across interactions
✓ Memory: long-term knowledge (persist)
✓ Conversation: short-term context (temporary)
✓ Summarization: compress long conversations

KEY: State persistence, memory management, context windows
"""

from anthropic import Anthropic
import json
from datetime import datetime

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class AgentMemory:
    """Agent memory system (long-term storage)"""

    def __init__(self):
        self.facts = {}  # Persistent facts
        self.interactions = []  # History
        self.max_history = 100

    def add_fact(self, key: str, value: str) -> None:
        """Store persistent fact"""
        self.facts[key] = {"value": value, "timestamp": datetime.now().isoformat()}

    def recall_fact(self, key: str):
        """Retrieve persistent fact"""
        return self.facts.get(key, {}).get("value")

    def add_interaction(self, query: str, response: str) -> None:
        """Store interaction"""
        self.interactions.append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

        # MUST REMEMBER: Bound memory size
        if len(self.interactions) > self.max_history:
            self.interactions = self.interactions[-self.max_history:]

    def get_context(self, n: int = 5) -> str:
        """Get recent interactions for context"""
        recent = self.interactions[-n:]
        return "\n".join([
            f"Q: {i['query']}\nA: {i['response'][:100]}"
            for i in recent
        ])


class StatefulAgent:
    """Agent with state and memory management"""

    def __init__(self, name: str):
        self.name = name
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        self.memory = AgentMemory()
        self.conversation_history = []
        self.state = {}  # Current session state

    def _build_context(self) -> str:
        """Build context from memory and state"""
        context_parts = []

        # Add facts
        if self.memory.facts:
            facts_str = "\n".join([
                f"- {k}: {v['value']}"
                for k, v in list(self.memory.facts.items())[-5:]
            ])
            context_parts.append(f"KNOWN FACTS:\n{facts_str}")

        # Add recent interactions
        if self.memory.interactions:
            context_parts.append(f"RECENT CONTEXT:\n{self.memory.get_context(3)}")

        # Add state
        if self.state:
            state_str = json.dumps(self.state, indent=2)
            context_parts.append(f"CURRENT STATE:\n{state_str}")

        return "\n".join(context_parts)

    def chat(self, user_message: str) -> str:
        """Chat with stateful agent"""
        print(f"\n💬 User: {user_message}")

        # MUST REMEMBER: Prepend context to message
        context = self._build_context()
        full_message = user_message

        if context:
            full_message = f"{context}\n\nUSER MESSAGE: {user_message}"

        self.conversation_history.append({
            "role": "user",
            "content": full_message
        })

        # Get response
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=self.conversation_history
        )

        agent_response = response.content[0].text

        # MUST REMEMBER: Store for memory
        self.conversation_history.append({
            "role": "assistant",
            "content": agent_response
        })

        self.memory.add_interaction(user_message, agent_response)

        print(f"🤖 Agent: {agent_response[:150]}...")
        return agent_response

    def remember_fact(self, key: str, value: str) -> None:
        """Agent remembers a fact"""
        self.memory.add_fact(key, value)
        print(f"✅ Remembered: {key} = {value}")

    def update_state(self, key: str, value) -> None:
        """Update agent state"""
        self.state[key] = value
        print(f"📍 State: {key} = {value}")


def main():
    print("=" * 60)
    print("11: AGENT STATE + MEMORY")
    print("=" * 60)

    agent = StatefulAgent(name="Assistant")

    # Example 1: Build up facts and state
    print("\n📝 Example 1: Building Memory and State")
    print("-" * 40)

    agent.remember_fact("user_name", "John")
    agent.remember_fact("preference", "technical_details")
    agent.update_state("conversation_topic", "machine_learning")
    agent.update_state("iteration_count", 1)

    # Example 2: Use context in chat
    print("\n📝 Example 2: Context-Aware Chat")
    print("-" * 40)

    response1 = agent.chat("Hi, what do you know about me?")

    # Example 3: State updates
    print("\n📝 Example 3: State Updates During Chat")
    print("-" * 40)

    agent.update_state("learning_level", "intermediate")
    response2 = agent.chat("Explain deep learning at my level")

    # Example 4: Memory persistence
    print("\n📝 Example 4: Memory Persistence")
    print("-" * 40)

    response3 = agent.chat("What have we discussed so far?")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. MEMORY TYPES:
   - Facts: persistent knowledge
   - Interactions: conversation history
   - State: current session variables

2. CONTEXT BUILDING:
   - Include relevant facts
   - Add recent interactions
   - Include current state
   - Limit context size (fits in window)

3. MEMORY MANAGEMENT:
   - Bound storage (max history)
   - Summarize long conversations
   - Archive old interactions
   - Persist to storage (file, DB)

4. STATE LIFECYCLE:
   - Initialize at session start
   - Update during interactions
   - Clear on session end
   - Sync with memory as needed
    """)


if __name__ == "__main__":
    main()
