"""UC3 — Insights: Interview Q&A and key takeaways for Architecture Patterns."""

import streamlit as st

from applications.sysdesign_projects.uc3.constants import ARCH_RESULT_KEY


def render() -> None:
    st.subheader("💡 Insights — Architecture Patterns")

    result = st.session_state.get(ARCH_RESULT_KEY)
    if result:
        pattern = result["pattern"]
        st.markdown(f"#### Your recommended pattern: {pattern.name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("RPS range", pattern.rps_range)
        c2.metric("Est. cost", pattern.estimated_cost)
        c3.metric("Components", str(len(pattern.components)))
        st.divider()

    st.markdown("#### Architecture Decision Matrix")

    st.table({
        "Pattern": ["Single Server", "Load-Balanced", "Async Queue", "Global CDN"],
        "RPS range": ["1–5", "10–100", "Any (decoupled)", "1000+"],
        "Latency type": ["Sync, fast", "Sync, fast", "Async (job-based)", "Sync + edge cache"],
        "State storage": ["In-process", "External (Redis)", "Queue + workers", "Distributed"],
        "Ops complexity": ["Very Low", "Medium", "High", "Very High"],
        "Min cost/month": ["$0", "~$200", "~$300", "~$2000"],
    })

    st.divider()

    st.markdown("#### 🎯 Interview Questions & Model Answers")
    st.caption("Common system design interview questions for LLM/ML engineering roles.")

    qa_pairs = [
        (
            "How do you design a stateless API for horizontal scaling?",
            "A stateless API stores no request-specific data in server memory between requests. "
            "Every request must contain everything the server needs, or the server must fetch state "
            "from a shared external store. For LLM RAG APIs: (1) **No in-process cache** — move "
            "the semantic cache to Redis so all replicas share it. (2) **No session objects** — "
            "store conversation history in Redis or a database keyed by session_id, passed by the "
            "client. (3) **No in-memory vector index** — connect to Pinecone or Weaviate. "
            "Statelessness enables load balancers to route any request to any replica, and replicas "
            "can be added or removed without data loss. Test it by asking: 'What breaks if we kill "
            "this server right now?' If the answer is 'nothing', it's stateless."
        ),
        (
            "Where does session storage go in a multi-replica API setup?",
            "Session state (conversation history, user preferences, in-progress job status) "
            "cannot live in API server memory when you have multiple replicas — the next request "
            "might hit a different server. Solutions: (1) **Redis** — fast, low-latency key-value "
            "store. Store session as JSON with TTL. Access from any replica in < 1ms. Best for "
            "conversation history and semantic cache. (2) **PostgreSQL / DynamoDB** — for "
            "persistent data that needs ACID guarantees (e.g., user accounts, billing state). "
            "(3) **Sticky sessions** — route the same user to the same server (via load balancer "
            "cookie). Simpler but breaks if that server restarts, so avoid for production. "
            "Redis is the right default for most LLM session state."
        ),
        (
            "When would you use an async message queue instead of a synchronous API for LLM calls?",
            "Use a queue when: (1) **LLM jobs take > 10 seconds** — HTTP connections time out, "
            "and the client must poll or receive a webhook. (2) **Traffic is bursty** — the queue "
            "absorbs spikes and workers process at a steady rate. (3) **You want to prioritize jobs** "
            "— queues support priority lanes (premium users jump the queue). (4) **Batch processing** "
            "— nightly document embedding, bulk report generation. Keep synchronous when: "
            "user is waiting for a response in real-time (chat), latency SLA is < 3 seconds, or "
            "your client (mobile app, browser) doesn't support polling/webhooks. "
            "The async pattern requires more client complexity: the API returns `{job_id}`, "
            "the client polls `/status/{job_id}` or awaits a webhook."
        ),
        (
            "How does data consistency work in a distributed RAG system?",
            "Distributed RAG has two consistency challenges: (1) **Vector DB consistency** — "
            "when you update the knowledge base (new docs, edits), replicas must sync. "
            "Pinecone and Weaviate handle this internally but with eventual consistency: "
            "a replica might briefly return stale results after an update. For most RAG apps "
            "this is acceptable; for compliance (e.g. policy updates), use strong consistency "
            "modes or route writes to a single primary. (2) **Cache invalidation** — when a "
            "document changes, cached answers based on it become stale. Solutions: "
            "(a) TTL — expire cache entries after N hours; (b) event-driven invalidation — "
            "when a document is updated, flush cache entries that reference it; (c) version tags — "
            "tag cache entries with document version, invalidate on version bump."
        ),
        (
            "How would you design disaster recovery for a production vector database?",
            "DR for vector DBs has three components: (1) **Backups** — export the vector index "
            "regularly. Pinecone supports collection snapshots; Weaviate has backup modules for S3. "
            "For ChromaDB: persist to disk (`persist_directory`) and back up the directory. "
            "RPO (recovery point objective) target: < 1 hour for most production systems. "
            "(2) **Replication** — Pinecone serverless auto-replicates; Weaviate supports "
            "multi-node replication. RTO (recovery time objective) target: < 15 minutes. "
            "(3) **Re-indexing pipeline** — maintain the original documents in S3/GCS so you can "
            "re-embed and rebuild the index from scratch if needed. This is your last resort but "
            "ensures you can recover from catastrophic index corruption. Test your DR plan: "
            "simulate a failure, restore from backup, verify search quality before declaring success."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs, 1):
        with st.expander(f"Q{i}: {question}"):
            st.markdown(answer)

    st.divider()
    st.markdown("#### 🔗 Connected Concepts")

    concepts = [
        ("CAP Theorem", "In distributed systems, you can have at most 2 of: Consistency, Availability, "
         "Partition tolerance. LLM APIs typically choose AP (available + partition tolerant) with "
         "eventual consistency. Vector DBs usually follow the same pattern."),
        ("Service Mesh (Istio, Linkerd)", "For enterprise deployments, a service mesh handles "
         "load balancing, mTLS (mutual TLS between services), circuit breaking, and observability "
         "at the infrastructure level — without changing your application code."),
        ("Blue/Green Deployments", "Deploy the new version alongside the old (blue = live, green = new). "
         "Switch traffic 10% → 50% → 100% while monitoring error rates. If green fails, "
         "instantly switch back to blue. Zero-downtime deployments for LLM API updates."),
        ("API Gateway vs Load Balancer", "A load balancer distributes traffic at Layer 4 (TCP) or "
         "Layer 7 (HTTP). An API gateway also handles auth (JWT), rate limiting, request transformation, "
         "and API versioning. Use both: API gateway for the public interface, load balancer behind it."),
        ("Twelve-Factor App", "The Twelve-Factor methodology (12factor.net) defines best practices "
         "for cloud-native apps: config via environment variables, stateless processes, disposable "
         "processes (fast start/stop), dev/prod parity. All four architecture tiers should follow "
         "twelve-factor principles."),
    ]

    for title, body in concepts:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.divider()
    st.success(
        "**UC4 → Cost Estimation:** Now that you've chosen an architecture, "
        "project your monthly cost: token costs, embeddings, infrastructure, and cache ROI."
    )
