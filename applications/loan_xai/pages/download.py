"""Download page for the loan eligibility XAI pipeline.

Exports:
  - SHAP values as CSV (all test instances × features)
  - Global feature importance CSV (mean |SHAP| ranked)
  - LIME explanation for a selected instance as CSV
"""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import streamlit as st

from applications.loan_xai.constants import (
    EXPLAIN_RESULT_SESSION_KEY,
    NAVIGATION_SESSION_KEY,
    TRAIN_RESULT_SESSION_KEY,
)
from applications.loan_xai.services.explainer import ExplainResult, explain_instance_lime
from applications.loan_ml.services.trainer import TrainResult

_EXPLAIN_PAGE = "🔍 Explain"


def render() -> None:
    st.header("⬇ Download Explanations")
    st.caption("Export SHAP values, global importance, and per-instance LIME reports.")

    train_result: TrainResult | None = st.session_state.get(TRAIN_RESULT_SESSION_KEY)
    explain_result: ExplainResult | None = st.session_state.get(EXPLAIN_RESULT_SESSION_KEY)

    if not isinstance(explain_result, ExplainResult):
        with st.container(border=True):
            st.warning("No explanations computed yet.")
            st.write("Run the Explain page before downloading.")
            st.button("← Go to Explain", type="primary",
                      on_click=lambda: st.session_state.update({NAVIGATION_SESSION_KEY: _EXPLAIN_PAGE}))
        return

    _render_summary(explain_result)
    st.divider()
    _render_downloads(explain_result, train_result)
    st.divider()
    _render_usage_note(explain_result)


def _render_summary(result: ExplainResult) -> None:
    st.subheader("Explanation summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model", result.model_name)
    m2.metric("SHAP explainer", result.explainer_type)
    m3.metric("Instances explained", str(len(result.X_test_sample)))
    m4.metric("Features", str(len(result.feature_names)))


def _render_downloads(result: ExplainResult, train_result: TrainResult | None) -> None:
    st.subheader("Artifacts")

    slug = result.model_name.lower().replace(" ", "_").replace("/", "_")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("#### SHAP values (all instances)")
            st.caption(f"`{slug}_shap_values.csv` — one row per test instance, one column per feature.")
            shap_df = pd.DataFrame(result.shap_values, columns=result.feature_names)
            st.download_button(
                "Download SHAP values (.csv)",
                data=shap_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{slug}_shap_values.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_xai_shap",
            )

    with c2:
        with st.container(border=True):
            st.markdown("#### Global feature importance")
            st.caption(f"`{slug}_global_importance.csv` — mean |SHAP| per feature, ranked.")
            mean_shap = np.abs(result.shap_values).mean(axis=0)
            imp_df = (
                pd.DataFrame({"feature": result.feature_names, "mean_abs_shap": mean_shap})
                .sort_values("mean_abs_shap", ascending=False)
                .reset_index(drop=True)
            )
            imp_df.index += 1
            imp_df.index.name = "rank"
            st.download_button(
                "Download importance (.csv)",
                data=imp_df.to_csv().encode("utf-8"),
                file_name=f"{slug}_global_importance.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_xai_imp",
            )

    # LIME for selected instance
    if train_result is not None:
        st.markdown("#### LIME explanation — single instance")
        n = len(result.X_test_sample)
        row_idx = st.slider("Instance to export", 0, n - 1, 0, key="loan_xai_dl_lime_row")

        with st.container(border=True):
            st.caption(f"`{slug}_lime_instance_{row_idx}.csv` — feature conditions and weights.")
            try:
                contributions = explain_instance_lime(result, train_result.model, row_idx)
                lime_df = pd.DataFrame(contributions, columns=["feature_condition", "weight"])
                st.download_button(
                    f"Download LIME — instance {row_idx} (.csv)",
                    data=lime_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"{slug}_lime_instance_{row_idx}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_xai_lime",
                )
            except Exception as exc:
                st.error(f"Could not generate LIME export: {exc}")


def _render_usage_note(result: ExplainResult) -> None:
    st.subheader("How to use SHAP values in production")
    st.code(
        f"""import pandas as pd
import numpy as np

# Load SHAP values exported from this page
shap_df = pd.read_csv("{result.model_name.lower().replace(' ', '_')}_shap_values.csv")

# Top feature for each prediction
top_feature_idx = np.argmax(np.abs(shap_df.values), axis=1)
top_features = [shap_df.columns[i] for i in top_feature_idx]

# Explanation text for a single instance
instance_shap = shap_df.iloc[0]
ranked = instance_shap.abs().sort_values(ascending=False)

for feature, shap_val in instance_shap[ranked.index[:3]].items():
    direction = "increased" if shap_val > 0 else "decreased"
    print(f"{{feature}} {{direction}} probability by {{abs(shap_val):.4f}}")
""",
        language="python",
    )
