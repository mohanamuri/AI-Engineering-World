"""Model export page for the HR Analytics ML pipeline."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from applications.hr_ml.constants import (
    EVAL_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_ml.services.metrics import EvaluationResult
from applications.hr_ml.services.preprocessor import PreprocessResult
from applications.hr_ml.services.trainer import TrainResult

_TRAIN_PAGE_LABEL = "🤖 Train Model"


def render() -> None:
    st.header("⬇ Download Model")
    st.caption(
        "Export the trained attrition model, fitted preprocessor, and evaluation metrics. "
        "Ship the preprocessor together with the model — never one without the other."
    )

    train_result: TrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result: PreprocessResult | None = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    eval_result: EvaluationResult | None = st.session_state.get(EVAL_RESULT_SESSION_KEY)

    if not isinstance(train_result, TrainResult):
        st.warning("Train a model first.")
        st.button("← Go to Train Model", type="primary",
                  on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE_LABEL}))
        return

    _render_summary(train_result, preprocess_result, eval_result)
    st.divider()
    _render_downloads(train_result, preprocess_result, eval_result)
    st.divider()
    _render_usage_snippet(train_result)


def _render_summary(train_result, preprocess_result, eval_result) -> None:
    st.subheader("Pipeline summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model", train_result.model_name)
    m2.metric("Features", str(len(train_result.feature_names)))
    m3.metric("Test accuracy", f"{train_result.test_accuracy:.1%}")
    m4.metric("ROC AUC", f"{eval_result.roc_auc:.3f}" if eval_result and eval_result.roc_auc else "—")

    if preprocess_result:
        config = preprocess_result.config
        with st.container(border=True):
            st.markdown("**Preprocessing config**")
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"Target: `{config.target_column}`")
            c2.markdown(f"Scaling: `{config.scaling_strategy}`")
            c3.markdown(f"Encoding: `{config.encoding_strategy}`")
            c4.markdown(f"Dropped: `{list(config.drop_columns)}`")


def _render_downloads(train_result, preprocess_result, eval_result) -> None:
    st.subheader("Artifacts")
    slug = _slug(train_result.model_name)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### Trained model")
            st.caption(f"`{slug}_model.pkl` — joblib-serialised sklearn estimator.")
            st.download_button("Download model (.pkl)", data=_joblib_bytes(train_result.model),
                               file_name=f"{slug}_model.pkl", mime="application/octet-stream",
                               use_container_width=True, key="dl_hr_model")

    with col2:
        with st.container(border=True):
            st.markdown("#### Preprocessing pipeline")
            st.caption(f"`{slug}_preprocessor.pkl` — fitted sklearn Pipeline.")
            if preprocess_result:
                st.download_button("Download preprocessor (.pkl)", data=_joblib_bytes(preprocess_result.pipeline),
                                   file_name=f"{slug}_preprocessor.pkl", mime="application/octet-stream",
                                   use_container_width=True, key="dl_hr_preprocessor")
            else:
                st.info("Preprocessor not available.")

    col3, col4 = st.columns(2)
    with col3:
        with st.container(border=True):
            st.markdown("#### Evaluation metrics")
            st.caption(f"`{slug}_metrics.json`")
            if eval_result:
                st.download_button("Download metrics (.json)", data=_metrics_bytes(train_result, eval_result),
                                   file_name=f"{slug}_metrics.json", mime="application/json",
                                   use_container_width=True, key="dl_hr_metrics")
            else:
                st.info("Run evaluation first.")

    with col4:
        with st.container(border=True):
            st.markdown("#### Feature importance")
            st.caption(f"`{slug}_feature_importance.csv`")
            fi_bytes = _feature_importance_bytes(train_result)
            if fi_bytes:
                st.download_button("Download importance (.csv)", data=fi_bytes,
                                   file_name=f"{slug}_feature_importance.csv", mime="text/csv",
                                   use_container_width=True, key="dl_hr_importance")
            else:
                st.info("Not available for this model type.")

    st.markdown("#### Combined bundle")
    with st.container(border=True):
        st.caption(f"`{slug}_bundle.pkl` — model + preprocessor + config. Recommended for deployment.")
        if preprocess_result:
            bundle = {
                "model": train_result.model,
                "preprocessor": preprocess_result.pipeline,
                "model_name": train_result.model_name,
                "feature_names": train_result.feature_names,
                "hyperparams": train_result.hyperparams,
                "config": preprocess_result.config,
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            st.download_button("Download bundle (.pkl)", data=_joblib_bytes(bundle),
                               file_name=f"{slug}_bundle.pkl", mime="application/octet-stream",
                               use_container_width=True, key="dl_hr_bundle")
        else:
            st.info("Preprocessor required for bundle export.")


def _render_usage_snippet(train_result) -> None:
    st.subheader("How to use these artifacts")
    slug = _slug(train_result.model_name)
    st.code(
        f"""import joblib
import pandas as pd

# Load the exported bundle
bundle = joblib.load("{slug}_bundle.pkl")
preprocessor = bundle["preprocessor"]
model         = bundle["model"]

# New employee data (same columns as training CSV, minus Attrition)
new_data = pd.read_csv("new_employees.csv")

# Apply the SAME preprocessing used during training
X_new = preprocessor.transform(new_data)

# Predict attrition risk
predictions  = model.predict(X_new)       # "Yes" / "No"
probabilities = model.predict_proba(X_new) # confidence scores

print(predictions)    # e.g., ["No", "Yes", "No"]
print(probabilities)  # e.g., [[0.88, 0.12], [0.15, 0.85], ...]
""",
        language="python",
    )
    with st.container(border=True):
        st.markdown("**Production checklist**")
        st.markdown(
            "- [ ] Validate new employee data has the same columns as the training CSV\n"
            "- [ ] Apply `preprocessor.transform()` — never `fit_transform()` on new data\n"
            "- [ ] Tune the classification threshold — lower threshold → catch more flight risks\n"
            "- [ ] Monitor prediction drift over time as workforce composition changes\n"
            "- [ ] Review flagged employees with HR managers before taking action"
        )


def _joblib_bytes(obj) -> bytes:
    buf = io.BytesIO()
    joblib.dump(obj, buf)
    buf.seek(0)
    return buf.read()


def _metrics_bytes(train_result, eval_result) -> bytes:
    payload = {
        "model_name": train_result.model_name,
        "hyperparams": train_result.hyperparams,
        "training_time_seconds": train_result.training_time_seconds,
        "train_accuracy": round(train_result.train_accuracy, 6),
        "test_accuracy": round(train_result.test_accuracy, 6),
        "precision_weighted": round(eval_result.precision, 6),
        "recall_weighted": round(eval_result.recall, 6),
        "f1_weighted": round(eval_result.f1, 6),
        "roc_auc": round(eval_result.roc_auc, 6) if eval_result.roc_auc else None,
        "class_labels": [str(l) for l in eval_result.class_labels],
        "classification_report": _sanitise(eval_result.classification_report),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, indent=2).encode()


def _feature_importance_bytes(train_result) -> bytes | None:
    model = train_result.model
    features = train_result.feature_names
    if hasattr(model, "feature_importances_"):
        imps = model.feature_importances_
    elif hasattr(model, "coef_"):
        coef = model.coef_
        imps = np.abs(coef[0] if coef.ndim > 1 else coef)
    else:
        return None
    df = (pd.DataFrame({"feature": features, "importance": imps})
          .sort_values("importance", ascending=False)
          .reset_index(drop=True))
    df.index += 1
    df.index.name = "rank"
    return df.to_csv().encode()


def _sanitise(report: dict) -> dict:
    return {
        label: (
            {k: float(v) if isinstance(v, float) else int(v) for k, v in metrics.items()}
            if isinstance(metrics, dict) else float(metrics)
        )
        for label, metrics in report.items()
    }


def _slug(model_name: str) -> str:
    return f"hr_{model_name.lower().replace(' ', '_')}"
