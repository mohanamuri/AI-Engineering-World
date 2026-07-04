"""Model evaluation dashboard for the HR Analytics ML pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from applications.hr_ml.constants import (
    EVAL_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_ml.services.metrics import EvaluationResult, evaluate
from applications.hr_ml.services.preprocessor import PreprocessResult
from applications.hr_ml.services.trainer import TrainResult

CHART_COLOR = "#4f46e5"
HEATMAP_COLORS = [[0.0, "#f0fdf4"], [0.5, "#86efac"], [1.0, "#15803d"]]
_TRAIN_PAGE_LABEL = "🤖 Train Model"


def render() -> None:
    st.header("📈 Evaluate Model")
    st.caption(
        "For attrition prediction, **F1 for the 'Yes' class** and **ROC AUC** matter most. "
        "Accuracy is misleading on this imbalanced dataset (~16 % attrition)."
    )

    train_result: TrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)

    if not isinstance(train_result, TrainResult) or not isinstance(preprocess_result, PreprocessResult):
        st.warning("Train a model first.")
        st.button(
            "← Go to Train Model",
            on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE_LABEL}),
        )
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
    _render_feature_importance(train_result)
    st.divider()
    _render_classification_report(eval_result)


def _get_or_compute_eval(train_result, preprocess_result):
    cached = st.session_state.get(EVAL_RESULT_SESSION_KEY)
    if isinstance(cached, EvaluationResult) and cached.model_name == train_result.model.__class__.__name__:
        return cached
    with st.spinner("Computing evaluation metrics…"):
        try:
            result = evaluate(train_result.model, preprocess_result.X_test, preprocess_result.y_test)
        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
            return None
    st.session_state[EVAL_RESULT_SESSION_KEY] = result
    return result


def _render_headline_metrics(result: EvaluationResult) -> None:
    st.subheader(f"Metrics — {result.model_name}")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Accuracy", f"{result.accuracy:.1%}", help="Fraction of correct predictions. Misleading on imbalanced data.")
    m2.metric("Precision", f"{result.precision:.1%}", help="Of predicted flight risks, how many actually left?")
    m3.metric("Recall", f"{result.recall:.1%}", help="Of actual flight risks, how many did we catch?")
    m4.metric("F1 Score", f"{result.f1:.1%}", help="Harmonic mean of precision and recall. Key metric for attrition.")
    m5.metric("ROC AUC", f"{result.roc_auc:.3f}" if result.roc_auc is not None else "N/A",
              help="Area under ROC curve. 1.0 = perfect, 0.5 = random.")


def _render_confusion_matrix(result: EvaluationResult) -> None:
    st.subheader("Confusion matrix")
    st.caption("Rows = actual · Columns = predicted. For HR: false negatives (missed flight risks) are costly.")

    labels = [str(l) for l in result.class_labels]
    cm = result.confusion_matrix
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)

    hover = np.array([
        [f"Actual: {labels[r]}<br>Predicted: {labels[c]}<br>Count: {cm[r, c]}<br>{cm_norm[r, c]:.1%} of row"
         for c in range(len(labels))]
        for r in range(len(labels))
    ])

    fig = go.Figure(data=go.Heatmap(
        z=cm_norm, x=labels, y=labels,
        colorscale=HEATMAP_COLORS, zmin=0, zmax=1,
        text=cm, texttemplate="%{text}",
        hovertext=hover, hoverinfo="text",
        showscale=True, colorbar={"title": "Row %"},
    ))
    fig.update_layout(xaxis_title="Predicted", yaxis_title="Actual",
                      margin=dict(l=10, r=10, t=20, b=10), yaxis_autorange="reversed")

    col_chart, col_interp = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True)
    with col_interp:
        with st.container(border=True):
            st.markdown("**Reading the matrix**")
            st.markdown(
                "- **Diagonal** → correct predictions\n"
                "- **False Negatives** (lower-left) → missed flight risks\n"
                "- **False Positives** (upper-right) → unnecessary retention spend\n\n"
                "In HR, false negatives are more costly — a missed resignation is harder to reverse."
            )


def _render_roc_curve(result: EvaluationResult) -> None:
    st.subheader("ROC curve")
    if result.fpr is None or result.tpr is None:
        if result.roc_auc is not None:
            st.info(f"ROC AUC: **{result.roc_auc:.3f}**")
        else:
            st.info("ROC curve not available for this model.")
        return

    roc_df = pd.DataFrame({"FPR": result.fpr, "TPR": result.tpr})
    fig = px.line(roc_df, x="FPR", y="TPR",
                  labels={"FPR": "False Positive Rate", "TPR": "True Positive Rate"},
                  color_discrete_sequence=[CHART_COLOR])
    fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                  line=dict(color="#94A3B8", width=1, dash="dash"))
    fig.add_annotation(x=0.65, y=0.45, text="Random classifier", showarrow=False,
                       font=dict(color="#94A3B8", size=11))
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10),
                      xaxis=dict(range=[0, 1]), yaxis=dict(range=[0, 1.02]))

    col_chart, col_interp = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True)
    with col_interp:
        with st.container(border=True):
            st.metric("AUC", f"{result.roc_auc:.3f}" if result.roc_auc else "N/A")
            st.markdown(
                "**AUC = Area Under Curve**\n\n"
                "- **1.0** → perfect\n- **0.5** → random\n\n"
                "Shows the trade-off between catching flight risks (TPR) "
                "and false alarms (FPR) at every threshold."
            )


def _render_feature_importance(train_result: TrainResult) -> None:
    st.subheader("Feature importance")
    model = train_result.model
    feature_names = train_result.feature_names
    importances = None

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        coef = model.coef_
        importances = np.abs(coef[0] if coef.ndim > 1 else coef)

    if importances is None:
        st.info("Feature importance not available for this model.")
        return

    top_n = min(20, len(feature_names))
    df = (pd.DataFrame({"Feature": feature_names, "Importance": importances})
          .sort_values("Importance", ascending=False)
          .head(top_n))

    fig = px.bar(df, x="Importance", y="Feature", orientation="h",
                 color_discrete_sequence=[CHART_COLOR], text_auto=".3f")
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Which factors most strongly predict employee attrition.")


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
    styled = (report_df.style
              .format({"Precision": "{:.1%}", "Recall": "{:.1%}", "F1": "{:.1%}"})
              .background_gradient(subset=["Precision", "Recall", "F1"], cmap="Greens"))
    with st.container(border=True):
        st.dataframe(styled, hide_index=True, use_container_width=True)
    st.caption("Focus on **Yes (Attrition)** row — that's what the model needs to get right.")
