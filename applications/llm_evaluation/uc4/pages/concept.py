"""UC4 — Concept: Why systematic eval pipelines are essential and how to build them."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Concept — Eval Pipeline")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why evaluating individual responses is not enough — you need a test dataset\n"
        "- What an eval pipeline is and how it connects all 4 evaluation patterns\n"
        "- How to design a good eval dataset (diverse, representative, ground-truth labelled)\n"
        "- How to integrate evaluation into CI/CD to prevent regressions from reaching production"
    )

    st.markdown(
        "You now have 3 evaluation tools: RAGAS (UC1), LLM-as-Judge (UC2), and "
        "Hallucination Detection (UC3). But running them one at a time on hand-picked examples "
        "tells you nothing reliable about your system's overall quality.\n\n"
        "**Systematic evaluation requires a test dataset** — a collection of representative "
        "question/answer pairs where you run all metrics automatically. Only then can you "
        "confidently say 'version 2 is better than version 1' or 'this deploy is safe to ship.'"
    )

    st.markdown(
        """
        ### The Problem: Ad-Hoc Evaluation Doesn't Scale

        Without a systematic eval pipeline, teams fall into these traps:
        """
    )

    problems = [
        (
            "Cherry-picking",
            "Developers naturally test the examples they know work well. "
            "Edge cases, ambiguous questions, and adversarial inputs are never tested — "
            "until they fail in production.",
        ),
        (
            "No baseline",
            "When a user reports a bug, you can't tell if it's a regression (it worked before) "
            "or a pre-existing issue. Without a fixed test set, you have no baseline to compare against.",
        ),
        (
            "Invisible regressions",
            "A model update or prompt change might fix 3 examples while breaking 10 others. "
            "If you only test the 3 you intended to fix, the regressions are invisible.",
        ),
        (
            "No CI/CD integration",
            "Without automated evaluation, every deploy is a manual check. "
            "This is fine for prototypes but breaks down at team scale or when deploying weekly.",
        ),
    ]

    for p_title, p_body in problems:
        with st.container(border=True):
            st.markdown(f"**❌ {p_title}**")
            st.write(p_body)

    st.divider()
    st.markdown("### What an Eval Pipeline Does")
    st.markdown(
        """
        ```
        Test dataset (JSON)
            ↓
        For each test case:
            → Run RAGAS  → faithfulness, relevance, recall, precision
            → Run hallucination detection  → hallucination_rate, per-claim verdicts
            ↓
        Aggregate metrics:
            → avg_faithfulness, avg_relevance, avg_recall, avg_precision
            → avg_hallucination_rate
            ↓
        Dashboard:
            → Metric averages with pass/fail thresholds
            → Per-case table with flag indicators
            → Trend over time (if you store results)
            ↓
        Decision:
            → All metrics green? → approve deploy
            → Any metric red? → block deploy, investigate
        ```
        """
    )

    st.divider()
    st.markdown("### Designing a Good Eval Dataset")
    st.markdown(
        "The quality of your evaluation is only as good as your test dataset. "
        "A poor test set gives false confidence."
    )

    dataset_principles = [
        (
            "1. Representative coverage",
            "Include questions from every user intent category in your application. "
            "For a customer support bot: billing questions, product questions, troubleshooting, "
            "complaints, and edge cases. Aim for proportional distribution (if 60 % of real "
            "queries are product questions, 60 % of test cases should be too).",
        ),
        (
            "2. Diverse difficulty",
            "Include easy questions (direct fact lookup), medium questions (multi-hop reasoning), "
            "and hard questions (ambiguous, adversarial, or requiring synthesis). "
            "A system that scores 0.90 on easy questions may score 0.40 on hard ones.",
        ),
        (
            "3. Ground truth is mandatory",
            "Every test case needs a ground truth answer — what the ideal response should contain. "
            "Without ground truth, you can't compute context recall, and hallucination detection "
            "has no reference. Ground truth doesn't need to be perfectly worded — "
            "it just needs to capture the key facts the answer must include.",
        ),
        (
            "4. Include failure cases",
            "Add examples where you know the system previously failed or is likely to fail. "
            "This makes your test set a 'regression suite' — it catches known failure modes "
            "from coming back after a fix.",
        ),
        (
            "5. Size",
            "For a meaningful average, you need at least 20–50 test cases. "
            "100+ is production-grade. More cases = more reliable averages and better "
            "signal for rare edge cases. Start small and grow the dataset over time.",
        ),
    ]

    for dp_title, dp_body in dataset_principles:
        with st.container(border=True):
            st.markdown(f"**{dp_title}**")
            st.write(dp_body)

    st.divider()
    st.markdown("### Test Case JSON Format")
    st.markdown("Each test case in the JSON upload uses this schema:")
    st.code(
        """\
[
  {
    "question": "What is the return policy for electronics?",
    "answer": "Electronics can be returned within 30 days...",
    "contexts": [
      "Our return policy allows customers to return...",
      "Electronics must be returned in original packaging..."
    ],
    "ground_truth": "Electronics: 30-day return, original packaging required.",
    "reference_answer": ""
  }
]""",
        language="json",
    )

    st.divider()
    st.markdown("### CI/CD Integration Pattern")
    st.markdown(
        """
        In a production team, eval runs automatically on every pull request:

        ```yaml
        # .github/workflows/eval.yml (example)
        on: pull_request
        jobs:
          evaluate:
            steps:
              - name: Run eval pipeline
                run: python run_eval.py --dataset tests/eval_dataset.json
              - name: Check thresholds
                run: python check_thresholds.py --min-faithfulness 0.75 --max-hallucination 0.25
        ```

        If thresholds are not met, the PR is blocked. This prevents quality regressions
        from being merged, just like unit tests prevent code regressions.
        """
    )

    st.success(
        "**Next → Playground:** Load 3 built-in sample test cases or upload your own JSON. "
        "Run RAGAS and hallucination detection across the full set and see the metrics dashboard."
    )
