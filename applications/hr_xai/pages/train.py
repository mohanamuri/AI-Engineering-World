import streamlit as st
from applications.hr_xai.constants import (
    PREPROCESS_RESULT_SESSION_KEY, TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_ml.services.trainer import SUPPORTED_MODELS, TrainingError, get_hyperparameter_defaults, train
from applications.shared.api_reference import render_api_reference


def render():
    st.header("🤖 Train Model")
    preprocess_result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    if preprocess_result is None:
        st.warning("Complete preprocessing first.")
        return

    model_name = st.selectbox("Select model", SUPPORTED_MODELS)
    defaults = get_hyperparameter_defaults(model_name)

    col1, col2 = st.columns(2)
    params = {}
    if model_name == "Logistic Regression":
        with col1:
            params["C"] = st.number_input("C", 0.001, 100.0, float(defaults["C"]))
            params["max_iter"] = st.number_input("max_iter", 100, 5000, int(defaults["max_iter"]))
        with col2:
            params["solver"] = st.selectbox("Solver", ["lbfgs", "liblinear", "saga"])
    elif model_name == "Decision Tree":
        with col1:
            params["max_depth"] = st.slider("max_depth", 1, 20, int(defaults["max_depth"]))
        with col2:
            params["min_samples_split"] = st.slider("min_samples_split", 2, 50, int(defaults["min_samples_split"]))
            params["min_samples_leaf"] = st.slider("min_samples_leaf", 1, 20, int(defaults["min_samples_leaf"]))
    elif model_name == "Random Forest":
        with col1:
            params["n_estimators"] = st.slider("n_estimators", 10, 300, int(defaults["n_estimators"]))
            params["max_depth"] = st.slider("max_depth", 1, 30, int(defaults["max_depth"]))
        with col2:
            params["min_samples_split"] = st.slider("min_samples_split", 2, 20, int(defaults["min_samples_split"]))
    elif model_name == "XGBoost":
        with col1:
            params["n_estimators"] = st.slider("n_estimators", 10, 300, int(defaults["n_estimators"]))
            params["learning_rate"] = st.number_input("learning_rate", 0.01, 1.0, float(defaults["learning_rate"]), 0.01)
        with col2:
            params["max_depth"] = st.slider("max_depth", 1, 10, int(defaults["max_depth"]))
            params["scale_pos_weight"] = st.slider("scale_pos_weight", 1, 10, 5)

    st.info("Note: Tree models (Random Forest, XGBoost, Decision Tree) work best with SHAP TreeExplainer.")

    if st.button("Train", use_container_width=True):
        with st.spinner(f"Training {model_name}…"):
            try:
                result = train(preprocess_result.X_train, preprocess_result.y_train,
                               preprocess_result.X_test, preprocess_result.y_test,
                               model_name, params)
            except TrainingError as exc:
                st.error(str(exc))
                return
        st.session_state[TRAIN_RESULT_SESSION_KEY] = result
        st.success(f"Trained **{model_name}** in {result.training_time_seconds:.3f}s.")

    result = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    if result:
        c1, c2 = st.columns(2)
        c1.metric("Train accuracy", f"{result.train_accuracy:.3f}")
        c2.metric("Test accuracy", f"{result.test_accuracy:.3f}")
    render_api_reference("hr_xai", "train")
