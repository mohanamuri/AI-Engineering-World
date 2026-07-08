"""Download page for HR Deep Learning artifacts."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from applications.hr_dl.constants import (
    EVAL_RESULT_SESSION_KEY, NAVIGATION_SESSION_KEY,
    PREPROCESS_RESULT_SESSION_KEY, TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_ml.services.metrics import EvaluationResult
from applications.shared.api_reference import render_api_reference

_TRAIN_PAGE_LABEL = "🧠 Train Neural Network"


def render() -> None:
    st.header("⬇ Download Model")

    train_result = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)
    eval_result = st.session_state.get(EVAL_RESULT_SESSION_KEY)

    if train_result is None:
        st.warning("Train a neural network first.")
        st.button("← Go to Train", type="primary",
                  on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE_LABEL}))
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model", train_result.model_name)
    m2.metric("Epochs", str(train_result.n_iter))
    m3.metric("Test accuracy", f"{train_result.test_accuracy:.1%}")
    m4.metric("ROC AUC", f"{eval_result.roc_auc:.3f}" if eval_result and eval_result.roc_auc else "—")

    st.divider()
    slug = f"hr_dl_{train_result.model_name.lower().replace(' ', '_').replace('·', '').replace('(', '').replace(')', '').replace('→', '')[:30]}"

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### Neural network model")
            st.download_button("Download model (.pkl)", data=_jbytes(train_result.model),
                               file_name=f"{slug}_model.pkl", mime="application/octet-stream",
                               use_container_width=True, key="dl_hr_dl_model")
    with col2:
        with st.container(border=True):
            st.markdown("#### Preprocessing pipeline")
            if preprocess_result:
                st.download_button("Download preprocessor (.pkl)", data=_jbytes(preprocess_result.pipeline),
                                   file_name=f"{slug}_preprocessor.pkl", mime="application/octet-stream",
                                   use_container_width=True, key="dl_hr_dl_prep")
            else:
                st.info("Preprocessor not available.")

    if preprocess_result:
        bundle = {"model": train_result.model, "preprocessor": preprocess_result.pipeline,
                  "model_name": train_result.model_name, "feature_names": train_result.feature_names,
                  "hyperparams": train_result.hyperparams, "loss_curve": train_result.loss_curve,
                  "exported_at": datetime.now(timezone.utc).isoformat()}
        st.download_button("Download bundle (.pkl)", data=_jbytes(bundle),
                           file_name=f"{slug}_bundle.pkl", mime="application/octet-stream",
                           use_container_width=True, key="dl_hr_dl_bundle")
    render_api_reference("hr_dl", "download")


def _jbytes(obj) -> bytes:
    buf = io.BytesIO()
    joblib.dump(obj, buf)
    buf.seek(0)
    return buf.read()
