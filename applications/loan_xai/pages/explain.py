"""Explainability dashboard for the loan eligibility XAI pipeline.

Three tabs:
  1. Global — SHAP summary: which features matter most across all predictions
  2. Local SHAP — waterfall chart: why this specific prediction was made
  3. Local LIME — linear approximation: independent local explanation

This is the unique page that differentiates T3 from T1 and T2.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from applications.loan_xai.constants import (
    EXPLAIN_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_xai.services.explainer import (
    ExplainResult,
    ExplainerError,
    build_explanation,
    explain_instance_lime,
)
from applications.loan_ml.services.preprocessor import PreprocessResult
from applications.loan_ml.services.trainer import TrainResult
from applications.shared.api_reference import render_api_reference

CHART_PRIMARY = "#7c3aed"
CHART_POS = "#059669"
CHART_NEG = "#dc2626"
_TRAIN_PAGE = "🤖 Train Model"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    st.header("🔍 Explain Predictions")
    st.caption(
        "Understand *why* the model made each decision. "
        "SHAP gives consistent global + local attributions; "
        "LIME provides fast local linear approximations."
    )

    train_result: TrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)

    if not isinstance(train_result, TrainResult) or not isinstance(preprocess_result, PreprocessResult):
        with st.container(border=True):
            st.warning("No trained model found.")
            st.write("Train a model before generating explanations.")
            st.button("← Go to Train Model", type="primary",
                      on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE}))
        return

    explain_result = _get_or_compute_explanations(train_result, preprocess_result)
    if explain_result is None:
        return

    tab_global, tab_shap_local, tab_lime_local = st.tabs([
        "🌍 Global — SHAP",
        "🔬 Local — SHAP",
        "🔬 Local — LIME",
    ])

    with tab_global:
        _render_global_shap(explain_result)

    with tab_shap_local:
        _render_local_shap(explain_result, train_result, preprocess_result)

    with tab_lime_local:
        _render_local_lime(explain_result, train_result, preprocess_result)
    render_api_reference("loan_xai", "explain")


# ---------------------------------------------------------------------------
# Compute / cache
# ---------------------------------------------------------------------------

def _get_or_compute_explanations(
    train_result: TrainResult,
    preprocess_result: PreprocessResult,
) -> ExplainResult | None:
    cached: ExplainResult | None = st.session_state.get(EXPLAIN_RESULT_SESSION_KEY)
    if isinstance(cached, ExplainResult) and cached.model_name == train_result.model_name:
        return cached

    with st.spinner("Computing SHAP values… (may take 10–30 seconds for large datasets)"):
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
    st.success(
        f"Explanations ready — {len(result.X_test_sample)} instances · "
        f"`{result.explainer_type}` SHAP explainer",
        icon="✅",
    )
    return result


# ---------------------------------------------------------------------------
# Tab 1 — Global SHAP
# ---------------------------------------------------------------------------

def _render_global_shap(result: ExplainResult) -> None:
    st.subheader("Global feature importance — mean |SHAP|")
    st.caption(
        "The average absolute SHAP value across all test instances. "
        "Higher = the feature pushes predictions further from the baseline on average."
    )

    mean_shap = np.abs(result.shap_values).mean(axis=0)
    top_n = min(20, len(result.feature_names))

    df = (
        pd.DataFrame({"Feature": result.feature_names, "Mean |SHAP|": mean_shap})
        .sort_values("Mean |SHAP|", ascending=False)
        .head(top_n)
    )

    fig = px.bar(
        df, x="Mean |SHAP|", y="Feature", orientation="h",
        color="Mean |SHAP|",
        color_continuous_scale=[[0, "#ede9fe"], [1, "#7c3aed"]],
        text_auto=".4f",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("SHAP value distribution — beeswarm (dot plot)")
    st.caption(
        "Each dot is one test instance. Position on X = SHAP value (push toward 1 or 0). "
        "Color = feature value (purple = high, light = low)."
    )

    # Build beeswarm manually with plotly (shap's matplotlib version won't render in Streamlit)
    top_features = df["Feature"].tolist()[:15]
    feature_indices = [result.feature_names.index(f) for f in top_features]

    rows = []
    X_arr = result.X_test_sample.values

    for fi, feat in zip(feature_indices, top_features):
        shap_col = result.shap_values[:, fi]
        feat_col = X_arr[:, fi].astype(float)
        # Normalise feature value to [0,1] for colouring
        feat_min, feat_max = feat_col.min(), feat_col.max()
        feat_norm = (feat_col - feat_min) / (feat_max - feat_min + 1e-9)
        for sv, fn in zip(shap_col, feat_norm):
            rows.append({"Feature": feat, "SHAP value": float(sv), "Feature value (norm)": float(fn)})

    bees_df = pd.DataFrame(rows)
    fig2 = px.scatter(
        bees_df, x="SHAP value", y="Feature",
        color="Feature value (norm)",
        color_continuous_scale=[[0, "#e0f2fe"], [0.5, "#818cf8"], [1, "#7c3aed"]],
    )
    fig2.update_traces(marker=dict(size=4, opacity=0.6))
    fig2.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(autorange="reversed", categoryorder="array", categoryarray=list(reversed(top_features))),
        coloraxis_colorbar=dict(title="Feature<br>value"),
        xaxis_title="SHAP value (impact on model output)",
    )
    fig2.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1)
    st.plotly_chart(fig2, use_container_width=True)

    with st.container(border=True):
        st.markdown("**How to read this chart**")
        st.markdown(
            "- **Right of 0** → feature pushed prediction toward the *positive* class\n"
            "- **Left of 0** → feature pushed prediction toward the *negative* class\n"
            "- **Spread** → high variability in this feature's impact across instances\n"
            "- **Colour** → whether the feature value was high (purple) or low (light blue)"
        )


# ---------------------------------------------------------------------------
# Tab 2 — Local SHAP
# ---------------------------------------------------------------------------

def _render_local_shap(
    result: ExplainResult,
    train_result: TrainResult,
    preprocess_result: PreprocessResult,
) -> None:
    st.subheader("Local SHAP — single prediction waterfall")
    st.caption(
        "Select a test instance and see exactly which features pushed the "
        "prediction up or down from the baseline."
    )

    n = len(result.X_test_sample)
    row_idx = st.slider("Test instance index", 0, n - 1, 0, key="loan_xai_shap_row")

    instance = result.X_test_sample.iloc[row_idx]
    shap_row = result.shap_values[row_idx]
    prediction = train_result.model.predict(instance.values.reshape(1, -1))[0]
    proba = train_result.model.predict_proba(instance.values.reshape(1, -1))[0]

    # Prediction summary
    c1, c2, c3 = st.columns(3)
    c1.metric("Prediction", str(prediction))
    c2.metric("Confidence", f"{proba.max():.1%}")
    c3.metric("SHAP base value", f"{result.shap_base_value:.4f}")

    st.divider()

    # Waterfall: top N features by |SHAP|
    top_n = min(15, len(result.feature_names))
    order = np.argsort(np.abs(shap_row))[::-1][:top_n]
    top_features = [result.feature_names[i] for i in order]
    top_shap = [shap_row[i] for i in order]

    waterfall_df = pd.DataFrame({
        "Feature": top_features,
        "SHAP value": top_shap,
        "Color": ["Positive" if v >= 0 else "Negative" for v in top_shap],
    }).sort_values("SHAP value")

    fig = px.bar(
        waterfall_df,
        x="SHAP value",
        y="Feature",
        orientation="h",
        color="Color",
        color_discrete_map={"Positive": CHART_POS, "Negative": CHART_NEG},
        text_auto=".4f",
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1)
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=True,
        legend=dict(title="Direction"),
        xaxis_title="SHAP value",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show raw feature values for this instance
    st.subheader("Feature values for this instance")
    with st.container(border=True):
        inst_df = pd.DataFrame({
            "Feature": result.feature_names,
            "Value": instance.values,
            "SHAP": result.shap_values[row_idx],
        }).sort_values("SHAP", key=abs, ascending=False).head(top_n)
        st.dataframe(
            inst_df.style.format({"Value": "{:.4g}", "SHAP": "{:.4f}"}),
            hide_index=True,
            width="stretch",
        )


# ---------------------------------------------------------------------------
# Tab 3 — Local LIME
# ---------------------------------------------------------------------------

def _render_local_lime(
    result: ExplainResult,
    train_result: TrainResult,
    preprocess_result: PreprocessResult,
) -> None:
    st.subheader("Local LIME — linear approximation")
    st.caption(
        "LIME fits a simple linear model around the selected instance by "
        "perturbing input values and observing how predictions change."
    )

    n = len(result.X_test_sample)
    row_idx = st.slider("Test instance index", 0, n - 1, 0, key="loan_xai_lime_row")

    instance = result.X_test_sample.iloc[row_idx]
    prediction = train_result.model.predict(instance.values.reshape(1, -1))[0]
    proba = train_result.model.predict_proba(instance.values.reshape(1, -1))[0]

    c1, c2 = st.columns(2)
    c1.metric("Prediction", str(prediction))
    c2.metric("Confidence", f"{proba.max():.1%}")

    st.divider()

    num_features = st.slider("Number of features to show", 5, min(20, len(result.feature_names)), 10, key="loan_xai_lime_nf")

    with st.spinner("Computing LIME explanation…"):
        try:
            contributions = explain_instance_lime(result, train_result.model, row_idx, num_features)
        except Exception as exc:
            st.error(f"LIME explanation failed: {exc}")
            return

    if not contributions:
        st.warning("No contributions returned.")
        return

    lime_df = pd.DataFrame(contributions, columns=["Feature condition", "Weight"])
    lime_df["Direction"] = lime_df["Weight"].apply(lambda w: "Supports" if w >= 0 else "Opposes")

    fig = px.bar(
        lime_df.sort_values("Weight"),
        x="Weight",
        y="Feature condition",
        orientation="h",
        color="Direction",
        color_discrete_map={"Supports": CHART_POS, "Opposes": CHART_NEG},
        text_auto=".4f",
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1)
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(title="Effect on prediction"),
        xaxis_title="LIME weight",
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        st.markdown("**How to read LIME**")
        st.markdown(
            "- Each bar is a feature **condition** (e.g., `income > 5000`)\n"
            "- **Green / right** → this condition supports the predicted class\n"
            "- **Red / left** → this condition argues against the predicted class\n"
            "- LIME only explains this **one** prediction — results may differ for other instances"
        )

    st.divider()
    st.subheader("SHAP vs LIME — same instance")
    st.caption("Both methods should broadly agree on the most important features, even if magnitudes differ.")

    shap_row = result.shap_values[row_idx]
    shap_top = {result.feature_names[i]: shap_row[i] for i in np.argsort(np.abs(shap_row))[::-1][:num_features]}

    # Extract pure feature names from LIME conditions for comparison
    lime_raw = {cond.split(" ")[0]: weight for cond, weight in contributions}

    common = set(shap_top.keys()) & set(lime_raw.keys())
    if common:
        cmp_df = pd.DataFrame([
            {"Feature": f, "SHAP": shap_top[f], "LIME": lime_raw[f]}
            for f in common
        ]).sort_values("SHAP", key=abs, ascending=False)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="SHAP", x=cmp_df["Feature"], y=cmp_df["SHAP"], marker_color=CHART_PRIMARY))
        fig2.add_trace(go.Bar(name="LIME", x=cmp_df["Feature"], y=cmp_df["LIME"], marker_color="#0891b2"))
        fig2.update_layout(
            barmode="group",
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_tickangle=-30,
            yaxis_title="Attribution value",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Feature names differ between SHAP and LIME conditions — comparison not shown.", icon="ℹ️")
