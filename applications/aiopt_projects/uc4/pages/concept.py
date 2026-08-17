"""UC4 — Concept: Streaming and Fallback in production LLM systems."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Streaming + Fallback")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why waiting for a full AI response feels slow — and how streaming fixes it\n"
        "- What happens when an AI API is overloaded or rate-limited\n"
        "- How automatic fallback keeps your app running even when the primary AI fails\n"
        "- How to experience streaming and fallback live in the Playground"
    )

    st.markdown(
        "You've used ChatGPT and noticed the response **types itself out word by word** "
        "instead of appearing all at once. That's streaming — and it makes the experience feel "
        "dramatically faster, even though the total time is the same.\n\n"
        "And sometimes AI APIs get overloaded and return errors. "
        "**Fallback** automatically switches to a backup model so users never see a failure.\n\n"
        "These are two independent production patterns that every real AI application needs."
    )

    st.markdown("### Two Independent Production Patterns")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**⚡ Streaming**")
            st.markdown(
                "Return tokens as they are generated instead of waiting for the full response.\n\n"
                "- **Perceived latency drops by 70–90 %** — the user sees the first token "
                "in < 500 ms instead of waiting 3–8 s for the full response\n"
                "- Actual total latency is the same — you're just distributing it across time\n"
                "- Essential for any conversational or interactive UX"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**🛡️ Fallback**")
            st.markdown(
                "If the primary model fails or rate-limits, retry then switch to a backup.\n\n"
                "- **Availability** — production LLM APIs return 429 (rate limit) and 503 (overload)\n"
                "- Retry with exponential backoff before giving up\n"
                "- If all retries fail, switch to a backup model automatically\n"
                "- User sees a response regardless of primary model failures"
            )

    st.divider()
    st.markdown("### Streaming — How It Works")

    steps = [
        ("1️⃣ Set stream=True in the API call",
         "The API sends tokens as a stream of server-sent events (SSE) instead of one large JSON response. "
         "Each event contains a delta: the next token or small token group."),
        ("2️⃣ Iterate the stream",
         "`for chunk in stream: delta = chunk.choices[0].delta.content` — "
         "each `delta` is a string (sometimes a single character, sometimes a word or two)."),
        ("3️⃣ Yield tokens to the UI",
         "In Streamlit, pass the generator to `st.write_stream()`. "
         "It renders each token as it arrives — the text appears to 'type itself'."),
    ]
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    st.code(
        """# Streaming with Groq
stream = client.chat.completions.create(
    model="mixtral-8x7b-32768",
    stream=True,  # ← enable streaming
    messages=[...],
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        yield delta  # ← yield each token""",
        language="python",
    )

    st.divider()
    st.markdown("### Fallback — How It Works")

    st.code(
        """# Retry then fallback
for attempt in range(1, MAX_RETRIES + 1):
    try:
        resp = client.chat.completions.create(model=PRIMARY, ...)
        return resp  # success
    except Exception:
        time.sleep(0.5 * attempt)  # exponential backoff

# All retries failed — switch to backup model
resp = client.chat.completions.create(model=FALLBACK, ...)
return resp""",
        language="python",
    )

    st.markdown("### Retry + Backoff Strategy")
    st.table({
        "Attempt": ["1", "2", "3 (fallback)"],
        "Model": ["Primary (8B)", "Primary (8B)", "Fallback (70B)"],
        "Wait before": ["0 ms", "500 ms", "1000 ms"],
        "What happens": [
            "First try — most requests succeed here",
            "Retry — handles transient 429s",
            "Permanent failure → switch model",
        ],
    })

    st.divider()
    st.markdown("### When to Use Each Pattern")
    st.table({
        "Pattern": ["Streaming", "Fallback", "Both together"],
        "Use when": [
            "Any interactive chat or assistant UI",
            "Production app with SLA / uptime requirements",
            "User-facing chat with reliable delivery requirement",
        ],
        "Don't use when": [
            "Batch processing (no user watching)",
            "Single model, no budget for backup calls",
            "Offline processing jobs",
        ],
    })

    st.success(
        "**Next → Playground:** Experience streaming live — watch tokens appear in real time. "
        "Then try the fallback demo to see automatic model switching."
    )
