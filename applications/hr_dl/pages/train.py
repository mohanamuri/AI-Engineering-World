import streamlit as st
import plotly.express as px
import pandas as pd

from applications.hr_dl.constants import (
    PREPROCESS_RESULT_SESSION_KEY, TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_dl.services.trainer import ARCHITECTURES, DLTrainingError, train
from applications.shared.api_reference import render_api_reference


def render():
    st.header("🧠 Train Neural Network")

    preprocess_result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if preprocess_result is None:
        st.warning("Complete preprocessing first.")
        return

    st.subheader("Architecture")
    arch = st.selectbox("Hidden layers", list(ARCHITECTURES.keys()), index=1)
    sizes = ARCHITECTURES[arch]

    _render_architecture_diagram(sizes)

    st.subheader("Hyperparameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        activation = st.selectbox("Activation", ["relu", "tanh", "logistic"], index=0)
        solver = st.selectbox("Solver", ["adam", "sgd", "lbfgs"], index=0)
    with col2:
        lr = st.number_input("Learning rate", 0.0001, 0.1, 0.001, 0.0001, format="%.4f")
        alpha = st.number_input("L2 regularisation (alpha)", 0.0, 1.0, 0.0001, 0.0001, format="%.4f")
    with col3:
        max_iter = st.slider("Max epochs", 50, 1000, 200, 50)

    st.info("Sample weights are applied to balance the attrition minority class during training.")

    if st.button("Train Neural Network", use_container_width=True):
        with st.spinner(f"Training MLP {sizes}…"):
            try:
                result = train(
                    preprocess_result.X_train, preprocess_result.y_train,
                    preprocess_result.X_test, preprocess_result.y_test,
                    arch, activation, solver, lr, max_iter, alpha,
                )
            except DLTrainingError as exc:
                st.error(f"Training failed: {exc}")
                return
        st.session_state[TRAIN_RESULT_SESSION_KEY] = result
        st.success(f"Trained **{result.model_name}** in {result.training_time_seconds:.3f}s — {result.n_iter} epochs.")

    result = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    if result is None:
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Train accuracy", f"{result.train_accuracy:.3f}")
    c2.metric("Test accuracy", f"{result.test_accuracy:.3f}")
    c3.metric("Epochs run", str(result.n_iter))
    c4.metric("Train time", f"{result.training_time_seconds:.2f}s")

    if result.loss_curve:
        st.subheader("Training loss curve")
        loss_df = pd.DataFrame({"Epoch": range(1, len(result.loss_curve) + 1), "Loss": result.loss_curve})
        fig = px.line(loss_df, x="Epoch", y="Loss", color_discrete_sequence=["#7c3aed"])
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Loss decreasing towards zero = model is learning. "
            "A plateau = learning rate may be too small or the model is stuck."
        )
    else:
        st.info("Loss curve not recorded (lbfgs solver doesn't track per-epoch loss).")
    render_api_reference("hr_dl", "train")


def _render_architecture_diagram(sizes: tuple) -> None:
    parts = ["Input"] + [f"Dense({s}, ReLU)" for s in sizes] + ["Output (Softmax)"]
    st.markdown(" → ".join(f"`{p}`" for p in parts))
