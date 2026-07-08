"""Train page for the loan eligibility XAI pipeline.

Reuses loan_ml's trainer service. Tree-based models (RF, XGBoost) are
recommended here as SHAP TreeExplainer is exact and fast for them.
"""

from __future__ import annotations

import streamlit as st

from applications.loan_xai.constants import (
    EXPLAIN_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_ml.services.preprocessor import PreprocessResult
from applications.loan_ml.services.trainer import (
    SUPPORTED_MODELS,
    TrainResult,
    TrainingError,
    get_hyperparameter_defaults,
    train,
)
from applications.shared.api_reference import render_api_reference

_PREPROCESS_PAGE = "🧹 Preprocess"


def render() -> None:
    st.header("🤖 Train Model")
    st.caption(
        "Train a classifier before generating explanations. "
        "Random Forest and XGBoost work best with SHAP TreeExplainer — exact and fast."
    )

    result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if not isinstance(result, PreprocessResult):
        with st.container(border=True):
            st.warning("Preprocessing not complete.")
            st.button("← Go to Preprocess", type="primary",
                      on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _PREPROCESS_PAGE}))
        return

    model_name, hyperparams = _render_panel()
    st.divider()

    if st.button("Train Model", type="primary", use_container_width=True):
        # Invalidate any cached explanations when model changes
        st.session_state.pop(EXPLAIN_RESULT_SESSION_KEY, None)
        with st.spinner(f"Training {model_name}…"):
            try:
                train_result = train(
                    X_train=result.X_train, y_train=result.y_train,
                    X_test=result.X_test, y_test=result.y_test,
                    model_name=model_name, hyperparams=hyperparams,
                )
            except TrainingError as exc:
                st.error(f"Training failed: {exc}")
                return
        st.session_state[TRAIN_RESULT_SESSION_KEY] = train_result
        st.success(
            f"**{model_name}** trained in {train_result.training_time_seconds:.2f}s — "
            f"Test accuracy: **{train_result.test_accuracy:.1%}**"
        )

    train_result: TrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    if train_result is not None:
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Train accuracy", f"{train_result.train_accuracy:.1%}")
        m2.metric("Test accuracy", f"{train_result.test_accuracy:.1%}")
        m3.metric("Overfit gap", f"{train_result.train_accuracy - train_result.test_accuracy:.1%}")
        m4.metric("Training time", f"{train_result.training_time_seconds:.2f}s")
        st.info("Model trained. Proceed to **Explain** to generate SHAP and LIME explanations.", icon="✅")
    render_api_reference("loan_xai", "train")


def _render_panel() -> tuple[str, dict]:
    model_name = st.selectbox(
        "Classifier",
        options=SUPPORTED_MODELS,
        index=2,  # Default: Random Forest — best SHAP compatibility
        key="loan_xai_model_name",
        help="Random Forest and XGBoost use fast SHAP TreeExplainer. Logistic Regression uses LinearExplainer.",
    )

    explainer_map = {
        "Logistic Regression": ("LinearExplainer", "fast, exact"),
        "Decision Tree": ("TreeExplainer", "fast, exact"),
        "Random Forest": ("TreeExplainer", "fast, exact"),
        "XGBoost": ("TreeExplainer", "fast, exact"),
    }
    exp_name, exp_note = explainer_map.get(model_name, ("KernelExplainer", "slow, approximate"))
    st.info(f"SHAP explainer for **{model_name}**: `{exp_name}` — {exp_note}", icon="ℹ️")

    defaults = get_hyperparameter_defaults(model_name)
    c1, c2 = st.columns(2)

    if model_name == "Logistic Regression":
        with c1:
            with st.container(border=True):
                C = st.slider("C — Regularisation", 0.01, 10.0, float(defaults["C"]), 0.01, key="loan_xai_hp_C")
        with c2:
            with st.container(border=True):
                max_iter = st.slider("Max iterations", 100, 2000, int(defaults["max_iter"]), 100, key="loan_xai_hp_iter")
        return model_name, {"C": C, "max_iter": max_iter, "solver": "lbfgs"}

    if model_name == "Decision Tree":
        with c1:
            with st.container(border=True):
                max_depth = st.slider("Max depth", 1, 20, int(defaults["max_depth"]), key="loan_xai_hp_dt_depth")
        with c2:
            with st.container(border=True):
                min_samples_leaf = st.slider("Min samples/leaf", 1, 50, int(defaults["min_samples_leaf"]), key="loan_xai_hp_dt_leaf")
        return model_name, {"max_depth": max_depth, "min_samples_split": defaults["min_samples_split"], "min_samples_leaf": min_samples_leaf}

    if model_name == "Random Forest":
        with c1:
            with st.container(border=True):
                n_est = st.slider("Trees", 10, 500, int(defaults["n_estimators"]), 10, key="loan_xai_hp_rf_n")
        with c2:
            with st.container(border=True):
                max_depth = st.slider("Max depth", 1, 30, int(defaults["max_depth"]), key="loan_xai_hp_rf_depth")
        return model_name, {"n_estimators": n_est, "max_depth": max_depth, "min_samples_split": defaults["min_samples_split"]}

    if model_name == "XGBoost":
        with c1:
            with st.container(border=True):
                n_est = st.slider("Trees", 10, 500, int(defaults["n_estimators"]), 10, key="loan_xai_hp_xgb_n")
            with st.container(border=True):
                lr = st.slider("Learning rate", 0.01, 0.5, float(defaults["learning_rate"]), 0.01, key="loan_xai_hp_xgb_lr")
        with c2:
            with st.container(border=True):
                max_depth = st.slider("Max depth", 1, 10, int(defaults["max_depth"]), key="loan_xai_hp_xgb_depth")
        return model_name, {"n_estimators": n_est, "learning_rate": lr, "max_depth": max_depth}

    return model_name, defaults
