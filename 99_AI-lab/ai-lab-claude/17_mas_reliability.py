"""
17_mas_reliability.py - Multi-Agent Reliability (Fault Tolerance)
==================================================================
MUST REMEMBER:
✓ Health checks: monitor agent status
✓ Recovery: restart failed agents
✓ Leader election: handle failures
✓ Heartbeat: detect dead agents

KEY: Health monitoring, agent recovery, fault tolerance
"""

import time


class HealthMonitor:
    """Monitor health of agents"""

    def __init__(self):
        self.agent_health = {}
        self.last_heartbeat = {}

    def heartbeat(self, agent_id: str) -> None:
        """Record heartbeat from agent"""
        self.agent_health[agent_id] = "healthy"
        self.last_heartbeat[agent_id] = time.time()

    def check_health(self, timeout: float = 5.0) -> dict:
        """Check which agents are alive"""
        current_time = time.time()
        health_status = {}

        for agent_id, last_beat in self.last_heartbeat.items():
            if current_time - last_beat > timeout:
                health_status[agent_id] = "dead"
            else:
                health_status[agent_id] = "alive"

        return health_status

    def get_status(self) -> dict:
        """Get all agent statuses"""
        return {
            "health": self.agent_health.copy(),
            "heartbeats": self.last_heartbeat.copy()
        }


class ResilientMASAgent:
    """Resilient agent with recovery"""

    def __init__(self, agent_id: str, health_monitor: HealthMonitor):
        self.agent_id = agent_id
        self.health_monitor = health_monitor
        self.retry_count = 0
        self.max_retries = 3

    def execute_with_recovery(self, task: str) -> str:
        """Execute with automatic recovery"""
        print(f"🤖 {self.agent_id}: Executing {task}")

        for attempt in range(self.max_retries):
            try:
                # MUST REMEMBER: Send heartbeat
                self.health_monitor.heartbeat(self.agent_id)

                # Simulate work
                if attempt == 1:  # Simulated failure
                    raise Exception("Temporary failure")

                print(f"   ✅ Success")
                return f"Completed: {task}"

            except Exception as e:
                print(f"   ⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(0.5)
                else:
                    print(f"   ❌ Max retries exceeded")
                    raise

        return "Failed"


class ReliableMultiAgentSystem:
    """MAS with fault tolerance"""

    def __init__(self, num_agents: int = 3):
        self.health_monitor = HealthMonitor()
        self.agents = [
            ResilientMASAgent(f"Agent-{i}", self.health_monitor)
            for i in range(num_agents)
        ]

    def run_with_health_checks(self) -> None:
        """Run system with health monitoring"""
        print("🚀 Reliable Multi-Agent System")
        print("=" * 60)

        # Initial heartbeats
        print("\n📝 Starting agents...")
        for agent in self.agents:
            self.health_monitor.heartbeat(agent.agent_id)

        # Execute tasks
        print("\n📝 Executing tasks...")
        for i, agent in enumerate(self.agents):
            try:
                result = agent.execute_with_recovery(f"task-{i}")
            except Exception as e:
                print(f"   ❌ {agent.agent_id} failed: {e}")

        # Health check
        print("\n📊 Health Status:")
        health = self.health_monitor.check_health()
        for agent_id, status in health.items():
            print(f"   {agent_id}: {status}")


def main():
    print("=" * 60)
    print("17: MAS RELIABILITY")
    print("=" * 60)

    mas = ReliableMultiAgentSystem(num_agents=3)
    mas.run_with_health_checks()

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. HEALTH MONITORING:
   - Heartbeat detection
   - Timeout thresholds
   - Status reporting

2. AGENT RECOVERY:
   - Automatic restart
   - Backoff strategy
   - Graceful degradation

3. FAILURE MODES:
   - Transient: retry
   - Permanent: remove agent
   - Partial: degraded mode

4. ORCHESTRATION:
   - Leader election
   - Work reassignment
   - Load rebalancing

5. MONITORING:
   - Alert on failures
   - Track recovery metrics
   - Log all events
    """)


if __name__ == "__main__":
    main()
