"""UC1 — Concept page: Zero-shot vs Few-shot."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Zero-shot vs Few-shot Prompting")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- What 'prompting' means and why it matters\n"
        "- The difference between zero-shot and few-shot in plain English\n"
        "- When to use examples and when not to bother\n"
        "- How to try both approaches yourself in the Playground"
    )

    st.markdown(
        "**Prompting** means writing instructions for an AI — the words you type before your actual request. "
        "The same question can get very different answers depending on how you frame it.\n\n"
        "The first choice every prompt engineer makes: *do I give the AI examples, or not?*"
    )
    st.write(
        "This single choice has a large effect on output quality, consistency, and style."
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### ⚡ Zero-shot")
            st.write(
                "You give the model an instruction and nothing else. "
                "The model relies entirely on its pre-trained knowledge to interpret and complete the task."
            )
            st.markdown("**When to use:**")
            st.markdown(
                "- General tasks the model already understands well\n"
                "- Quick prototyping and exploration\n"
                "- When you have no examples available\n"
                "- Simple, unambiguous instructions"
            )
            st.info("**Strength:** Fast, minimal prompt tokens\n\n**Risk:** Output style may vary")

    with col2:
        with st.container(border=True):
            st.markdown("#### 🎯 Few-shot")
            st.write(
                "You include 2–5 worked examples before your actual request. "
                "The model learns the expected pattern, tone, and format from your demonstrations."
            )
            st.markdown("**When to use:**")
            st.markdown(
                "- Custom output formats or styles\n"
                "- Domain-specific tasks the model may misinterpret\n"
                "- Classification with specific label schemes\n"
                "- When consistency matters more than speed"
            )
            st.info("**Strength:** Consistent, style-matched output\n\n**Risk:** More prompt tokens")

    st.divider()
    st.markdown("#### How it looks in practice")

    tab_zero, tab_few = st.tabs(["Zero-shot prompt", "Few-shot prompt"])

    with tab_zero:
        st.code(
            """# Zero-shot: instruction only
prompt = \"\"\"
Classify the sentiment of this review as Positive, Negative, or Neutral.

Review: "The battery life is okay but the camera is disappointing."
Sentiment:
\"\"\"
""",
            language="python",
        )

    with tab_few:
        st.code(
            """# Few-shot: instruction + 3 examples
prompt = \"\"\"
Classify the sentiment of each review as Positive, Negative, or Neutral.

Example 1:
Review: "Absolutely love this product, exceeded all expectations!"
Sentiment: Positive

Example 2:
Review: "Broke after two days. Terrible quality."
Sentiment: Negative

Example 3:
Review: "It works fine. Nothing special."
Sentiment: Neutral

Now classify:
Review: "The battery life is okay but the camera is disappointing."
Sentiment:
\"\"\"
""",
            language="python",
        )

    st.divider()
    st.markdown("#### Key insight")
    st.success(
        "Few-shot doesn't teach the model new knowledge — it teaches it **how you want the output formatted**. "
        "The examples are a template, not training data. "
        "Good examples are diverse, representative, and short."
    )

    st.markdown("#### Rule of thumb")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Zero-shot", "Start here", "Always try first")
    col_b.metric("Few-shot", "2–5 examples", "If zero-shot is inconsistent")
    col_c.metric("Example quality", "> quantity", "1 great > 5 mediocre")
