"""Model export page for the loan eligibility ML pipeline.

Provides in-memory downloads for all pipeline artifacts:
  - Trained model (.pkl via joblib)
  - Fitted preprocessor pipeline (.pkl via joblib)
  - Evaluation metrics (.json)
  - Feature importance (.csv)

Interview note — Why joblib over pickle?
-----------------------------------------
Both serialize Python objects, but joblib is optimised for large numpy
arrays (used inside sklearn estimators). It uses memory-mapped files
internally, making serialization of large forests ~3-5x faster than
pickle and producing smaller files due to numpy-aware compression.

Interview note — No disk writes
---------------------------------
Streamlit Community Cloud runs on a read-only filesystem. All artifacts
are built in io.BytesIO buffers (in-memory) and handed directly to
st.download_button. This is also safer — no temp files to clean up and
no risk of one user's artifacts overwriting another's.

Interview note — Packaging model + preprocessor together
----------------------------------------------------------
In production, you never ship the model alone. The preprocessor was fit
on the training data and must be applied identically at inference time.
Shipping them separately creates a coordination risk — a future engineer
might update one without the other.

Best practice: store them together in a dict or a versioned artifact store
(MLflow, DVC). Here we offer both separately AND as a combined bundle.
"""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import joblib
import pandas as pd
import streamlit as st

from applications.loan_ml.constants import (
    EVAL_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_ml.services.metrics import EvaluationResult
from applications.loan_ml.services.preprocessor import PreprocessResult
from applications.loan_ml.services.trainer import TrainResult
from applications.loan_ml.utils.api_reference import render_api_reference

_TRAIN_PAGE_LABEL = "🤖 Train Model"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    st.header("⬇ Download Model")
    st.caption(
        "Export all pipeline artifacts. Package the model and preprocessor "
        "together to guarantee identical transforms at inference time."
    )

    train_result: TrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    eval_result: EvaluationResult | None = st.session_state.get(EVAL_RESULT_SESSION_KEY)

    if not isinstance(train_result, TrainResult):
        _render_empty_state()
        return

    _render_artifact_summary(train_result, preprocess_result, eval_result)
    st.divider()
    _render_downloads(train_result, preprocess_result, eval_result)
    st.divider()
    _render_usage_snippet(train_result)
    render_api_reference("download")


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

def _render_empty_state() -> None:
    with st.container(border=True):
        st.warning("No trained model found.")
        st.write("Train and evaluate a model before downloading artifacts.")
        st.button(
            "← Go to Train Model",
            type="primary",
            on_click=lambda: st.session_state.update(
                {NAVIGATION_SESSION_KEY: _TRAIN_PAGE_LABEL}
            ),
        )


# ---------------------------------------------------------------------------
# Artifact summary
# ---------------------------------------------------------------------------

def _render_artifact_summary(
    train_result: TrainResult,
    preprocess_result: PreprocessResult | None,
    eval_result: EvaluationResult | None,
) -> None:
    st.subheader("Pipeline summary")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model", train_result.model_name)
    m2.metric("Features", str(len(train_result.feature_names)))
    m3.metric(
        "Test accuracy",
        f"{train_result.test_accuracy:.1%}",
    )
    m4.metric(
        "ROC AUC",
        f"{eval_result.roc_auc:.3f}" if eval_result and eval_result.roc_auc else "—",
    )

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
    train_result: TrainResult,
    preprocess_result: PreprocessResult | None,
    eval_result: EvaluationResult | None,
) -> None:
    st.subheader("Artifacts")

    slug = _filename_slug(train_result.model_name)

    col1, col2 = st.columns(2)

    # --- Model ---
    with col1:
        with st.container(border=True):
            st.markdown("#### Trained model")
            st.caption(
                f"`{slug}_model.pkl` · joblib-serialised sklearn estimator. "
                "Load with `joblib.load()` and call `.predict()`."
            )
            st.download_button(
                label="Download model (.pkl)",
                data=_serialise_joblib(train_result.model),
                file_name=f"{slug}_model.pkl",
                mime="application/octet-stream",
                use_container_width=True,
                key="dl_model",
            )

    # --- Preprocessor ---
    with col2:
        with st.container(border=True):
            st.markdown("#### Preprocessing pipeline")
            st.caption(
                f"`{slug}_preprocessor.pkl` · fitted sklearn Pipeline. "
                "Apply to new raw data before calling the model."
            )
            if preprocess_result is not None:
                st.download_button(
                    label="Download preprocessor (.pkl)",
                    data=_serialise_joblib(preprocess_result.pipeline),
                    file_name=f"{slug}_preprocessor.pkl",
                    mime="application/octet-stream",
                    use_container_width=True,
                    key="dl_preprocessor",
                )
            else:
                st.info("Preprocessor not available in session.")

    col3, col4 = st.columns(2)

    # --- Metrics JSON ---
    with col3:
        with st.container(border=True):
            st.markdown("#### Evaluation metrics")
            st.caption(
                f"`{slug}_metrics.json` · accuracy, precision, recall, F1, "
                "ROC AUC, and per-class report."
            )
            if eval_result is not None:
                st.download_button(
                    label="Download metrics (.json)",
                    data=_serialise_metrics(train_result, eval_result),
                    file_name=f"{slug}_metrics.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_metrics",
                )
            else:
                st.info("Run evaluation first to download metrics.")

    # --- Feature importance CSV ---
    with col4:
        with st.container(border=True):
            st.markdown("#### Feature importance")
            st.caption(
                f"`{slug}_feature_importance.csv` · ranked feature scores "
                "for model interpretability."
            )
            importance_bytes = _serialise_feature_importance(train_result)
            if importance_bytes is not None:
                st.download_button(
                    label="Download importance (.csv)",
                    data=importance_bytes,
                    file_name=f"{slug}_feature_importance.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_importance",
                )
            else:
                st.info("Feature importance not available for this model type.")

    # --- Combined bundle ---
    st.markdown("#### Combined bundle")
    with st.container(border=True):
        st.caption(
            f"`{slug}_bundle.pkl` · model + preprocessor + config in one file. "
            "Recommended for deployment: load once, apply pipeline then model."
        )
        if preprocess_result is not None:
            bundle = {
                "model": train_result.model,
                "preprocessor": preprocess_result.pipeline,
                "model_name": train_result.model_name,
                "feature_names": train_result.feature_names,
                "hyperparams": train_result.hyperparams,
                "config": preprocess_result.config,
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            st.download_button(
                label="Download bundle (.pkl)",
                data=_serialise_joblib(bundle),
                file_name=f"{slug}_bundle.pkl",
                mime="application/octet-stream",
                use_container_width=True,
                key="dl_bundle",
            )
        else:
            st.info("Preprocessor required for bundle export.")


# ---------------------------------------------------------------------------
# Usage snippet
# ---------------------------------------------------------------------------

def _render_usage_snippet(train_result: TrainResult) -> None:
    st.subheader("How to use these artifacts")

    model_name = train_result.model_name
    slug = _filename_slug(model_name)

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
predictions = model.predict(X_new)
probabilities = model.predict_proba(X_new)  # confidence scores

print(predictions)      # e.g., [1, 0, 1, 1, 0]
print(probabilities)    # e.g., [[0.12, 0.88], ...]
""",
        language="python",
    )

    with st.container(border=True):
        st.markdown("**Production checklist**")
        st.markdown(
            "- [ ] Validate that new data has the same columns as your training CSV\n"
            "- [ ] Apply `preprocessor.transform()` — never `fit_transform()` on new data\n"
            "- [ ] Monitor prediction distributions over time for data drift\n"
            "- [ ] Version your artifacts alongside your training code (DVC, MLflow, or git-lfs)\n"
            "- [ ] Set a probability threshold appropriate to your business cost of FP vs FN"
        )


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _serialise_joblib(obj) -> bytes:
    """Serialise any object to in-memory bytes using joblib."""
    buffer = io.BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)
    return buffer.read()


def _serialise_metrics(train_result: TrainResult, eval_result: EvaluationResult) -> bytes:
    """Build a clean metrics JSON without numpy types."""
    payload = {
        "model_name": train_result.model_name,
        "hyperparams": train_result.hyperparams,
        "training_time_seconds": train_result.training_time_seconds,
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


def _serialise_feature_importance(train_result: TrainResult) -> bytes | None:
    """Return ranked feature importance as CSV bytes, or None if unavailable."""
    import numpy as np

    model = train_result.model
    feature_names = train_result.feature_names

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        coef = model.coef_
        importances = np.abs(coef[0] if coef.ndim > 1 else coef)
    else:
        return None

    df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    df.index += 1  # 1-based rank
    df.index.name = "rank"
    return df.to_csv().encode("utf-8")


def _sanitise_report(report: dict) -> dict:
    """Convert numpy floats to Python floats for JSON serialisation."""
    return {
        label: (
            {k: float(v) if isinstance(v, float) else int(v) for k, v in metrics.items()}
            if isinstance(metrics, dict) else float(metrics)
        )
        for label, metrics in report.items()
    }


def _filename_slug(model_name: str) -> str:
    return model_name.lower().replace(" ", "_")
