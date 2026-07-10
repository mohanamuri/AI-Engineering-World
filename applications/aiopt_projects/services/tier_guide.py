"""Shared Tier Guide page — shown in every AI Optimisation UC."""

import streamlit as st


def render() -> None:
    st.subheader("📋 AI Optimisation Techniques — Series Guide")

    st.markdown(
        """
        This project covers **4 production patterns** that every LLM engineer should know.
        Each use case solves one specific problem you will face when building real AI applications.
        """
    )

    st.divider()
    st.markdown("### The 4 Patterns at a Glance")
    st.markdown("*Each row answers one of the most-asked LLM system design interview questions.*")

    rows = [
        {
            "uc": "UC1",
            "technique": "Semantic Caching",
            "concern": "Cost",
            "icon": "💰",
            "interview_q": "How do you reduce LLM API costs in production?",
            "one_line": "Embed queries → find similar cached answers → return instantly, no LLM call.",
        },
        {
            "uc": "UC2",
            "technique": "Model Routing",
            "concern": "Cost + Performance",
            "icon": "⚡",
            "interview_q": "How do you scale LLM systems without costs exploding?",
            "one_line": "Classify query complexity → route simple queries to a cheap model, hard ones to a powerful model.",
        },
        {
            "uc": "UC3",
            "technique": "Memory Patterns",
            "concern": "Memory",
            "icon": "🧠",
            "interview_q": "How do LLMs maintain context across a long conversation?",
            "one_line": "Choose the right strategy: keep last N messages, compress old ones, or track named facts.",
        },
        {
            "uc": "UC4",
            "technique": "Streaming + Fallback",
            "concern": "Performance + Reliability",
            "icon": "🛡️",
            "interview_q": "How do you make LLM responses feel fast? What if the API goes down?",
            "one_line": "Stream tokens as they're generated so users see output immediately; switch models automatically on failure.",
        },
    ]

    for r in rows:
        with st.container(border=True):
            col_badge, col_content = st.columns([1, 5])
            with col_badge:
                st.markdown(f"### {r['icon']}")
                st.markdown(f"**{r['uc']}**")
            with col_content:
                st.markdown(f"#### {r['technique']}")
                st.markdown(f"*Concern: {r['concern']}*")
                st.markdown(f"**{r['one_line']}**")
                st.caption(f"Interview question this answers: \"{r['interview_q']}\"")

    st.divider()
    st.markdown("### What Each UC Teaches — In Plain English")

    with st.expander("UC1 — Semantic Caching", expanded=False):
        st.markdown(
            """
            **The problem:** Every LLM call costs money. If 100 users ask "What is machine learning?" in
            slightly different ways, you pay for 100 separate API calls — even though the answer is the same.

            **The solution:** Store answers with their *meaning* (a vector), not the exact text.
            When a new question comes in, check if it means the same thing as a stored one.
            If it's similar enough (above a threshold), return the stored answer instantly.

            **You will learn:**
            - How exact-match caching fails for natural language
            - How cosine similarity finds semantically equivalent questions
            - How to tune the similarity threshold
            - Latency comparison: cached (~5 ms) vs LLM call (~800 ms)
            """
        )

    with st.expander("UC2 — Model Routing", expanded=False):
        st.markdown(
            """
            **The problem:** A 70B model is 5–10× more expensive than an 8B model per token.
            But most questions don't need a 70B model — "What is Python?" does not require a supercomputer.

            **The solution:** Before sending a query to the big model, run a quick classifier
            (using the small model itself, 5 tokens, ~50 ms) to decide: is this simple or complex?
            Simple → small model. Complex → large model.

            **You will learn:**
            - How to write a complexity classifier prompt
            - How to measure the routing overhead vs the savings it produces
            - When routing pays off and when it doesn't
            - Estimated cost breakdown: 70 % simple traffic → 67 % cost reduction
            """
        )

    with st.expander("UC3 — Memory Patterns", expanded=False):
        st.markdown(
            """
            **The problem:** LLMs are stateless — they remember nothing between calls.
            To have a conversation, you must resend all previous messages every time.
            As the conversation grows, so does your cost and the risk of hitting the context limit.

            **The solution:** Three strategies for deciding what to send:

            - **Buffer Memory** — keep only the last N messages. Simple, but forgets older context.
            - **Summary Memory** — use the LLM to compress old turns into bullet points,
              then send the summary + recent messages. Scales to long conversations.
            - **Entity Memory** — extract names, organisations, and facts from each message,
              store them in a dict, and inject the dict into the system prompt.
              Best for assistants that need to remember who the user is.

            **You will learn:**
            - The real cost of long conversation histories
            - How to implement all three patterns from scratch (no LangChain required)
            - How to pick the right strategy for your use case
            """
        )

    with st.expander("UC4 — Streaming + Fallback", expanded=False):
        st.markdown(
            """
            **The problem 1 (Streaming):** A typical LLM response takes 2–5 seconds to generate.
            If you wait for the full response before showing anything, the UI feels frozen.

            **The solution:** Turn on streaming. The API sends tokens as they're generated.
            The user sees the first word in < 500 ms and the text appears to "type itself".
            Total generation time is identical — but *perceived* latency drops by 70–90 %.

            ---

            **The problem 2 (Fallback):** LLM APIs go down. Rate limits hit at the worst moment.
            If your app crashes when the primary model fails, users have a bad experience.

            **The solution:** Build a retry + fallback layer:
            1. Try the primary model. If it fails, wait 0.5 s and retry.
            2. If it fails again, wait 1 s and retry once more.
            3. If all retries fail, automatically switch to the fallback model.
            4. Users get an answer regardless of primary model outages.

            **You will learn:**
            - How to implement Groq streaming with `st.write_stream()`
            - How exponential backoff prevents hammering a rate-limited API
            - How to design a multi-model fallback chain
            - Which production metrics to monitor (TTFT, fallback rate, retry count)
            """
        )

    st.divider()
    st.markdown("### How These Patterns Work Together in Production")
    st.markdown(
        """
        In a real production LLM system, you layer all four:

        ```
        User query
            ↓
        [UC1] Semantic Cache → HIT? Return instantly (no LLM needed)
            ↓ MISS
        [UC2] Model Router  → Simple? Use 8B. Complex? Use 70B.
            ↓
        [UC3] Memory        → Inject the right conversation context
            ↓
        [UC4] Streaming     → Stream tokens to the user as they arrive
              Fallback      → If primary fails, retry → switch model
        ```

        Together, this stack typically reduces API cost by **60–80 %** and
        reduces perceived latency by **70–90 %** compared to a naïve single-model setup.
        """
    )
