"""
Reusable API reference panel for Loan ML pages.

Each page calls render_api_reference("<step>") at the bottom of its render()
function. This renders a collapsed expander showing the matching REST endpoint,
a curl example, and the expected request / response shape — so users can see
exactly how to consume the same functionality programmatically.
"""

import streamlit as st

_BASE = "http://localhost:8000"

# ─── Per-step content ─────────────────────────────────────────────────────────

_STEPS: dict[str, dict] = {
    "upload": {
        "title": "POST /api/loan-ml/upload",
        "description": (
            "Upload a CSV file and receive a `session_id`. "
            "Pass this `session_id` to every subsequent endpoint."
        ),
        "curl": f"""\
curl -X POST {_BASE}/api/loan-ml/upload \\
  -F "file=@your_dataset.csv"\
""",
        "request": None,
        "response": """\
{
  "session_id": "3f2a1b4c-...",
  "rows": 1000,
  "columns": 12,
  "filename": "loan_data.csv"
}\
""",
    },

    "explore": {
        "title": "GET /api/loan-ml/{session_id}/explore",
        "description": (
            "Returns the dataset profile — shape, missing values, column types, "
            "and the auto-detected target column."
        ),
        "curl": f"""\
SESSION_ID="3f2a1b4c-..."

curl {_BASE}/api/loan-ml/$SESSION_ID/explore\
""",
        "request": None,
        "response": """\
{
  "rows": 1000,
  "columns": 12,
  "missing_values": 23,
  "duplicate_rows": 5,
  "numeric_columns": ["Age", "Income", "LoanAmount", "CreditScore"],
  "categorical_columns": ["EmploymentStatus", "Education"],
  "detected_target": "LoanApproved",
  "missing_summary": [
    {"Column": "Income", "Missing Values": 15, "Missing (%)": 1.5},
    ...
  ]
}\
""",
    },

    "preprocess": {
        "title": "POST /api/loan-ml/{session_id}/preprocess",
        "description": (
            "Configures and fits the preprocessing pipeline on the train split only "
            "(no data leakage). Returns train/test sizes and post-encoding feature names."
        ),
        "curl": f"""\
SESSION_ID="3f2a1b4c-..."

curl -X POST {_BASE}/api/loan-ml/$SESSION_ID/preprocess \\
  -H "Content-Type: application/json" \\
  -d '{{
    "target_column": "LoanApproved",
    "numeric_impute_strategy": "median",
    "categorical_impute_strategy": "most_frequent",
    "scaling_strategy": "standard",
    "encoding_strategy": "ordinal",
    "test_size": 0.2,
    "random_state": 42,
    "drop_columns": []
  }}'\
""",
        "request": """\
{
  "target_column": "LoanApproved",        // required
  "numeric_impute_strategy": "median",    // mean | median | most_frequent | constant
  "categorical_impute_strategy": "most_frequent",
  "scaling_strategy": "standard",         // standard | minmax | none
  "encoding_strategy": "ordinal",         // ordinal | onehot
  "test_size": 0.2,
  "random_state": 42,
  "drop_columns": []
}\
""",
        "response": """\
{
  "train_rows": 800,
  "test_rows": 200,
  "feature_count": 11,
  "feature_names": ["Age", "Income", "CreditScore", "EmploymentStatus", ...],
  "class_labels": ["0", "1"]
}\
""",
    },

    "train": {
        "title": "POST /api/loan-ml/{session_id}/train",
        "description": (
            "Trains a classification model on the preprocessed data. "
            "Supported models: `Logistic Regression`, `Decision Tree`, "
            "`Random Forest`, `XGBoost`."
        ),
        "curl": f"""\
SESSION_ID="3f2a1b4c-..."

curl -X POST {_BASE}/api/loan-ml/$SESSION_ID/train \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model_name": "Random Forest",
    "hyperparams": {{
      "n_estimators": 100,
      "max_depth": 10,
      "min_samples_split": 5
    }}
  }}'\
""",
        "request": """\
{
  "model_name": "Random Forest",   // Logistic Regression | Decision Tree | Random Forest | XGBoost
  "hyperparams": {}                // omit to use defaults (see GET /api/loan-ml/models)
}\
""",
        "response": """\
{
  "model_name": "Random Forest",
  "train_accuracy": 0.9475,
  "test_accuracy": 0.9150,
  "training_time_seconds": 1.23,
  "hyperparams": {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5
  }
}\
""",
    },

    "evaluate": {
        "title": "GET /api/loan-ml/{session_id}/evaluate  ·  POST /api/loan-ml/{session_id}/predict",
        "description": (
            "**Evaluate** returns full metrics for the trained model. "
            "**Predict** runs the pipeline on raw input features and returns "
            "the predicted class and per-class probabilities."
        ),
        "curl": f"""\
SESSION_ID="3f2a1b4c-..."

# ── Evaluate ──────────────────────────────────────────────────────
curl {_BASE}/api/loan-ml/$SESSION_ID/evaluate

# ── Predict (raw, unscaled feature values) ────────────────────────
curl -X POST {_BASE}/api/loan-ml/$SESSION_ID/predict \\
  -H "Content-Type: application/json" \\
  -d '{{
    "features": {{
      "Age": 35,
      "Income": 60000,
      "CreditScore": 720,
      "LoanAmount": 150000,
      "EmploymentStatus": "Employed",
      "Education": "Bachelor"
    }}
  }}'\
""",
        "request": """\
// Predict request — provide raw (unscaled) values for every feature column
{
  "features": {
    "Age": 35,
    "Income": 60000,
    "CreditScore": 720,
    "LoanAmount": 150000,
    "EmploymentStatus": "Employed"
  }
}\
""",
        "response": """\
// Evaluate response
{
  "accuracy": 0.9150,
  "precision": 0.9132,
  "recall": 0.9150,
  "f1": 0.9138,
  "roc_auc": 0.9612,
  "confusion_matrix": [[172, 12], [5, 11]],
  "class_labels": ["0", "1"],
  "classification_report": { ... }
}

// Predict response
{
  "prediction": "1",
  "probabilities": {"0": 0.0821, "1": 0.9179}
}\
""",
    },

    "download": {
        "title": "GET /api/loan-ml/{session_id}/download/model  ·  GET /api/loan-ml/{session_id}/download/bundle",
        "description": (
            "**Model** returns the trained model as a `.pkl` (joblib). "
            "**Bundle** returns model + fitted preprocessing pipeline together — "
            "load the bundle to make predictions in any Python environment."
        ),
        "curl": f"""\
SESSION_ID="3f2a1b4c-..."

# Download trained model only
curl -OJ {_BASE}/api/loan-ml/$SESSION_ID/download/model

# Download bundle (model + preprocessing pipeline)
curl -OJ {_BASE}/api/loan-ml/$SESSION_ID/download/bundle\
""",
        "request": None,
        "response": """\
# Load and use the bundle in any Python script
import joblib

bundle = joblib.load("loan_ml_bundle.pkl")

# bundle keys:
#   model          — fitted sklearn estimator
#   pipeline       — fitted preprocessing pipeline
#   feature_names  — post-encoding column names
#   original_features — pre-encoding column names (pipeline input)
#   class_labels   — target classes
#   model_name     — e.g. "Random Forest"

import pandas as pd
raw = pd.DataFrame([{"Age": 35, "Income": 60000, ...}])
transformed = bundle["pipeline"].transform(raw)
prediction  = bundle["model"].predict(transformed)\
""",
    },
}


# ─── Public entry point ───────────────────────────────────────────────────────

def render_api_reference(step: str) -> None:
    """
    Render a collapsed expander at the bottom of the page showing
    the REST API equivalent of the current UI step.

    Args:
        step: one of 'upload', 'explore', 'preprocess', 'train', 'evaluate', 'download'
    """
    content = _STEPS.get(step)
    if content is None:
        return

    st.divider()
    with st.expander("🔌 API Reference — use this step programmatically", expanded=False):
        st.caption(
            "The same functionality is available as a REST endpoint. "
            "Start the API server with `python run_api.py`, then hit "
            f"`{_BASE}/docs` for interactive Swagger UI."
        )

        st.markdown(f"#### `{content['title']}`")
        st.write(content["description"])

        st.markdown("**cURL**")
        st.code(content["curl"], language="bash")

        if content["request"]:
            st.markdown("**Request body**")
            st.code(content["request"], language="json")

        label = "Response / Usage" if step == "download" else "Example response"
        st.markdown(f"**{label}**")
        st.code(content["response"], language="json" if step != "download" else "python")
