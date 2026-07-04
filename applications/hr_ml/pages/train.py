import streamlit as st

from applications.hr_ml.constants import (
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_ml.services.trainer import (
    SUPPORTED_MODELS,
    TrainingError,
    get_hyperparameter_defaults,
    train,
)


def render():
    st.header("🤖 Train Model")

    preprocess_result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if preprocess_result is None:
        st.warning("Complete preprocessing first.")
        return

    model_name = st.selectbox("Select model", SUPPORTED_MODELS)
    defaults = get_hyperparameter_defaults(model_name)

    st.subheader("Hyperparameters")
    hyperparams = _render_hyperparams(model_name, defaults)

    st.info(
        "All models use **class_weight='balanced'** to handle attrition class imbalance. "
        "This re-weights training samples so the minority class (Yes) is not ignored."
    )

    if st.button("Train", use_container_width=True):
        with st.spinner(f"Training {model_name}…"):
            try:
                result = train(
                    preprocess_result.X_train,
                    preprocess_result.y_train,
                    preprocess_result.X_test,
                    preprocess_result.y_test,
                    model_name,
                    hyperparams,
                )
            except TrainingError as exc:
                st.error(f"Training failed: {exc}")
                return

        st.session_state[TRAIN_RESULT_SESSION_KEY] = result
        st.success(f"Trained **{model_name}** in {result.training_time_seconds:.3f}s.")

    result = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    if result is None:
        return

    st.subheader("Training summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Train accuracy", f"{result.train_accuracy:.3f}")
    c2.metric("Test accuracy", f"{result.test_accuracy:.3f}")
    c3.metric("Training time", f"{result.training_time_seconds:.3f}s")

    gap = result.train_accuracy - result.test_accuracy
    if gap > 0.15:
        st.warning(f"Train–test gap is {gap:.3f} — the model may be overfitting. Try reducing max_depth or increasing regularisation.")
    elif gap < 0.01:
        st.info("Train and test accuracy are nearly identical — the model generalises well.")
    else:
        st.success(f"Reasonable train–test gap of {gap:.3f}.")


def _render_hyperparams(model_name: str, defaults: dict) -> dict:
    params = {}
    col1, col2 = st.columns(2)

    if model_name == "Logistic Regression":
        with col1:
            params["C"] = st.number_input("C (regularisation)", 0.001, 100.0, float(defaults["C"]), 0.1)
            params["max_iter"] = st.number_input("max_iter", 100, 5000, int(defaults["max_iter"]), 100)
        with col2:
            params["solver"] = st.selectbox("Solver", ["lbfgs", "liblinear", "saga"])

    elif model_name == "Decision Tree":
        with col1:
            params["max_depth"] = st.slider("max_depth", 1, 20, int(defaults["max_depth"]))
            params["min_samples_split"] = st.slider("min_samples_split", 2, 50, int(defaults["min_samples_split"]))
        with col2:
            params["min_samples_leaf"] = st.slider("min_samples_leaf", 1, 20, int(defaults["min_samples_leaf"]))

    elif model_name == "Random Forest":
        with col1:
            params["n_estimators"] = st.slider("n_estimators", 10, 500, int(defaults["n_estimators"]), 10)
            params["max_depth"] = st.slider("max_depth", 1, 30, int(defaults["max_depth"]))
        with col2:
            params["min_samples_split"] = st.slider("min_samples_split", 2, 20, int(defaults["min_samples_split"]))

    elif model_name == "XGBoost":
        with col1:
            params["n_estimators"] = st.slider("n_estimators", 10, 500, int(defaults["n_estimators"]), 10)
            params["learning_rate"] = st.number_input("learning_rate", 0.01, 1.0, float(defaults["learning_rate"]), 0.01)
        with col2:
            params["max_depth"] = st.slider("max_depth", 1, 15, int(defaults["max_depth"]))
            params["scale_pos_weight"] = st.slider("scale_pos_weight", 1, 10, 5,
                help="Ratio of negative:positive samples. Adjust to match your dataset's class balance.")

    return params
