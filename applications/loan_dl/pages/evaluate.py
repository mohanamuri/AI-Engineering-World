"""Model evaluation dashboard for the loan eligibility DL pipeline.

Mirrors loan_ml's evaluate page but uses loan_dl session keys and
DLTrainResult. Feature importance is not available for MLP (shown as a
note); the page instead highlights the loss curve from the train page.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from applications.loan_dl.constants import (
    EVAL_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_dl.services.trainer import DLTrainResult
from applications.loan_ml.services.metrics import EvaluationResult, evaluate
from applications.loan_ml.services.preprocessor import PreprocessResult
from applications.shared.api_reference import render_api_reference

CHART_COLOR = "#0891b2"
HEATMAP_COLORS = [[0.0, "#ECFEFF"], [0.5, "#67E8F9"], [1.0, "#0E7490"]]
_TRAIN_PAGE_LABEL = "🧠 Train Neural Network"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    st.header("📈 Evaluate Model")
    st.caption(
        "Accuracy alone is not enough. Inspect precision, recall, the confusion "
        "matrix, and the ROC curve to understand where your network succeeds and fails."
    )

    train_result: DLTrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)

    if not isinstance(train_result, DLTrainResult) or not isinstance(preprocess_result, PreprocessResult):
        _render_empty_state()
        return

    eval_result = _get_or_compute_eval(train_result, preprocess_result)
    if eval_result is None:
        return

    _render_headline_metrics(eval_result)
    st.divider()
    _render_confusion_matrix(eval_result)
    st.divider()
    _render_roc_curve(eval_result)
    st.divider()
    _render_feature_importance_note(train_result)
    st.divider()
    _render_classification_report(eval_result)
    render_api_reference("loan_dl", "evaluate")


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("No trained neural network found.")
        st.write("Train a neural network before opening the evaluation dashboard.")
        st.button(
            "← Go to Train Neural Network",
            type="primary",
            on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE_LABEL}),
        )


# ---------------------------------------------------------------------------
# Evaluation compute + cache
# ---------------------------------------------------------------------------

def _get_or_compute_eval(
    train_result: DLTrainResult,
    preprocess_result: PreprocessResult,
) -> EvaluationResult | None:
    cached: EvaluationResult | None = st.session_state.get(EVAL_RESULT_SESSION_KEY)

    if isinstance(cached, EvaluationResult) and cached.model_name == train_result.model.__class__.__name__:
        return cached

    with st.spinner("Computing evaluation metrics…"):
        try:
            result = evaluate(
                model=train_result.model,
                X_test=preprocess_result.X_test,
                y_test=preprocess_result.y_test,
            )
        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
            return None

    st.session_state[EVAL_RESULT_SESSION_KEY] = result
    return result


# ---------------------------------------------------------------------------
# Headline metrics
# ---------------------------------------------------------------------------

def _render_headline_metrics(result: EvaluationResult) -> None:
    st.subheader(f"Metrics — {result.model_name}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Accuracy", f"{result.accuracy:.1%}", help="Fraction of correct predictions.")
    m2.metric("Precision", f"{result.precision:.1%}", help="Of predicted positives, how many were correct?")
    m3.metric("Recall", f"{result.recall:.1%}", help="Of actual positives, how many did we catch?")
    m4.metric("F1 Score", f"{result.f1:.1%}", help="Harmonic mean of precision and recall.")
    m5.metric(
        "ROC AUC",
        f"{result.roc_auc:.3f}" if result.roc_auc is not None else "N/A",
        help="Area under the ROC curve. 1.0 = perfect, 0.5 = random.",
    )


# ---------------------------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------------------------

def _render_confusion_matrix(result: EvaluationResult) -> None:
    st.subheader("Confusion matrix")
    st.caption("Rows = actual class · Columns = predicted class. Diagonal = correct predictions.")

    labels = [str(l) for l in result.class_labels]
    cm = result.confusion_matrix
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)

    hover = np.array([
        [
            f"Actual: {labels[r]}<br>Predicted: {labels[c]}<br>Count: {cm[r, c]}<br>{cm_norm[r, c]:.1%} of row"
            for c in range(len(labels))
        ]
        for r in range(len(labels))
    ])

    figure = go.Figure(data=go.Heatmap(
        z=cm_norm, x=labels, y=labels,
        colorscale=HEATMAP_COLORS, zmin=0, zmax=1,
        text=cm, texttemplate="%{text}",
        hovertext=hover, hoverinfo="text",
        showscale=True, colorbar={"title": "Row %"},
    ))
    figure.update_layout(
        xaxis_title="Predicted", yaxis_title="Actual",
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_autorange="reversed",
    )

    col_chart, col_interp = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(figure, use_container_width=True)
    with col_interp:
        with st.container(border=True):
            st.markdown("**Reading the matrix**")
            st.markdown(
                "- **Diagonal cells** (dark) → correct predictions\n"
                "- **Off-diagonal cells** (light) → errors\n"
                "- **False Negatives** → bottom-left\n"
                "- **False Positives** → top-right"
            )


# ---------------------------------------------------------------------------
# ROC curve
# ---------------------------------------------------------------------------

def _render_roc_curve(result: EvaluationResult) -> None:
    st.subheader("ROC curve")

    if result.fpr is None or result.tpr is None:
        if result.roc_auc is not None:
            st.info(f"ROC AUC: **{result.roc_auc:.3f}** (multi-class — per-class curves not shown).", icon="ℹ️")
        else:
            st.info("ROC curve is not available for this configuration.", icon="ℹ️")
        return

    roc_df = pd.DataFrame({"FPR": result.fpr, "TPR": result.tpr})
    figure = px.line(
        roc_df, x="FPR", y="TPR",
        labels={"FPR": "False Positive Rate", "TPR": "True Positive Rate"},
        color_discrete_sequence=[CHART_COLOR],
    )
    figure.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(color="#94A3B8", width=1, dash="dash"))
    figure.add_annotation(x=0.65, y=0.45, text="Random classifier", showarrow=False, font=dict(color="#94A3B8", size=11))
    figure.update_layout(margin=dict(l=10, r=10, t=20, b=10), xaxis=dict(range=[0, 1]), yaxis=dict(range=[0, 1.02]))

    col_chart, col_interp = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(figure, use_container_width=True)
    with col_interp:
        with st.container(border=True):
            st.metric("AUC", f"{result.roc_auc:.3f}" if result.roc_auc else "N/A")
            st.markdown(
                "**AUC = Area Under the Curve**\n\n"
                "- **1.0** → perfect classifier\n"
                "- **0.5** → random guessing\n"
                "- **< 0.5** → worse than random"
            )


# ---------------------------------------------------------------------------
# Feature importance note (MLP-specific)
# ---------------------------------------------------------------------------

def _render_feature_importance_note(train_result: DLTrainResult) -> None:
    st.subheader("Feature importance")
    with st.container(border=True):
        st.info(
            "MLPClassifier does not expose feature importances directly — it has no "
            "`feature_importances_` or `coef_` attribute at the input layer.\n\n"
            "**Production approaches for MLP interpretability:**\n"
            "- **SHAP** (SHapley Additive exPlanations) — model-agnostic, works via perturbation\n"
            "- **Integrated Gradients** — computes gradients w.r.t. inputs (PyTorch/TF)\n"
            "- **Permutation importance** — shuffle each feature and measure accuracy drop\n\n"
            "These are implemented in the **Explainability (T3)** tier of this project.",
            icon="ℹ️",
        )
        st.caption(f"Network architecture: {train_result.hyperparams.get('architecture', 'N/A')}")


# ---------------------------------------------------------------------------
# Per-class report
# ---------------------------------------------------------------------------

def _render_classification_report(result: EvaluationResult) -> None:
    st.subheader("Per-class report")

    report = result.classification_report
    rows = []
    for label, metrics in report.items():
        if label in ("accuracy", "macro avg", "weighted avg"):
            continue
        if isinstance(metrics, dict):
            rows.append({
                "Class": str(label),
                "Precision": metrics.get("precision", 0),
                "Recall": metrics.get("recall", 0),
                "F1": metrics.get("f1-score", 0),
                "Support": int(metrics.get("support", 0)),
            })

    if not rows:
        return

    report_df = pd.DataFrame(rows)
    styled = (
        report_df.style
        .format({"Precision": "{:.1%}", "Recall": "{:.1%}", "F1": "{:.1%}"})
        .background_gradient(subset=["Precision", "Recall", "F1"], cmap="Blues")
    )
    with st.container(border=True):
        st.dataframe(styled, hide_index=True, width="stretch")
    st.caption("**Support** = number of test samples for that class.")
