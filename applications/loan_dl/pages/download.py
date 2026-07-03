"""Model export page for the loan eligibility DL pipeline.

Provides in-memory downloads for all pipeline artifacts:
  - Trained MLP model (.pkl via joblib)
  - Fitted preprocessor pipeline (.pkl via joblib)
  - Evaluation metrics (.json)
  - Combined bundle (.pkl) — model + preprocessor + config

No disk writes — all artifacts built in io.BytesIO buffers.
"""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import joblib
import pandas as pd
import streamlit as st

from applications.loan_dl.constants import (
    EVAL_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_dl.services.trainer import DLTrainResult
from applications.loan_ml.services.metrics import EvaluationResult
from applications.loan_ml.services.preprocessor import PreprocessResult

_TRAIN_PAGE_LABEL = "🧠 Train Neural Network"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    st.header("⬇ Download Model")
    st.caption(
        "Export all pipeline artifacts. Package the model and preprocessor "
        "together to guarantee identical transforms at inference time."
    )

    train_result: DLTrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    eval_result: EvaluationResult | None = st.session_state.get(EVAL_RESULT_SESSION_KEY)

    if not isinstance(train_result, DLTrainResult):
        _render_empty_state()
        return

    _render_artifact_summary(train_result, preprocess_result, eval_result)
    st.divider()
    _render_downloads(train_result, preprocess_result, eval_result)
    st.divider()
    _render_usage_snippet(train_result)


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("No trained model found.")
        st.write("Train and evaluate a neural network before downloading artifacts.")
        st.button(
            "← Go to Train Neural Network",
            type="primary",
            on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE_LABEL}),
        )


# ---------------------------------------------------------------------------
# Artifact summary
# ---------------------------------------------------------------------------

def _render_artifact_summary(
    train_result: DLTrainResult,
    preprocess_result: PreprocessResult | None,
    eval_result: EvaluationResult | None,
) -> None:
    st.subheader("Pipeline summary")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Model", "MLPClassifier")
    m2.metric("Architecture", train_result.hyperparams.get("architecture", "N/A"))
    m3.metric("Features", str(len(train_result.feature_names)))
    m4.metric("Test accuracy", f"{train_result.test_accuracy:.1%}")
    m5.metric("Epochs", str(train_result.n_iter))

    if preprocess_result:
        config = preprocess_result.config
        with st.container(border=True):
            st.markdown("**Preprocessing config**")
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"Target: `{config.target_column}`")
            col2.markdown(f"Scaling: `{config.scaling_strategy}`")
            col3.markdown(f"Encoding: `{config.encoding_strategy}`")
            col4.markdown(f"Numeric impute: `{config.numeric_impute_strategy}`")


# ---------------------------------------------------------------------------
# Download buttons
# ---------------------------------------------------------------------------

def _render_downloads(
    train_result: DLTrainResult,
    preprocess_result: PreprocessResult | None,
    eval_result: EvaluationResult | None,
) -> None:
    st.subheader("Artifacts")

    slug = _filename_slug(train_result.model_name)

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### Trained MLP model")
            st.caption(f"`{slug}_model.pkl` · joblib-serialised MLPClassifier.")
            st.download_button(
                label="Download model (.pkl)",
                data=_serialise_joblib(train_result.model),
                file_name=f"{slug}_model.pkl",
                mime="application/octet-stream",
                use_container_width=True,
                key="dl_dl_model",
            )

    with col2:
        with st.container(border=True):
            st.markdown("#### Preprocessing pipeline")
            st.caption(f"`{slug}_preprocessor.pkl` · fitted sklearn Pipeline.")
            if preprocess_result is not None:
                st.download_button(
                    label="Download preprocessor (.pkl)",
                    data=_serialise_joblib(preprocess_result.pipeline),
                    file_name=f"{slug}_preprocessor.pkl",
                    mime="application/octet-stream",
                    use_container_width=True,
                    key="dl_dl_preprocessor",
                )
            else:
                st.info("Preprocessor not available in session.")

    col3, col4 = st.columns(2)

    with col3:
        with st.container(border=True):
            st.markdown("#### Evaluation metrics")
            st.caption(f"`{slug}_metrics.json` · accuracy, F1, ROC AUC.")
            if eval_result is not None:
                st.download_button(
                    label="Download metrics (.json)",
                    data=_serialise_metrics(train_result, eval_result),
                    file_name=f"{slug}_metrics.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_dl_metrics",
                )
            else:
                st.info("Run evaluation first to download metrics.")

    with col4:
        with st.container(border=True):
            st.markdown("#### Loss curve")
            st.caption(f"`{slug}_loss_curve.csv` · training loss per epoch.")
            if train_result.loss_curve:
                loss_df = pd.DataFrame({
                    "epoch": range(1, len(train_result.loss_curve) + 1),
                    "loss": train_result.loss_curve,
                })
                st.download_button(
                    label="Download loss curve (.csv)",
                    data=loss_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"{slug}_loss_curve.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_dl_loss",
                )
            else:
                st.info("Loss curve not available (lbfgs solver).")

    st.markdown("#### Combined bundle")
    with st.container(border=True):
        st.caption(
            f"`{slug}_bundle.pkl` · model + preprocessor + config in one file. "
            "Recommended for deployment."
        )
        if preprocess_result is not None:
            bundle = {
                "model": train_result.model,
                "preprocessor": preprocess_result.pipeline,
                "model_name": train_result.model_name,
                "feature_names": train_result.feature_names,
                "hyperparams": train_result.hyperparams,
                "config": preprocess_result.config,
                "loss_curve": train_result.loss_curve,
                "n_iter": train_result.n_iter,
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            st.download_button(
                label="Download bundle (.pkl)",
                data=_serialise_joblib(bundle),
                file_name=f"{slug}_bundle.pkl",
                mime="application/octet-stream",
                use_container_width=True,
                key="dl_dl_bundle",
            )
        else:
            st.info("Preprocessor required for bundle export.")


# ---------------------------------------------------------------------------
# Usage snippet
# ---------------------------------------------------------------------------

def _render_usage_snippet(train_result: DLTrainResult) -> None:
    st.subheader("How to use these artifacts")

    slug = _filename_slug(train_result.model_name)

    st.code(
        f"""import joblib
import pandas as pd

# Load the exported bundle
bundle = joblib.load("{slug}_bundle.pkl")
preprocessor = bundle["preprocessor"]
model         = bundle["model"]

# New raw data (same columns as training CSV, minus the target)
new_data = pd.read_csv("new_applications.csv")

# Apply the SAME preprocessing used during training
X_new = preprocessor.transform(new_data)

# Predict
predictions   = model.predict(X_new)
probabilities = model.predict_proba(X_new)

print(predictions)    # e.g., [1, 0, 1, 1, 0]
print(probabilities)  # e.g., [[0.08, 0.92], ...]
""",
        language="python",
    )

    with st.container(border=True):
        st.markdown("**Production checklist**")
        st.markdown(
            "- [ ] Validate that new data has the same columns as your training CSV\n"
            "- [ ] Apply `preprocessor.transform()` — never `fit_transform()` on new data\n"
            "- [ ] Monitor prediction distributions over time for data drift\n"
            "- [ ] Version artifacts alongside training code (DVC, MLflow, or git-lfs)\n"
            "- [ ] For production DL, consider PyTorch/TF + ONNX export for performance"
        )


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _serialise_joblib(obj) -> bytes:
    buffer = io.BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)
    return buffer.read()


def _serialise_metrics(train_result: DLTrainResult, eval_result: EvaluationResult) -> bytes:
    payload = {
        "model_name": train_result.model_name,
        "hyperparams": {
            k: list(v) if isinstance(v, tuple) else v
            for k, v in train_result.hyperparams.items()
        },
        "training_time_seconds": train_result.training_time_seconds,
        "n_iter": train_result.n_iter,
        "train_accuracy": round(train_result.train_accuracy, 6),
        "test_accuracy": round(train_result.test_accuracy, 6),
        "precision_weighted": round(eval_result.precision, 6),
        "recall_weighted": round(eval_result.recall, 6),
        "f1_weighted": round(eval_result.f1, 6),
        "roc_auc": round(eval_result.roc_auc, 6) if eval_result.roc_auc is not None else None,
        "class_labels": [str(l) for l in eval_result.class_labels],
        "classification_report": _sanitise_report(eval_result.classification_report),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, indent=2).encode("utf-8")


def _sanitise_report(report: dict) -> dict:
    return {
        label: (
            {k: float(v) if isinstance(v, float) else int(v) for k, v in metrics.items()}
            if isinstance(metrics, dict) else float(metrics)
        )
        for label, metrics in report.items()
    }


def _filename_slug(model_name: str) -> str:
    return model_name.lower().replace(" ", "_").replace("·", "").replace("(", "").replace(")", "").replace("→", "").strip("_").replace("__", "_")
