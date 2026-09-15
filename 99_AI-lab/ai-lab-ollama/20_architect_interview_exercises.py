"""
20_architect_interview_exercises.py - System Design Interview Exercises
========================================================================
Practice problems for architect-level understanding

MUST REMEMBER:
✓ Design for scale
✓ Consider trade-offs
✓ Plan for failures
✓ Optimize costs

EXERCISE FORMAT:
1. Problem statement
2. Constraints
3. Design approach
4. Implementation sketch
"""


class InterviewExercises:
    """Collection of system design exercises"""

    @staticmethod
    def exercise_1_rag_at_scale():
        """
        EXERCISE 1: Design a RAG system for 1B documents

        CONSTRAINTS:
        - 1 billion documents (1TB uncompressed)
        - 10k queries/second
        - <500ms latency (p95)
        - $100k/month budget

        DESIGN APPROACH:
        1. Chunking: Fixed 512-token chunks with 10% overlap
        2. Embeddings: Use dimension reduction (512 → 128)
        3. Vector DB: Distributed Pinecone (sharded by doc_id)
        4. Retrieval: Two-stage (BM25 + vector search)
        5. Caching: Redis for hot queries (80/20 rule)
        6. Scaling: Multi-region for latency

        IMPLEMENTATION SKETCH:
        """
        print("=" * 60)
        print("EXERCISE 1: RAG System at Scale (1B documents)")
        print("=" * 60)

        design = {
            "components": {
                "ingestion": {
                    "chunking": "Fixed 512 tokens, 10% overlap",
                    "embeddings": "Dimension: 128 (reduced from 768)",
                    "vector_db": "Pinecone (sharded)"
                },
                "retrieval": {
                    "stage_1": "BM25 on sparse index (top-100)",
                    "stage_2": "Vector search (top-10)",
                    "reranking": "Cross-encoder for top-3"
                },
                "caching": {
                    "layer_1": "Redis (hot queries, 24h TTL)",
                    "layer_2": "CDN for common contexts"
                },
                "scaling": {
                    "regions": 3,
                    "replicas": 3,
                    "load_balancer": "Round-robin"
                }
            },
            "metrics": {
                "latency_p95": "<500ms",
                "throughput": "10k queries/sec",
                "cost": "$100k/month"
            }
        }

        print("\n🏗️  DESIGN COMPONENTS:")
        for component, details in design["components"].items():
            print(f"\n{component.upper()}:")
            for key, value in details.items():
                print(f"   - {key}: {value}")

        print("\n" + "=" * 60)

    @staticmethod
    def exercise_2_multi_agent_reliability():
        """
        EXERCISE 2: Multi-Agent System with 99.99% uptime

        CONSTRAINTS:
        - 1000 agents
        - 99.99% uptime (52 min/year downtime)
        - Sub-second agent-to-agent communication
        - Graceful degradation

        DESIGN APPROACH:
        1. Health monitoring: Heartbeat every 5s
        2. Consensus: Raft for leader election
        3. Communication: Message queue (Kafka)
        4. Replication: 3x replication for state
        5. Recovery: Automatic restart with backoff
        6. Monitoring: Prometheus + Grafana
        """
        print("\n" + "=" * 60)
        print("EXERCISE 2: Multi-Agent 99.99% Reliability")
        print("=" * 60)

        design = {
            "reliability": {
                "health_checks": "Heartbeat every 5s (timeout 15s)",
                "consensus": "Raft for state consistency",
                "replication": "3x replication, quorum writes",
                "recovery": "Auto-restart with exponential backoff"
            },
            "communication": {
                "protocol": "gRPC (protobuf)",
                "queue": "Kafka (durable)",
                "latency": "<100ms p99"
            },
            "monitoring": {
                "metrics": "Prometheus",
                "alerts": "Critical on >2 agent failures",
                "dashboard": "Grafana real-time"
            }
        }

        print("\n🔧 RELIABILITY DESIGN:")
        for aspect, details in design.items():
            print(f"\n{aspect.upper()}:")
            for key, value in details.items():
                print(f"   - {key}: {value}")

        print("\n" + "=" * 60)

    @staticmethod
    def exercise_3_genai_platform():
        """
        EXERCISE 3: Production GenAI Platform (Startup)

        CONSTRAINTS:
        - $2M first-year budget
        - 100k users
        - MVP in 3 months
        - Scale to 1M users

        DESIGN APPROACH:
        1. Use managed services (Anthropic API)
        2. Serverless (Lambda + Step Functions)
        3. Postgres + Redis (managed)
        4. Monitor with DataDog
        5. Auto-scaling based on load
        """
        print("\n" + "=" * 60)
        print("EXERCISE 3: Startup GenAI Platform ($2M Budget)")
        print("=" * 60)

        design = {
            "phase_1_mvp": {
                "llm_api": "Anthropic Claude (managed)",
                "backend": "Lambda (Python/Node)",
                "database": "RDS Postgres + ElastiCache",
                "frontend": "React + Vercel",
                "time_to_market": "8 weeks"
            },
            "phase_2_scale": {
                "storage": "S3 for documents",
                "vector_db": "Pinecone (managed)",
                "message_queue": "SQS",
                "monitoring": "CloudWatch + DataDog",
                "target_users": "1M"
            },
            "cost_breakdown": {
                "api_calls": "$600k/year",
                "compute": "$500k/year",
                "storage_db": "$200k/year",
                "monitoring_other": "$200k/year"
            }
        }

        print("\n💰 COST-EFFECTIVE DESIGN:")
        for phase, details in design.items():
            print(f"\n{phase.upper()}:")
            for key, value in details.items():
                print(f"   - {key}: {value}")

        print("\n" + "=" * 60)

    @staticmethod
    def exercise_4_tradeoffs():
        """
        EXERCISE 4: Design Trade-offs

        COMMON TRADE-OFFS:
        1. Latency vs Cost
           - Fast: In-memory caching everywhere ($$$)
           - Cheap: Batch processing (slow)
           - Balance: Tiered caching + batch optimization

        2. Consistency vs Availability
           - Consistent: Synchronous writes (slow)
           - Available: Eventual consistency (complex)
           - Balance: Quorum writes + async replication

        3. Generality vs Specificity
           - General: Works for any query (slow/expensive)
           - Specific: Optimized for common cases (less flexible)
           - Balance: Specialize common paths, fallback for general

        4. Complexity vs Maintainability
           - Simple: Monolith (easier to debug)
           - Complex: Microservices (better scalability)
           - Balance: Start simple, migrate as needed
        """
        print("\n" + "=" * 60)
        print("EXERCISE 4: Design Trade-offs")
        print("=" * 60)

        tradeoffs = {
            "latency_vs_cost": {
                "fast": "In-memory caching everywhere ($$$)",
                "cheap": "Batch processing only (slow)",
                "balanced": "Tiered caching + optimization"
            },
            "consistency_vs_availability": {
                "consistent": "Sync writes (slower)",
                "available": "Eventual consistency (complex)",
                "balanced": "Quorum writes + async"
            },
            "generality_vs_specificity": {
                "general": "Works for any case (slow)",
                "specific": "Optimized for common (inflexible)",
                "balanced": "Specialize common + fallback"
            },
            "complexity_vs_maintainability": {
                "simple": "Monolith (debug-friendly)",
                "complex": "Microservices (scalable)",
                "balanced": "Start simple, scale when needed"
            }
        }

        print("\n⚖️  TRADE-OFF ANALYSIS:")
        for category, options in tradeoffs.items():
            print(f"\n{category.upper()}:")
            for approach, description in options.items():
                print(f"   - {approach}: {description}")

        print("\n" + "=" * 60)


def main():
    print("=" * 60)
    print("20: ARCHITECT-LEVEL INTERVIEW EXERCISES")
    print("=" * 60)

    exercises = InterviewExercises()

    # Run all exercises
    exercises.exercise_1_rag_at_scale()
    exercises.exercise_2_multi_agent_reliability()
    exercises.exercise_3_genai_platform()
    exercises.exercise_4_tradeoffs()

    print("\n" + "=" * 60)
    print("✅ INTERVIEW PREPARATION CHECKLIST:")
    print("=" * 60)
    print("""
BEFORE INTERVIEW:
✓ Understand all 20 modules deeply
✓ Practice explaining each component
✓ Know trade-offs by heart
✓ Think about failure modes
✓ Calculate rough costs/metrics

DURING INTERVIEW:
✓ Ask clarifying questions first
✓ Define constraints clearly
✓ Start with simple design
✓ Add complexity incrementally
✓ Discuss trade-offs openly
✓ Draw diagrams
✓ Handle follow-ups (scaling, failures)

COMMON QUESTIONS:
- "How would you scale this to 10x users?"
- "What happens if component X fails?"
- "How do you monitor/alert?"
- "What would you optimize first?"
- "How much would this cost?"
- "What's the trade-off between A and B?"

STRONG ANSWERS INCLUDE:
✓ Specific numbers (latency, throughput, cost)
✓ Multiple solutions with trade-offs
✓ Failure mode thinking
✓ Monitoring/observability
✓ Cost awareness
✓ References to real systems
✓ Willingness to learn

WEAK ANSWERS:
✗ "I don't know"
✗ "It depends" (without explaining what)
✗ Ignoring scale/failure
✗ Over-engineering for MVP
✗ Missing monitoring
✗ No cost considerations
    """)


if __name__ == "__main__":
    main()
