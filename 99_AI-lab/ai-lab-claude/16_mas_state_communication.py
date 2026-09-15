"""
16_mas_state_communication.py - Multi-Agent State + Message Passing
===================================================================
MUST REMEMBER:
✓ Shared state: agents access common data
✓ Message queue: asynchronous communication
✓ Synchronization: locks/semaphores
✓ Consensus: distributed decision-making

KEY: Shared state, message passing, consensus
"""

from collections import deque
import json


class SharedState:
    """Shared state for multi-agent system"""

    def __init__(self):
        self.state = {}
        self.version = 0

    def get(self, key: str):
        """Get state value"""
        return self.state.get(key)

    def set(self, key: str, value):
        """Set state value"""
        self.state[key] = value
        self.version += 1

    def update(self, updates: dict):
        """Batch update"""
        self.state.update(updates)
        self.version += 1


class MessageQueue:
    """Message queue for agent communication"""

    def __init__(self):
        self.queues = {}

    def send(self, sender: str, recipient: str, message: dict) -> None:
        """Send message from agent to agent"""
        if recipient not in self.queues:
            self.queues[recipient] = deque()

        message["sender"] = sender
        self.queues[recipient].append(message)

    def receive(self, agent_id: str) -> dict:
        """Receive message (blocking)"""
        if agent_id in self.queues and self.queues[agent_id]:
            return self.queues[agent_id].popleft()
        return None

    def broadcast(self, sender: str, message: dict, recipients: list) -> None:
        """Broadcast to multiple agents"""
        for recipient in recipients:
            self.send(sender, recipient, message)


class MASAgent:
    """Agent in multi-agent system"""

    def __init__(self, agent_id: str, shared_state: SharedState, msg_queue: MessageQueue):
        self.agent_id = agent_id
        self.shared_state = shared_state
        self.msg_queue = msg_queue
        self.local_state = {}

    def act(self, action: str) -> None:
        """Perform action and share state"""
        print(f"🤖 {self.agent_id}: {action}")

        # Update shared state
        self.shared_state.set(f"{self.agent_id}_last_action", action)

        # Send message to other agents
        self.msg_queue.broadcast(
            self.agent_id,
            {"action": action, "timestamp": str(__import__('datetime').datetime.now())},
            [f"Agent-{i}" for i in range(1, 3) if f"Agent-{i}" != self.agent_id]
        )

    def receive_messages(self) -> list:
        """Receive and process messages"""
        messages = []
        while True:
            msg = self.msg_queue.receive(self.agent_id)
            if not msg:
                break
            messages.append(msg)

        if messages:
            print(f"📨 {self.agent_id} received {len(messages)} messages")

        return messages


class MultiAgentSystem:
    """Complete multi-agent system"""

    def __init__(self, num_agents: int = 3):
        self.shared_state = SharedState()
        self.msg_queue = MessageQueue()
        self.agents = [
            MASAgent(f"Agent-{i}", self.shared_state, self.msg_queue)
            for i in range(num_agents)
        ]

    def run(self) -> None:
        """Run multi-agent system"""
        print("🚀 Starting Multi-Agent System")
        print("=" * 60)

        # Round 1: Each agent acts
        print("\n📝 Round 1: Agents act independently")
        for i, agent in enumerate(self.agents):
            agent.act(f"performing task {i}")

        # Round 2: Agents receive messages
        print("\n📝 Round 2: Agents communicate")
        for agent in self.agents:
            agent.receive_messages()

        # Show shared state
        print(f"\n📊 Shared State (v{self.shared_state.version}):")
        for k, v in self.shared_state.state.items():
            print(f"   {k}: {v}")


def main():
    print("=" * 60)
    print("16: MAS STATE + COMMUNICATION")
    print("=" * 60)

    mas = MultiAgentSystem(num_agents=3)
    mas.run()

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. SHARED STATE:
   - Central store for common data
   - Version tracking for consistency
   - Atomic updates

2. MESSAGE PASSING:
   - Asynchronous communication
   - Queue per agent
   - Broadcast capability

3. SYNCHRONIZATION:
   - Locks for shared resources
   - Barriers for coordination
   - Timeouts for deadlock prevention

4. CONSENSUS:
   - Voting mechanisms
   - Byzantine fault tolerance
   - Conflict resolution
    """)


if __name__ == "__main__":
    main()
