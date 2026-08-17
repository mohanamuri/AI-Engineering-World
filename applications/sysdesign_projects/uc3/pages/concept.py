"""UC3 — Concept: Architecture tiers and when to use each."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Architecture Patterns for LLM Systems")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- The 4 tiers of LLM system architecture and when each is appropriate\n"
        "- Key decision factors: RPS, latency budget, traffic pattern, compliance, cost\n"
        "- The exact components in each tier and what they do\n"
        "- When to use async queues vs synchronous APIs\n"
        "- How architecture evolves as your product grows"
    )

    st.markdown(
        "A student asks: 'Should I use a load balancer or a message queue?' "
        "The answer is: *it depends*. On your traffic, your latency budget, your budget, "
        "and your traffic pattern.\n\n"
        "Architecture decisions are not about which technology is 'better' — they're about "
        "**matching the architecture to the requirements**. This app teaches you a framework "
        "for making that match."
    )

    st.divider()
    st.markdown("### The 4 Architecture Tiers")

    tiers = [
        {
            "tier": "Tier 1",
            "name": "Single Server",
            "rps": "1–5 RPS",
            "cost": "$0–50/month",
            "icon": "🖥️",
            "when": "Prototype, demo, personal project, development",
            "diagram": "Client → FastAPI + ChromaDB (in-memory) → Groq API",
            "components": [
                "**FastAPI** — serves all requests",
                "**ChromaDB in-memory** — vector store, dies on restart",
                "**Groq API** — LLM inference (free tier)",
            ],
            "pros": ["Zero infrastructure cost", "Simple to set up and debug", "No DevOps overhead"],
            "cons": ["Single point of failure", "No persistence (restart = data loss)", "Can't scale beyond 1 instance"],
        },
        {
            "tier": "Tier 2",
            "name": "Load-Balanced + Persistent Store",
            "rps": "10–100 RPS",
            "cost": "$200–800/month",
            "icon": "⚖️",
            "when": "Production app, stable knowledge base, growing user base",
            "diagram": "Client → Load Balancer (nginx/ALB) → [API1 | API2 | API3] → Pinecone + Redis → Groq",
            "components": [
                "**Load Balancer** — distributes traffic, health checks",
                "**Stateless API replicas** — each handles requests independently",
                "**Pinecone / Weaviate** — persistent vector DB, survives restarts",
                "**Redis** — semantic cache + session storage",
            ],
            "pros": ["Horizontal scaling", "Fault tolerant (lose 1 replica = still working)", "Cache reduces LLM cost"],
            "cons": ["More infrastructure to manage", "Sessions must be external (Redis, not in-process)", "$200+/month"],
        },
        {
            "tier": "Tier 3",
            "name": "Async Queue + Worker Pool",
            "rps": "Any (decoupled)",
            "cost": "$300–1200/month",
            "icon": "📬",
            "when": "Bursty traffic, long-running LLM jobs, batch processing",
            "diagram": "Client → API Gateway (returns job ID) → Queue (Celery/SQS) → Workers → Vector DB + LLM → WebSocket/Webhook",
            "components": [
                "**API Gateway** — accepts requests, returns job_id immediately",
                "**Message Queue** — decouples intake from processing (Celery + Redis, or SQS)",
                "**Worker Pool** — processes LLM jobs, scales independently",
                "**WebSocket / Webhook** — notifies client when job is complete",
            ],
            "pros": ["No request timeouts (async by nature)", "Workers absorb traffic spikes", "Workers auto-scale independently"],
            "cons": ["Adds inherent latency (polling overhead)", "More complex client integration", "Harder to debug failed jobs"],
        },
        {
            "tier": "Tier 4",
            "name": "Global CDN + Multi-Region",
            "rps": "1000+ RPS",
            "cost": "$2000+/month",
            "icon": "🌍",
            "when": "Enterprise, global user base, compliance requirements (GDPR, HIPAA)",
            "diagram": "User (US) → CDN Edge → US API → Pinecone\nUser (EU) → CDN Edge → EU API → Pinecone (EU replica)\nGlobal Redis (Upstash) shared cache",
            "components": [
                "**CDN (Cloudflare)** — caches responses at edge nodes, < 100ms for hits globally",
                "**Multi-region API** — deployed in US, EU, APAC to minimize RTT",
                "**Pinecone serverless** — regional read replicas for data residency",
                "**Upstash Global Redis** — shared cache across regions",
            ],
            "pros": ["< 100ms for cached responses globally", "99.99% availability SLA", "GDPR data residency"],
            "cons": ["Complex deployment and operations", "Data consistency across regions", "$2000+/month base cost"],
        },
    ]

    for tier in tiers:
        with st.expander(f"{tier['icon']} {tier['tier']}: {tier['name']} — {tier['rps']} | {tier['cost']}", expanded=False):
            col_when, col_diag = st.columns([1, 2])
            with col_when:
                st.markdown(f"**When to use:** {tier['when']}")
                st.markdown(f"**RPS target:** {tier['rps']}")
                st.markdown(f"**Monthly cost:** {tier['cost']}")
            with col_diag:
                st.code(tier["diagram"], language=None)

            st.markdown("**Components:**")
            for comp in tier["components"]:
                st.markdown(f"- {comp}")

            col_p, col_c = st.columns(2)
            with col_p:
                with st.container(border=True):
                    st.markdown("**Pros**")
                    for p in tier["pros"]:
                        st.markdown(f"- {p}")
            with col_c:
                with st.container(border=True):
                    st.markdown("**Cons**")
                    for c in tier["cons"]:
                        st.markdown(f"- {c}")

    st.divider()
    st.markdown("### The Decision Tree")

    st.markdown(
        """
        ```
        Expected RPS < 5 and no compliance?
            → Single Server (Tier 1)

        Global users needed OR RPS > 500?
            → Global CDN + Multi-Region (Tier 4)

        RPS > 50 OR latency budget < 500ms?
            → Load-Balanced (Tier 2)
            (tight latency budget rules out async queue)

        Traffic is bursty or jobs are long-running?
            → Async Queue (Tier 3)

        Otherwise (moderate RPS, standard requirements)?
            → Load-Balanced (Tier 2) — the default production choice
        ```
        """
    )

    st.divider()
    st.markdown("### Architecture Evolution Path")

    st.markdown(
        "Most products follow this evolution as they grow:\n\n"
        "1. **Month 1 (prototype):** Single server, ChromaDB in-memory, Groq free tier\n"
        "2. **Month 3 (early users):** Add persistent vector DB (Pinecone), basic load balancer\n"
        "3. **Month 6 (growing):** Add Redis cache, 3 replicas, proper monitoring\n"
        "4. **Year 1 (scale):** Async queue for batch jobs, autoscaling policies\n"
        "5. **Enterprise:** Multi-region, CDN, compliance certifications, SLAs\n\n"
        "**You do not start at Tier 4.** Over-engineering for scale you don't have costs "
        "money and slows you down. Start simple, measure, and scale when the data demands it."
    )

    st.success(
        "**Next → Playground:** Enter your requirements (RPS, latency budget, global users, compliance) "
        "and get an instant architecture recommendation with full component details."
    )
