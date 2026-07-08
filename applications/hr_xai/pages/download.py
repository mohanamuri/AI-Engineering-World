"""Download page for HR XAI artifacts."""

from __future__ import annotations
import io
import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from applications.hr_xai.constants import (
    EVAL_RESULT_SESSION_KEY, EXPLAIN_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY, PREPROCESS_RESULT_SESSION_KEY, TRAIN_RESULT_SESSION_KEY,
)
from applications.hr_ml.services.metrics import evaluate
from applications.shared.api_reference import render_api_reference

_TRAIN_PAGE = "🤖 Train Model"


def render() -> None:
    st.header("⬇ Download")

    train_result = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    preprocess_result = st.session_state.get(PREPROCESS_RESULT_SESSION_KEY)

    if train_result is None:
        st.warning("Train a model first.")
        st.button("← Go to Train Model", type="primary",
                  on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _TRAIN_PAGE}))
        return

    # Compute eval if not cached
    eval_result = st.session_state.get(EVAL_RESULT_SESSION_KEY)
    if eval_result is None and preprocess_result is not None:
        eval_result = evaluate(train_result.model, preprocess_result.X_test, preprocess_result.y_test)
        st.session_state[EVAL_RESULT_SESSION_KEY] = eval_result

    slug = f"hr_xai_{train_result.model_name.lower().replace(' ', '_')}"

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### Trained model")
            st.download_button("Download model (.pkl)", data=_jb(train_result.model),
                               file_name=f"{slug}_model.pkl", mime="application/octet-stream",
                               use_container_width=True, key="dl_hr_xai_model")
    with col2:
        with st.container(border=True):
            st.markdown("#### Preprocessor")
            if preprocess_result:
                st.download_button("Download preprocessor (.pkl)", data=_jb(preprocess_result.pipeline),
                                   file_name=f"{slug}_preprocessor.pkl", mime="application/octet-stream",
                                   use_container_width=True, key="dl_hr_xai_prep")
            else:
                st.info("Preprocessor not available.")

    if preprocess_result:
        bundle = {"model": train_result.model, "preprocessor": preprocess_result.pipeline,
                  "model_name": train_result.model_name,
                  "exported_at": datetime.now(timezone.utc).isoformat()}
        st.download_button("Download bundle (.pkl)", data=_jb(bundle),
                           file_name=f"{slug}_bundle.pkl", mime="application/octet-stream",
                           use_container_width=True, key="dl_hr_xai_bundle")
    render_api_reference("hr_xai", "download")


def _jb(obj) -> bytes:
    buf = io.BytesIO()
    joblib.dump(obj, buf)
    buf.seek(0)
    return buf.read()
