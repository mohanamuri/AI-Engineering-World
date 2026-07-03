"""Neural network training page for the loan eligibility DL pipeline.

Exposes architecture selection, activation function, solver, learning rate,
regularisation, and epoch count. After training, shows the loss curve — the
signature deep-learning artifact that distinguishes this tier from loan_ml.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from applications.loan_dl.constants import (
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_dl.services.trainer import (
    ARCHITECTURES,
    DLTrainResult,
    DLTrainingError,
    train,
)
from applications.loan_ml.services.preprocessor import PreprocessResult

CHART_COLOR = "#0891b2"
_PREPROCESS_PAGE_LABEL = "🧹 Preprocess"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    st.header("🧠 Train Neural Network")
    st.caption(
        "Configure a multi-layer perceptron (MLP) and train it on the "
        "preprocessed data. Inspect the loss curve to diagnose convergence."
    )

    result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if not isinstance(result, PreprocessResult):
        _render_empty_state()
        return

    arch_name, activation, solver, lr_init, max_iter, alpha = _render_config_panel(result)
    st.divider()

    if st.button("Train Neural Network", type="primary", use_container_width=True):
        _run_training(result, arch_name, activation, solver, lr_init, max_iter, alpha)

    train_result: DLTrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    if train_result is not None:
        st.divider()
        _render_results(train_result)


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("Preprocessing not complete.")
        st.write("Run the preprocessing pipeline before training a neural network.")
        st.button(
            "← Go to Preprocess",
            type="primary",
            on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _PREPROCESS_PAGE_LABEL}),
        )


# ---------------------------------------------------------------------------
# Configuration panel
# ---------------------------------------------------------------------------

def _render_config_panel(preprocess_result: PreprocessResult) -> tuple:
    n_features = len(preprocess_result.feature_names)
    n_classes = len(preprocess_result.class_labels)

    with st.container(border=True):
        st.markdown(
            f"**Input:** {n_features} features &nbsp;·&nbsp; "
            f"**Output:** {n_classes} classes"
        )

    st.subheader("Architecture")

    arch_col, act_col = st.columns(2)

    with arch_col:
        with st.container(border=True):
            st.markdown("**Hidden layers**")
            arch_name = st.radio(
                "Architecture",
                options=list(ARCHITECTURES.keys()),
                index=1,
                label_visibility="collapsed",
                key="loan_dl_architecture",
                help=(
                    "Each value is a layer's neuron count. "
                    "More layers = more representational capacity, but harder to train."
                ),
            )
            hidden = ARCHITECTURES[arch_name]
            arch_str = " → ".join(str(h) for h in hidden)
            st.caption(f"Input({n_features}) → {arch_str} → Output({n_classes})")

    with act_col:
        with st.container(border=True):
            st.markdown("**Activation function**")
            activation = st.radio(
                "Activation",
                options=["relu", "tanh", "logistic"],
                index=0,
                label_visibility="collapsed",
                key="loan_dl_activation",
                help=(
                    "relu: most common, avoids vanishing gradient. "
                    "tanh: zero-centred, good for normalised data. "
                    "logistic: sigmoid, saturates for large inputs."
                ),
            )

    st.subheader("Optimiser")

    solver_col, lr_col = st.columns(2)

    with solver_col:
        with st.container(border=True):
            st.markdown("**Solver**")
            solver = st.radio(
                "Solver",
                options=["adam", "sgd", "lbfgs"],
                index=0,
                label_visibility="collapsed",
                key="loan_dl_solver",
                help=(
                    "adam: adaptive learning rate, best default. "
                    "sgd: stochastic gradient descent, manual lr tuning needed. "
                    "lbfgs: quasi-Newton, faster for small datasets but no loss curve."
                ),
            )

    with lr_col:
        with st.container(border=True):
            st.markdown("**Initial learning rate**")
            lr_init = st.select_slider(
                "Learning rate",
                options=[0.0001, 0.001, 0.005, 0.01, 0.05, 0.1],
                value=0.001,
                label_visibility="collapsed",
                key="loan_dl_lr",
                help="Adam adjusts this automatically per parameter. Lower = safer but slower.",
            )

    st.subheader("Training budget & regularisation")

    epoch_col, alpha_col = st.columns(2)

    with epoch_col:
        with st.container(border=True):
            st.markdown("**Max epochs**")
            max_iter = st.slider(
                "Max epochs",
                min_value=50, max_value=1000, value=200, step=50,
                label_visibility="collapsed",
                key="loan_dl_max_iter",
                help="Training stops early if the loss converges before this limit.",
            )

    with alpha_col:
        with st.container(border=True):
            st.markdown("**L2 regularisation (alpha)**")
            alpha = st.select_slider(
                "Alpha",
                options=[1e-5, 1e-4, 1e-3, 0.01, 0.1, 1.0],
                value=1e-4,
                label_visibility="collapsed",
                key="loan_dl_alpha",
                help="Higher alpha = stronger weight decay = less overfitting.",
            )

    return arch_name, activation, solver, lr_init, max_iter, alpha


# ---------------------------------------------------------------------------
# Run & store
# ---------------------------------------------------------------------------

def _run_training(
    preprocess_result: PreprocessResult,
    arch_name: str,
    activation: str,
    solver: str,
    lr_init: float,
    max_iter: int,
    alpha: float,
) -> None:
    with st.spinner("Training neural network… (this may take a moment)"):
        try:
            result = train(
                X_train=preprocess_result.X_train,
                y_train=preprocess_result.y_train,
                X_test=preprocess_result.X_test,
                y_test=preprocess_result.y_test,
                architecture_name=arch_name,
                activation=activation,
                solver=solver,
                learning_rate_init=lr_init,
                max_iter=max_iter,
                alpha=alpha,
            )
        except DLTrainingError as exc:
            st.error(f"Training failed: {exc}")
            return

    st.session_state[TRAIN_RESULT_SESSION_KEY] = result
    st.success(
        f"**{result.model_name}** trained in {result.training_time_seconds:.2f}s over "
        f"**{result.n_iter} epochs** — Test accuracy: **{result.test_accuracy:.1%}**"
    )


# ---------------------------------------------------------------------------
# Results panel
# ---------------------------------------------------------------------------

def _render_results(result: DLTrainResult) -> None:
    st.subheader(f"Results — {result.model_name}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Train accuracy", f"{result.train_accuracy:.1%}")
    m2.metric("Test accuracy", f"{result.test_accuracy:.1%}")
    m3.metric(
        "Overfit gap",
        f"{(result.train_accuracy - result.test_accuracy):.1%}",
        help="Train − Test. Values above 10% suggest overfitting.",
    )
    m4.metric("Training time", f"{result.training_time_seconds:.2f}s")
    m5.metric("Epochs", str(result.n_iter))

    gap = result.train_accuracy - result.test_accuracy
    if gap > 0.15:
        st.warning(
            f"Overfit gap is {gap:.1%}. Try increasing `alpha`, reducing the "
            "architecture size, or collecting more data.",
            icon="⚠️",
        )
    elif gap < 0.0:
        st.info(
            "Test accuracy exceeds train — common with small datasets. "
            "Evaluate on more data if possible.",
            icon="ℹ️",
        )
    else:
        st.success("The network generalises well. Proceed to **Evaluate Model**.", icon="✅")

    # --- Loss curve (unique DL artifact) ---
    if result.loss_curve:
        st.divider()
        st.subheader("Training loss curve")
        st.caption(
            "Shows how the cross-entropy loss decreased across epochs. "
            "A smooth, monotonically decreasing curve indicates stable convergence. "
            "Oscillations suggest the learning rate is too high."
        )
        loss_df = pd.DataFrame({"Epoch": range(1, len(result.loss_curve) + 1), "Loss": result.loss_curve})
        figure = px.line(
            loss_df, x="Epoch", y="Loss",
            color_discrete_sequence=[CHART_COLOR],
            labels={"Loss": "Cross-Entropy Loss"},
        )
        figure.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        figure.update_traces(line=dict(width=2))
        st.plotly_chart(figure, use_container_width=True)
    elif result.hyperparams.get("solver") == "lbfgs":
        st.info(
            "The `lbfgs` solver does not expose a per-epoch loss curve. "
            "Switch to `adam` or `sgd` to see the convergence plot.",
            icon="ℹ️",
        )
