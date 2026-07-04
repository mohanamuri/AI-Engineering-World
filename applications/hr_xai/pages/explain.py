"""Explainability dashboard for the HR Analytics XAI pipeline.

Three tabs:
  1. Global — SHAP summary: which HR factors drive attrition most
  2. Local SHAP — waterfall: why this specific employee is a flight risk
  3. Local LIME — linear approximation for the same employee
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from applications.hr_xai.constants import (
    EXPLAIN_RESULT_SESSION_KEY, NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY, TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_xai.services.explainer import (
    ExplainResult, build_explanation, explain_instance_lime,
)

CHART_PRIMARY = "#0d9488"
CHART_POS = "#059669"
CHART_NEG = "#dc2626"
_TRAIN_PAGE = "🤖 Train Model"


def render() -> None:
    st.header("🔍 Explain Attrition Predictions")
    st.caption(
        "Understand *why* the model flags an employee as a flight risk. "
        "SHAP gives consistent global + local attributions; "
        "LIME provides fast local linear approximations."
    )

    train_result = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)

    if train_result is None or preprocess_result is None:
        st.warning("Train a model first.")
        st.button("← Go to Train Model", type="primary",
                  on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE}))
        return

    explain_result = _get_or_compute(train_result, preprocess_result)
    if explain_result is None:
        return

    tab1, tab2, tab3 = st.tabs(["🌍 Global — SHAP", "🔬 Local — SHAP", "🔬 Local — LIME"])

    with tab1:
        _render_global(explain_result)
    with tab2:
        _render_local_shap(explain_result, train_result)
    with tab3:
        _render_local_lime(explain_result, train_result)


def _get_or_compute(train_result, preprocess_result):
    cached = st.session_state.get(EXPLAIN_RESULT_SESSION_KEY)
    if isinstance(cached, ExplainResult) and cached.model_name == train_result.model_name:
        return cached
    with st.spinner("Computing SHAP values… (10–30 seconds for large datasets)"):
        try:
            result = build_explanation(
                model=train_result.model,
                X_train=preprocess_result.X_train,
                X_test=preprocess_result.X_test,
                class_names=[str(c) for c in preprocess_result.class_labels],
                model_name=train_result.model_name,
            )
        except Exception as exc:
            st.error(f"Explanation failed: {exc}")
            return None
    st.session_state[EXPLAIN_RESULT_SESSION_KEY] = result
    st.success(f"Ready — {len(result.X_test_sample)} instances · `{result.explainer_type}` SHAP explainer")
    return result


def _render_global(result: ExplainResult) -> None:
    st.subheader("Which HR factors drive attrition most?")
    st.caption("Mean |SHAP| across all test employees — higher = more impactful on attrition prediction.")

    mean_shap = np.abs(result.shap_values).mean(axis=0)
    top_n = min(20, len(result.feature_names))
    df = (pd.DataFrame({"Factor": result.feature_names, "Mean |SHAP|": mean_shap})
          .sort_values("Mean |SHAP|", ascending=False).head(top_n))

    fig = px.bar(df, x="Mean |SHAP|", y="Factor", orientation="h",
                 color="Mean |SHAP|",
                 color_continuous_scale=[[0, "#ccfbf1"], [1, "#0d9488"]],
                 text_auto=".4f")
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), yaxis=dict(autorange="reversed"),
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("SHAP value distribution")
    st.caption("Each dot = one employee. Right = pushed toward attrition; Left = pushed away.")
    top_features = df["Factor"].tolist()[:15]
    feature_indices = [result.feature_names.index(f) for f in top_features]
    rows = []
    X_arr = result.X_test_sample.values
    for fi, feat in zip(feature_indices, top_features):
        shap_col = result.shap_values[:, fi]
        feat_col = X_arr[:, fi].astype(float)
        fmin, fmax = feat_col.min(), feat_col.max()
        feat_norm = (feat_col - fmin) / (fmax - fmin + 1e-9)
        for sv, fn in zip(shap_col, feat_norm):
            rows.append({"Factor": feat, "SHAP value": float(sv), "Feature value (norm)": float(fn)})

    bees_df = pd.DataFrame(rows)
    fig2 = px.scatter(bees_df, x="SHAP value", y="Factor",
                      color="Feature value (norm)",
                      color_continuous_scale=[[0, "#e0f2fe"], [0.5, "#67e8f9"], [1, "#0d9488"]])
    fig2.update_traces(marker=dict(size=4, opacity=0.6))
    fig2.update_layout(margin=dict(l=10, r=10, t=20, b=10),
                       yaxis=dict(autorange="reversed", categoryorder="array",
                                  categoryarray=list(reversed(top_features))),
                       xaxis_title="SHAP value (impact on attrition prediction)")
    fig2.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1)
    st.plotly_chart(fig2, use_container_width=True)

    with st.container(border=True):
        st.markdown("**Reading this chart**")
        st.markdown(
            "- **Right of 0** → factor increases attrition probability\n"
            "- **Left of 0** → factor decreases attrition probability\n"
            "- **Colour** → high feature value (teal) vs low (light blue)"
        )


def _render_local_shap(result: ExplainResult, train_result) -> None:
    st.subheader("Why is this employee flagged as a flight risk?")
    st.caption("Select a test instance to see which factors drove the prediction.")

    n = len(result.X_test_sample)
    row_idx = st.slider("Employee index (test set)", 0, n - 1, 0, key="hr_xai_shap_row")

    instance = result.X_test_sample.iloc[row_idx]
    shap_row = result.shap_values[row_idx]
    prediction = train_result.model.predict(instance.values.reshape(1, -1))[0]
    proba = train_result.model.predict_proba(instance.values.reshape(1, -1))[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Prediction", str(prediction))
    c2.metric("Confidence", f"{proba.max():.1%}")
    c3.metric("Baseline", f"{result.shap_base_value:.4f}")

    top_n = min(15, len(result.feature_names))
    order = np.argsort(np.abs(shap_row))[::-1][:top_n]
    top_features = [result.feature_names[i] for i in order]
    top_shap = [shap_row[i] for i in order]

    wf_df = pd.DataFrame({
        "Factor": top_features, "SHAP value": top_shap,
        "Direction": ["Increases risk" if v >= 0 else "Decreases risk" for v in top_shap],
    }).sort_values("SHAP value")

    fig = px.bar(wf_df, x="SHAP value", y="Factor", orientation="h",
                 color="Direction",
                 color_discrete_map={"Increases risk": CHART_NEG, "Decreases risk": CHART_POS},
                 text_auto=".4f")
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1)
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Employee factor values"):
        inst_df = pd.DataFrame({
            "Factor": result.feature_names,
            "Value": instance.values,
            "SHAP": result.shap_values[row_idx],
        }).sort_values("SHAP", key=abs, ascending=False).head(top_n)
        st.dataframe(inst_df.style.format({"Value": "{:.4g}", "SHAP": "{:.4f}"}),
                     hide_index=True, use_container_width=True)


def _render_local_lime(result: ExplainResult, train_result) -> None:
    st.subheader("LIME — linear approximation for one employee")
    st.caption("LIME fits a simple linear model near the selected employee by perturbing inputs.")

    n = len(result.X_test_sample)
    row_idx = st.slider("Employee index (test set)", 0, n - 1, 0, key="hr_xai_lime_row")

    instance = result.X_test_sample.iloc[row_idx]
    prediction = train_result.model.predict(instance.values.reshape(1, -1))[0]
    proba = train_result.model.predict_proba(instance.values.reshape(1, -1))[0]

    c1, c2 = st.columns(2)
    c1.metric("Prediction", str(prediction))
    c2.metric("Confidence", f"{proba.max():.1%}")

    num_features = st.slider("Factors to show", 5, min(20, len(result.feature_names)), 10, key="hr_xai_lime_nf")

    with st.spinner("Computing LIME…"):
        try:
            contributions = explain_instance_lime(result, train_result.model, row_idx, num_features)
        except Exception as exc:
            st.error(f"LIME failed: {exc}")
            return

    lime_df = pd.DataFrame(contributions, columns=["Factor condition", "Weight"])
    lime_df["Direction"] = lime_df["Weight"].apply(lambda w: "Increases risk" if w >= 0 else "Decreases risk")

    fig = px.bar(lime_df.sort_values("Weight"), x="Weight", y="Factor condition", orientation="h",
                 color="Direction",
                 color_discrete_map={"Increases risk": CHART_NEG, "Decreases risk": CHART_POS},
                 text_auto=".4f")
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1)
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        st.markdown("**Reading LIME**")
        st.markdown(
            "- Each bar is a factor **condition** (e.g. `OverTime = Yes`)\n"
            "- **Red / right** → condition increases attrition risk\n"
            "- **Green / left** → condition decreases attrition risk\n"
            "- LIME only explains **this one** employee — other employees may differ"
        )
