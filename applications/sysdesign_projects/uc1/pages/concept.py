"""UC1 — Concept: What is a Latency Budget and why it matters."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Latency Budget")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why 'my RAG app feels slow' is not a useful observation — you need a breakdown\n"
        "- The typical latency of each stage: network, embedding, vector search, LLM\n"
        "- Why LLM generation dominates — it's 75–80% of total end-to-end time\n"
        "- How streaming transforms perceived latency without changing actual generation time\n"
        "- What P50/P95/P99 SLA targets mean and why P99 is what users actually experience"
    )

    st.markdown(
        "A user clicks 'Send' in your chatbot. 1.6 seconds later, they get a response. "
        "That feels slow. You want to fix it — but *where* is the time being spent? "
        "Without a breakdown, every optimization is a guess.\n\n"
        "**A latency budget is a structured accounting of every millisecond** from the moment "
        "the client sends the request to the moment it receives a complete response. "
        "It tells you exactly which component to optimize first."
    )

    st.markdown("### The Lifecycle of a RAG Request")

    steps = [
        ("1️⃣ Network (in)", "20 ms", "The request travels from the client to your API server. "
         "Depends on geographic proximity. CDN edge nodes reduce this."),
        ("2️⃣ Query Embedding", "15 ms", "The user's question is passed through an embedding model "
         "(e.g. all-MiniLM-L6-v2) to produce a dense vector. Fast on GPU, ~15ms on CPU."),
        ("3️⃣ Vector Search", "30 ms", "The query vector is compared against all stored document "
         "vectors in your vector DB (ChromaDB, Pinecone). ANN algorithms make this fast even "
         "with millions of vectors."),
        ("4️⃣ (Optional) Reranking", "0–80 ms", "A cross-encoder reranker re-scores the top K results "
         "for higher precision. Adds latency but improves answer quality."),
        ("5️⃣ Context Preparation", "5 ms", "Retrieved chunks are formatted into the final prompt "
         "sent to the LLM. Mostly string operations — negligible time."),
        ("6️⃣ LLM Time-to-First-Token (TTFT)", "250–350 ms", "The time from sending the prompt until "
         "the first token is generated. This is the model's 'thinking time'. "
         "With streaming ON, this is what the user sees first."),
        ("7️⃣ LLM Generation", "800–1200 ms", "The remaining tokens are generated one-by-one. "
         "For a 200-token response at 150 tok/s, this takes ~1300ms. "
         "This is usually the largest single component."),
        ("8️⃣ Post-processing", "10 ms", "Parse the LLM response, apply formatting, validate output. "
         "Usually negligible."),
        ("9️⃣ Network (out)", "20 ms", "The complete response travels from server to client."),
    ]

    for stage, typical_time, explanation in steps:
        with st.container(border=True):
            col_s, col_t, col_e = st.columns([2, 1, 4])
            with col_s:
                st.markdown(f"**{stage}**")
            with col_t:
                st.markdown(f"`{typical_time}`")
            with col_e:
                st.write(explanation)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Typical Basic RAG — Total: ~1,600 ms**")
            st.markdown(
                "| Stage | ms |\n"
                "|---|---|\n"
                "| Network in | 20 |\n"
                "| Embedding | 15 |\n"
                "| Vector search | 30 |\n"
                "| Context prep | 5 |\n"
                "| LLM TTFT | 300 |\n"
                "| LLM Generation | 1,200 |\n"
                "| Post-process | 10 |\n"
                "| Network out | 20 |\n"
                "| **Total** | **1,600** |"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**The Key Insight: LLM dominates**")
            st.markdown(
                "Of the 1,600 ms total:\n\n"
                "- LLM (TTFT + generation): **1,500 ms = 93.8%**\n"
                "- Everything else: **100 ms = 6.2%**\n\n"
                "Optimization implication:\n"
                "- Optimizing embedding from 15ms → 5ms saves **0.6%** of latency\n"
                "- Switching to a faster LLM that generates at 300tok/s instead of 150tok/s "
                "saves **50%** of total latency\n\n"
                "**Always optimize the biggest slice first.**"
            )

    st.divider()
    st.markdown("### The Streaming Breakthrough")

    st.markdown(
        "The most impactful latency optimization requires zero code changes to your LLM pipeline."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**❌ Without Streaming**")
            st.markdown(
                "The server waits until every token is generated, *then* sends the full response.\n\n"
                "User experience: blank screen for 1,600 ms, then text appears all at once.\n\n"
                "**Perceived latency = 1,600 ms**"
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**✅ With Streaming**")
            st.markdown(
                "Tokens are sent to the client as they're generated. The user sees the first "
                "word after just ~300ms (TTFT), and the rest 'types itself'.\n\n"
                "Total generation time is identical — but the experience is completely different.\n\n"
                "**Perceived latency = 300 ms (TTFT)**"
            )

    st.success(
        "Streaming reduces perceived latency from ~1,600ms to ~300ms — **an 81% improvement** "
        "with zero changes to your model or infrastructure."
    )

    st.divider()
    st.markdown("### Production SLA Targets")

    st.markdown(
        "In production, you don't track average latency — you track **percentiles**. "
        "P99 latency is what your worst 1% of users experience, and it's what matters for SLAs."
    )

    st.table({
        "Percentile": ["P50 (median)", "P95", "P99"],
        "What it means": [
            "50% of requests are faster than this",
            "95% of requests are faster than this",
            "99% of requests are faster than this",
        ],
        "Target (streaming on)": ["< 400 ms TTFT", "< 700 ms TTFT", "< 1,200 ms TTFT"],
        "Why it matters": [
            "Typical user experience",
            "Most users have a good experience",
            "Only 1% of users see this — but they complain loudly",
        ],
    })

    st.markdown("### Cache as a Latency Optimizer")
    st.markdown(
        "A semantic cache transforms the latency budget entirely for repeat queries:\n\n"
        "- **Without cache:** ~1,600 ms end-to-end every time\n"
        "- **With cache hit:** ~5 ms (cache lookup only)\n\n"
        "A 30% cache hit rate means 30% of your requests return in 5ms instead of 1600ms — "
        "cutting average latency by ~28% with no infrastructure changes."
    )

    st.success(
        "**Next → Playground:** Use the sliders to build your own latency budget. "
        "Try different presets (simple chatbot vs enterprise RAG) and see the waterfall chart update."
    )
