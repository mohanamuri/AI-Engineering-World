"""Evaluate page for HR Deep Learning — reuses hr_ml metrics service."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from applications.hr_dl.constants import (
    EVAL_RESULT_SESSION_KEY, NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY, TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_ml.services.metrics import EvaluationResult, evaluate

_TRAIN_PAGE_LABEL = "🧠 Train Neural Network"
CHART_COLOR = "#7c3aed"


def render() -> None:
    st.header("📈 Evaluate Model")
    st.caption("Neural networks on imbalanced data — check F1 for the 'Yes' class, not just accuracy.")

    train_result = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)

    if train_result is None or preprocess_result is None:
        st.warning("Train a neural network first.")
        st.button("← Go to Train", on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE_LABEL}))
        return

    cached = st.session_state.get(EVAL_RESULT_SESSION_KEY)
    if isinstance(cached, EvaluationResult) and cached.model_name == train_result.model.__class__.__name__:
        result = cached
    else:
        with st.spinner("Computing metrics…"):
            try:
                result = evaluate(train_result.model, preprocess_result.X_test, preprocess_result.y_test)
            except Exception as exc:
                st.error(f"Evaluation failed: {exc}")
                return
        st.session_state[EVAL_RESULT_SESSION_KEY] = result

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Accuracy", f"{result.accuracy:.1%}")
    m2.metric("Precision", f"{result.precision:.1%}")
    m3.metric("Recall", f"{result.recall:.1%}")
    m4.metric("F1 Score", f"{result.f1:.1%}")
    m5.metric("ROC AUC", f"{result.roc_auc:.3f}" if result.roc_auc else "N/A")

    st.divider()
    # Confusion matrix
    labels = [str(l) for l in result.class_labels]
    cm = result.confusion_matrix
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)
    fig = go.Figure(data=go.Heatmap(
        z=cm_norm, x=labels, y=labels,
        colorscale=[[0, "#f5f3ff"], [0.5, "#a78bfa"], [1, "#6d28d9"]],
        text=cm, texttemplate="%{text}", showscale=True,
    ))
    fig.update_layout(xaxis_title="Predicted", yaxis_title="Actual",
                      margin=dict(l=10, r=10, t=20, b=10), yaxis_autorange="reversed")
    st.subheader("Confusion matrix")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    # ROC curve
    if result.fpr is not None and result.tpr is not None:
        st.subheader("ROC curve")
        roc_df = pd.DataFrame({"FPR": result.fpr, "TPR": result.tpr})
        fig2 = px.line(roc_df, x="FPR", y="TPR", color_discrete_sequence=[CHART_COLOR])
        fig2.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(color="#94A3B8", dash="dash"))
        fig2.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        c1, c2 = st.columns([2, 1])
        with c1:
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            st.metric("AUC", f"{result.roc_auc:.3f}" if result.roc_auc else "N/A")

    st.divider()
    # Per-class report
    st.subheader("Per-class report")
    rows = [{"Class": str(k), "Precision": v["precision"], "Recall": v["recall"],
              "F1": v["f1-score"], "Support": int(v["support"])}
             for k, v in result.classification_report.items()
             if isinstance(v, dict) and k not in ("macro avg", "weighted avg")]
    if rows:
        df = pd.DataFrame(rows)
        styled = df.style.format({"Precision": "{:.1%}", "Recall": "{:.1%}", "F1": "{:.1%}"})\
                         .background_gradient(subset=["Precision", "Recall", "F1"], cmap="Purples")
        st.dataframe(styled, hide_index=True, use_container_width=True)
        st.caption("Focus on **Yes (Attrition)** — catching flight risks is the goal.")
