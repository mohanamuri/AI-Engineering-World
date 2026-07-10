"""UC2 — Concept page: Chain-of-Thought prompting."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Chain-of-Thought Prompting")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why AI sometimes gets wrong answers to seemingly simple questions\n"
        "- How one phrase ('Let's think step by step') dramatically improves accuracy\n"
        "- When Chain-of-Thought helps most — and when it's overkill\n"
        "- How to try direct vs CoT prompting side by side in the Playground"
    )

    st.markdown(
        "Have you ever asked an AI a maths or logic question and got a confidently wrong answer? "
        "That happens because the model 'jumps to a conclusion' without thinking through the steps.\n\n"
        "**Chain-of-Thought (CoT)** is a technique that fixes this: you tell the AI to "
        "*think out loud* before answering — and it suddenly gets the right answer."
    )
    st.write(
        "It was introduced by Wei et al. (2022) and remains one of the most impactful "
        "zero-cost improvements in prompt engineering."
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 🚀 Direct prompting")
            st.write(
                "Ask the question, get an answer. The model produces output in a single step "
                "without showing any intermediate reasoning."
            )
            st.markdown("**Works well for:**")
            st.markdown(
                "- Simple factual lookups\n"
                "- Straightforward instructions\n"
                "- Low-latency scenarios\n"
                "- Tasks with unambiguous answers"
            )
            st.warning("**Risk:** On complex problems the model may jump to a wrong answer confidently.")

    with col2:
        with st.container(border=True):
            st.markdown("#### 🔗 Chain-of-Thought")
            st.write(
                "The model is prompted to think out loud — it writes reasoning steps before "
                "the final answer. Each step builds on the previous, reducing errors from "
                "skipped logic."
            )
            st.markdown("**Works well for:**")
            st.markdown(
                "- Multi-step math and logic\n"
                "- Planning and scheduling problems\n"
                "- Code debugging and analysis\n"
                "- Decisions requiring justification"
            )
            st.success("**Benefit:** Errors in intermediate steps are visible and correctable.")

    st.divider()
    st.markdown("#### The magic phrase")
    st.info(
        "Just adding **\"Let's think step by step\"** or **\"Think through this carefully\"** "
        "to your prompt activates CoT — no examples needed. This is called **zero-shot CoT**."
    )

    tab_direct, tab_cot = st.tabs(["Direct prompt", "Chain-of-Thought prompt"])

    with tab_direct:
        st.code(
            """# Direct — answer in one shot
prompt = \"\"\"
A bat and a ball cost $1.10 in total.
The bat costs $1.00 more than the ball.
How much does the ball cost?
\"\"\"
# Common wrong answer: $0.10
# Correct answer: $0.05
""",
            language="python",
        )

    with tab_cot:
        st.code(
            """# Chain-of-Thought — reason before answering
prompt = \"\"\"
A bat and a ball cost $1.10 in total.
The bat costs $1.00 more than the ball.
How much does the ball cost?

Let's think step by step:
\"\"\"
# Model now reasons:
# Let ball = x
# bat = x + 1.00
# x + (x + 1.00) = 1.10
# 2x = 0.10
# x = 0.05 ✓
""",
            language="python",
        )

    st.divider()
    st.markdown("#### Why does CoT work?")
    c1, c2, c3 = st.columns(3)
    c1.metric("Error surface", "Reduced", "Each step is checkable")
    c2.metric("Reasoning depth", "Increased", "Forces sub-problem decomposition")
    c3.metric("Setup cost", "~0 tokens", "Just one trigger phrase")
