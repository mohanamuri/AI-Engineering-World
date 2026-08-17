"""UC2 — Concept: What is LLM-as-Judge and why it scales where humans can't."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — LLM-as-Judge")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why human evaluation is the gold standard but doesn't scale to production\n"
        "- How LLM judges work: rubric-based scoring with explicit reasoning\n"
        "- The 5 biases that affect LLM judges and how to mitigate them\n"
        "- When LLM-as-judge is reliable and when to be cautious"
    )

    st.markdown(
        "You deployed an LLM-powered product. Now you need to know: **is it giving good responses?**\n\n"
        "Manual review by humans is expensive ($10–$50 per response for expert annotators), slow "
        "(days to weeks), and hard to scale. If your system handles 10,000 requests per day, "
        "you cannot review them all.\n\n"
        "**LLM-as-Judge** is the solution: use a second, trusted LLM to score responses automatically, "
        "at scale, with consistent rubrics and written reasoning."
    )

    st.markdown(
        """
        ### The Problem: Human Evaluation Doesn't Scale

        | Method | Cost | Speed | Scale | Consistency |
        |---|---|---|---|---|
        | Human expert review | Very high | Slow | Poor | Variable |
        | Crowdsourced labels | Medium | Medium | Good | Low |
        | Simple metrics (BLEU, ROUGE) | Very low | Fast | Excellent | High |
        | LLM-as-Judge | Low | Fast | Excellent | High |

        Simple metrics like BLEU (word overlap) correlate poorly with human judgement for open-ended
        generation. LLM judges achieve **~80 % agreement with human annotators** on structured criteria —
        comparable to inter-annotator agreement between humans.
        """
    )

    st.divider()
    st.markdown("### How LLM-as-Judge Works")

    steps = [
        (
            "1️⃣ Define your criteria",
            "Specify what makes a response 'good' for your use case. "
            "Generic criteria work for most applications: accuracy, relevance, clarity, completeness. "
            "Domain-specific criteria might include: medical safety, legal precision, tone (formal vs casual). "
            "Each criterion gets a weight — accuracy might matter twice as much as conciseness.",
        ),
        (
            "2️⃣ Write a scoring rubric",
            "For each criterion, the judge LLM needs to understand what 1/10 looks like vs 10/10. "
            "Implicit rubrics work for general criteria. For specialised domains, write explicit "
            "rubrics: 'Score 1 = factually incorrect, Score 5 = partially correct with one error, "
            "Score 10 = factually accurate with no mistakes.'",
        ),
        (
            "3️⃣ Submit to judge LLM",
            "Pass the original question + the response to evaluate to a capable judge LLM "
            "(we use the same Groq-hosted models as the generator). The judge scores each criterion "
            "1–10 and provides a one-sentence reason. This creates an audit trail.",
        ),
        (
            "4️⃣ Compute weighted average",
            "Aggregate the criterion scores using a weighted average. "
            "The result is a single 1–10 quality score for the response.",
        ),
        (
            "5️⃣ Pairwise comparison (optional)",
            "Instead of scoring one response, compare two: 'Which response is better and why?' "
            "Pairwise comparison is more reliable than absolute scoring because it exploits the "
            "judge's relative reasoning ability.",
        ),
    ]

    for step_title, step_body in steps:
        with st.container(border=True):
            st.markdown(f"**{step_title}**")
            st.write(step_body)

    st.divider()
    st.markdown("### The 5 Biases That Affect LLM Judges")

    biases = [
        (
            "1. Position Bias",
            "When comparing two responses (A vs B), the judge tends to prefer whichever is presented first. "
            "**Mitigation:** Always evaluate both orderings — judge A vs B and B vs A — and use the "
            "average. If results flip, the judge is unreliable for this criterion.",
        ),
        (
            "2. Verbosity Bias",
            "Longer responses look more thorough, so judges often rate them higher regardless of quality. "
            "**Mitigation:** Explicitly instruct the judge: 'Do not reward length. A concise, accurate "
            "answer is better than a long, padded one.' Add Conciseness as a separate criterion.",
        ),
        (
            "3. Self-Preference Bias",
            "An LLM judge tends to rate responses from its own model family higher. GPT-4 prefers "
            "GPT-4 outputs; Claude prefers Claude-style writing. "
            "**Mitigation:** Use a different model family for the judge than for the generator, "
            "or use multiple judges and average their scores.",
        ),
        (
            "4. Sycophancy Bias",
            "The judge may agree with confident-sounding statements even if they are wrong. "
            "**Mitigation:** Use zero temperature for the judge (deterministic), and frame the "
            "evaluation task as adversarial fact-checking, not approval.",
        ),
        (
            "5. Recency Bias",
            "In long conversations, the judge may overweight the most recent message. "
            "**Mitigation:** Summarise the full conversation before passing it to the judge, "
            "or evaluate each turn independently.",
        ),
    ]

    for bias_title, bias_body in biases:
        with st.container(border=True):
            st.markdown(f"**{bias_title}**")
            st.write(bias_body)

    st.divider()
    st.markdown("### Single-Response vs Pairwise Evaluation")

    col_single, col_pair = st.columns(2)
    with col_single:
        with st.container(border=True):
            st.markdown("**Single-Response Scoring**")
            st.markdown(
                "Score one response in isolation on each criterion.\n\n"
                "- Faster — one LLM call per response\n"
                "- Easier to automate at scale\n"
                "- Less susceptible to position bias\n"
                "- Harder to calibrate (what does 7/10 mean?)\n\n"
                "**Best for:** Monitoring production quality over time."
            )
    with col_pair:
        with st.container(border=True):
            st.markdown("**Pairwise Comparison**")
            st.markdown(
                "Compare two responses: which is better?\n\n"
                "- More reliable — relative judgement is easier for LLMs\n"
                "- Natural for A/B testing (new vs old version)\n"
                "- Susceptible to position bias (always swap order)\n"
                "- More expensive — two sets of LLM calls\n\n"
                "**Best for:** Evaluating model upgrades or prompt changes."
            )

    st.success(
        "**Next → Playground:** Paste two responses to the same question and see the judge "
        "score each one on Accuracy, Relevance, Clarity, Completeness, and Conciseness."
    )
