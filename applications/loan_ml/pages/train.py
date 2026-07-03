"""Model training page for the loan eligibility ML pipeline.

Renders model selection and hyperparameter controls, then calls the
trainer service and stores the TrainResult in session state.
"""

from __future__ import annotations

import streamlit as st

from applications.loan_ml.constants import (
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

_PREPROCESS_PAGE_LABEL = "🧹 Preprocess"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    st.header("🤖 Train Model")
    st.caption(
        "Select a classifier and tune its hyperparameters. "
        "The model is trained on the preprocessed training split only."
    )

    result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if not isinstance(result, PreprocessResult):
        _render_empty_state()
        return

    model_name, hyperparams = _render_model_panel()

    st.divider()

    if st.button("Train Model", type="primary", use_container_width=True):
        _run_training(result, model_name, hyperparams)

    train_result: TrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    if train_result is not None:
        st.divider()
        _render_results(train_result)


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("Preprocessing not complete.")
        st.write("Run the preprocessing pipeline before training a model.")
        st.button(
            "← Go to Preprocess",
            type="primary",
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: _PREPROCESS_PAGE_LABEL}
            ),
        )


# ---------------------------------------------------------------------------
# Model selection + hyperparameter panel
# ---------------------------------------------------------------------------

def _render_model_panel() -> tuple[str, dict]:
    st.subheader("Model selection")

    model_name = st.selectbox(
        "Classifier",
        options=SUPPORTED_MODELS,
        index=2,  # Default: Random Forest
        key="loan_ml_model_name",
        help="Each model represents a different learning strategy.",
    )

    _render_model_explainer(model_name)

    st.markdown("#### Hyperparameters")
    hyperparams = _render_hyperparams(model_name)

    return model_name, hyperparams


def _render_model_explainer(model_name: str) -> None:
    explainers = {
        "Logistic Regression": (
            "**Linear model.** Learns a decision boundary as a weighted sum of features. "
            "Fast, interpretable, and a strong baseline. Works best when the relationship "
            "between features and target is approximately linear."
        ),
        "Decision Tree": (
            "**Rule-based model.** Splits data on feature thresholds to form a tree of "
            "if-else rules. Fully interpretable but prone to overfitting on deep trees. "
            "`max_depth` is the primary control."
        ),
        "Random Forest": (
            "**Bagging ensemble.** Trains many decision trees on bootstrap samples and "
            "averages their predictions. Robust to overfitting, handles missing values "
            "gracefully, and provides reliable feature importances."
        ),
        "XGBoost": (
            "**Boosting ensemble.** Builds trees sequentially, each correcting the errors "
            "of the previous. State-of-the-art on tabular data. `learning_rate` controls "
            "the contribution of each tree — lower is slower but more accurate."
        ),
    }
    st.info(explainers.get(model_name, ""), icon="ℹ️")


def _render_hyperparams(model_name: str) -> dict:
    defaults = get_hyperparameter_defaults(model_name)

    hp_col1, hp_col2 = st.columns(2)

    if model_name == "Logistic Regression":
        with hp_col1:
            with st.container(border=True):
                C = st.slider(
                    "C — Regularisation strength",
                    min_value=0.01, max_value=10.0,
                    value=float(defaults["C"]), step=0.01,
                    key="loan_ml_hp_C",
                    help="Lower C = stronger regularisation (less overfitting).",
                )
        with hp_col2:
            with st.container(border=True):
                max_iter = st.slider(
                    "Max iterations",
                    min_value=100, max_value=2000,
                    value=int(defaults["max_iter"]), step=100,
                    key="loan_ml_hp_max_iter",
                    help="Increase if the solver warns about convergence.",
                )
        return {"C": C, "max_iter": max_iter, "solver": "lbfgs"}

    if model_name == "Decision Tree":
        with hp_col1:
            with st.container(border=True):
                max_depth = st.slider(
                    "Max depth",
                    min_value=1, max_value=20,
                    value=int(defaults["max_depth"]),
                    key="loan_ml_hp_dt_depth",
                    help="Deeper trees overfit. Start at 5 and increase.",
                )
        with hp_col2:
            with st.container(border=True):
                min_samples_leaf = st.slider(
                    "Min samples per leaf",
                    min_value=1, max_value=50,
                    value=int(defaults["min_samples_leaf"]),
                    key="loan_ml_hp_dt_leaf",
                    help="Higher values smooth the decision boundary.",
                )
        return {
            "max_depth": max_depth,
            "min_samples_split": defaults["min_samples_split"],
            "min_samples_leaf": min_samples_leaf,
        }

    if model_name == "Random Forest":
        with hp_col1:
            with st.container(border=True):
                n_estimators = st.slider(
                    "Number of trees",
                    min_value=10, max_value=500,
                    value=int(defaults["n_estimators"]), step=10,
                    key="loan_ml_hp_rf_n",
                    help="More trees = lower variance, slower training.",
                )
        with hp_col2:
            with st.container(border=True):
                max_depth = st.slider(
                    "Max tree depth",
                    min_value=1, max_value=30,
                    value=int(defaults["max_depth"]),
                    key="loan_ml_hp_rf_depth",
                    help="None = fully grown trees. Limit to reduce overfitting.",
                )
        return {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_split": defaults["min_samples_split"],
        }

    if model_name == "XGBoost":
        with hp_col1:
            with st.container(border=True):
                n_estimators = st.slider(
                    "Number of trees",
                    min_value=10, max_value=500,
                    value=int(defaults["n_estimators"]), step=10,
                    key="loan_ml_hp_xgb_n",
                )
            with st.container(border=True):
                learning_rate = st.slider(
                    "Learning rate",
                    min_value=0.01, max_value=0.5,
                    value=float(defaults["learning_rate"]), step=0.01,
                    key="loan_ml_hp_xgb_lr",
                    help="Lower = each tree contributes less. Reduces overfitting.",
                )
        with hp_col2:
            with st.container(border=True):
                max_depth = st.slider(
                    "Max tree depth",
                    min_value=1, max_value=10,
                    value=int(defaults["max_depth"]),
                    key="loan_ml_hp_xgb_depth",
                )
        return {
            "n_estimators": n_estimators,
            "learning_rate": learning_rate,
            "max_depth": max_depth,
        }

    return defaults


# ---------------------------------------------------------------------------
# Run & store
# ---------------------------------------------------------------------------

def _run_training(
    preprocess_result: PreprocessResult,
    model_name: str,
    hyperparams: dict,
) -> None:
    with st.spinner(f"Training {model_name}…"):
        try:
            result = train(
                X_train=preprocess_result.X_train,
                y_train=preprocess_result.y_train,
                X_test=preprocess_result.X_test,
                y_test=preprocess_result.y_test,
                model_name=model_name,
                hyperparams=hyperparams,
            )
        except TrainingError as exc:
            st.error(f"Training failed: {exc}")
            return

    st.session_state[TRAIN_RESULT_SESSION_KEY] = result
    st.success(
        f"**{model_name}** trained in {result.training_time_seconds:.2f}s — "
        f"Test accuracy: **{result.test_accuracy:.1%}**"
    )


# ---------------------------------------------------------------------------
# Results panel
# ---------------------------------------------------------------------------

def _render_results(result: TrainResult) -> None:
    st.subheader(f"Results — {result.model_name}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Train accuracy", f"{result.train_accuracy:.1%}")
    m2.metric("Test accuracy", f"{result.test_accuracy:.1%}")
    m3.metric(
        "Overfit gap",
        f"{(result.train_accuracy - result.test_accuracy):.1%}",
        help="Train − Test accuracy. Values above 10% suggest overfitting.",
    )
    m4.metric("Training time", f"{result.training_time_seconds:.2f}s")

    gap = result.train_accuracy - result.test_accuracy
    if gap > 0.15:
        st.warning(
            f"Overfit gap is {gap:.1%}. Try reducing `max_depth`, increasing "
            "`min_samples_leaf`, or adding more regularisation.",
            icon="⚠️",
        )
    elif gap < 0.0:
        st.info(
            "Test accuracy exceeds train accuracy — this can happen with small "
            "datasets and stratified splits. Evaluate on more data if possible.",
            icon="ℹ️",
        )
    else:
        st.success(
            "The model generalises well. Proceed to **Evaluate Model** for full metrics.",
            icon="✅",
        )
