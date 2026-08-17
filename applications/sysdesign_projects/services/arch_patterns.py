"""Architecture pattern selector — rule-based."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ArchRequirements:
    expected_rps: float             # requests per second
    avg_latency_budget_ms: float    # maximum acceptable latency
    need_global_distribution: bool  # multi-region / CDN needed
    data_volume_gb: float           # total knowledge base size
    multi_tenant: bool              # serving multiple orgs
    compliance_required: bool       # HIPAA / GDPR / SOC2
    budget_tier: str                # "startup", "growth", "enterprise"


@dataclass
class ArchComponent:
    name: str
    purpose: str
    examples: list[str]
    cost_tier: str  # "free", "low", "medium", "high"


@dataclass
class ArchPattern:
    name: str
    description: str
    diagram: str            # ASCII art / description
    components: list[ArchComponent]
    pros: list[str]
    cons: list[str]
    best_for: str
    rps_range: str
    estimated_cost: str     # monthly ballpark


PATTERNS = {
    "single_server": ArchPattern(
        name="Single Server",
        description="One FastAPI server with ChromaDB in-memory. Good for prototypes.",
        diagram="Client → FastAPI + ChromaDB (in-memory) → Groq API",
        components=[
            ArchComponent("FastAPI", "Serve requests", ["uvicorn"], "free"),
            ArchComponent("ChromaDB in-memory", "Vector search", ["chromadb"], "free"),
            ArchComponent("Groq API", "LLM inference", ["langchain-groq"], "free tier"),
        ],
        pros=["Simple setup", "Zero infrastructure cost", "Easy to debug"],
        cons=["Single point of failure", "No persistence", "Can't scale beyond 1 server"],
        best_for="Prototypes, demos, development",
        rps_range="1–5 RPS",
        estimated_cost="$0–50/month",
    ),
    "load_balanced": ArchPattern(
        name="Load-Balanced + Persistent Store",
        description="Multiple API replicas behind a load balancer. Persistent vector DB.",
        diagram="Client → Load Balancer → [API1, API2, API3] → Pinecone/Weaviate + Redis Cache → Groq",
        components=[
            ArchComponent("Load Balancer", "Distribute traffic", ["nginx", "AWS ALB"], "low"),
            ArchComponent("API Replicas", "Stateless request handlers", ["FastAPI x3"], "low"),
            ArchComponent("Pinecone / Weaviate", "Persistent vector search", ["pinecone-client"], "medium"),
            ArchComponent("Redis", "Semantic cache + session", ["redis", "upstash"], "low"),
            ArchComponent("Groq API", "LLM inference", ["langchain-groq"], "free/paid"),
        ],
        pros=["Horizontal scaling", "Persistent knowledge base", "Cache reduces LLM cost"],
        cons=["More infrastructure", "Operational overhead", "Higher monthly cost"],
        best_for="Production apps, 10–100 RPS, stable knowledge base",
        rps_range="10–100 RPS",
        estimated_cost="$200–800/month",
    ),
    "async_queue": ArchPattern(
        name="Async Queue + Worker Pool",
        description="Decouple request intake from LLM processing using a message queue.",
        diagram="Client → API Gateway → Queue (Celery/SQS) → Worker Pool → Vector DB + LLM → Webhook/WebSocket",
        components=[
            ArchComponent("API Gateway", "Accept requests, return job ID", ["FastAPI"], "low"),
            ArchComponent("Message Queue", "Decouple intake from processing", ["Celery+Redis", "AWS SQS"], "low"),
            ArchComponent("Worker Pool", "Process LLM tasks asynchronously", ["Celery workers"], "medium"),
            ArchComponent("WebSocket / Webhook", "Notify client when done", ["websockets"], "low"),
        ],
        pros=["Handles traffic spikes gracefully", "No request timeouts", "Workers auto-scale"],
        cons=["Adds latency (async by nature)", "More complex client integration", "Harder to debug"],
        best_for="Batch processing, long-running LLM jobs, unpredictable traffic",
        rps_range="Any (decoupled)",
        estimated_cost="$300–1200/month",
    ),
    "global_cdn": ArchPattern(
        name="Global CDN + Multi-Region",
        description="Edge caching + geo-distributed API deployments for global users.",
        diagram="User (US) → CDN Edge → US API → Pinecone\nUser (EU) → CDN Edge → EU API → Pinecone (EU replica)",
        components=[
            ArchComponent("CDN (Cloudflare)", "Cache static + semi-static responses at edge", ["cloudflare"], "low"),
            ArchComponent("Multi-region API", "Reduce latency for global users", ["Fly.io", "Railway"], "medium"),
            ArchComponent("Vector DB replication", "Regional read replicas", ["Pinecone serverless"], "high"),
            ArchComponent("Global Redis", "Shared cache across regions", ["Upstash Global"], "medium"),
        ],
        pros=["< 100ms for cached responses globally", "High availability", "GDPR data residency"],
        cons=["Complex deployment", "High cost", "Data consistency challenges"],
        best_for="Enterprise, global user base, compliance requirements",
        rps_range="1000+ RPS",
        estimated_cost="$2000+/month",
    ),
}


def get_pattern_recommendation(req: ArchRequirements) -> tuple[ArchPattern, list[str]]:
    """Return recommended pattern + reasoning list."""
    reasons = []

    if req.expected_rps < 5 and not req.compliance_required:
        reasons.append(f"Low RPS ({req.expected_rps:.0f}) — single server is sufficient")
        return PATTERNS["single_server"], reasons

    if req.need_global_distribution or req.expected_rps > 500:
        reasons.append("Global distribution or high RPS requires CDN + multi-region")
        return PATTERNS["global_cdn"], reasons

    if req.expected_rps > 50 or req.avg_latency_budget_ms < 500:
        reasons.append(f"RPS={req.expected_rps:.0f} requires horizontal scaling")
        if req.avg_latency_budget_ms < 300:
            reasons.append(
                "Tight latency budget → async queue would add delay, use load-balanced instead"
            )
        return PATTERNS["load_balanced"], reasons

    if req.budget_tier == "startup" and not req.compliance_required:
        reasons.append("Startup budget + moderate RPS → load-balanced is the right step up")
        return PATTERNS["load_balanced"], reasons

    reasons.append(f"Moderate RPS ({req.expected_rps:.0f}) with standard requirements")
    return PATTERNS["load_balanced"], reasons
