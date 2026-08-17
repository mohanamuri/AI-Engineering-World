"""
Shared API reference panel for all AI Engineering World applications.

Usage in any page:
    from applications.shared.api_reference import render_api_reference
    render_api_reference("loan_dl", "train")

app_id:  loan_ml | loan_dl | loan_xai | loan_rag | loan_agent | loan_multi_agent
         hr_ml   | hr_dl   | hr_xai   | hr_rag   | hr_agent   | hr_multi_agent
step:    depends on the tier (see _STEPS_BY_TIER)
"""

import streamlit as st

_BASE = "https://ai-engineering-world.onrender.com"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _prefix(app_id: str) -> str:
    return f"/api/{app_id.replace('_', '-')}"


def _tier(app_id: str) -> str:
    if "multi_agent" in app_id:
        return "multi_agent"
    if "agent" in app_id:
        return "agent"
    if "rag" in app_id:
        return "rag"
    if "xai" in app_id:
        return "xai"
    if "_dl" in app_id:
        return "dl"
    return "ml"


def _domain(app_id: str) -> str:
    return "hr" if app_id.startswith("hr_") else "loan"


# ─── Domain-specific example payloads ─────────────────────────────────────────

_EX = {
    "loan": {
        "target": "LoanApproved",
        "features": (
            '{\n    "Age": 35,\n    "Income": 60000,\n    '
            '"CreditScore": 720,\n    "LoanAmount": 150000,\n    '
            '"EmploymentStatus": "Employed"\n  }'
        ),
        "prediction": '"prediction": "1",\n  "probabilities": {"0": 0.08, "1": 0.92}',
        "class_labels": '["0", "1"]',
        "application": (
            '{\n    "applicant_name": "Jane Smith",\n    "loan_amount": 250000,\n    '
            '"annual_income": 75000,\n    "credit_score": 720,\n    '
            '"employment_status": "Employed",\n    "loan_purpose": "Home"\n  }'
        ),
        "decision_field": "decision",
        "decision_values": "APPROVED | DECLINED | MANUAL_REVIEW",
        "decision_example": '"decision": "APPROVED"',
        "rag_question": "What credit score is required for loan approval?",
        "specialist_reports": (
            '"underwriter_report": "Income sufficient...",\n  '
            '"fraud_report": "No anomalies detected",\n  '
            '"compliance_report": "All requirements met"'
        ),
    },
    "hr": {
        "target": "Attrition",
        "features": (
            '{\n    "Age": 35,\n    "Department": "Sales",\n    '
            '"JobSatisfaction": 3,\n    "MonthlyIncome": 5000,\n    '
            '"YearsAtCompany": 3\n  }'
        ),
        "prediction": '"prediction": "Yes",\n  "probabilities": {"No": 0.32, "Yes": 0.68}',
        "class_labels": '["No", "Yes"]',
        "application": (
            '{\n    "employee_id": "EMP001",\n    "department": "Sales",\n    '
            '"age": 35,\n    "monthly_income": 5000,\n    '
            '"job_satisfaction": 3,\n    "years_at_company": 3,\n    "overtime": "Yes"\n  }'
        ),
        "decision_field": "risk_level",
        "decision_values": "HIGH | MEDIUM | LOW",
        "decision_example": '"risk_level": "HIGH",\n  "risk_score": 0.78',
        "rag_question": "What are the retention policies for high-risk employees?",
        "specialist_reports": (
            '"hr_manager_report": "Low engagement detected...",\n  '
            '"perf_evaluator_report": "Below average performance",\n  '
            '"risk_assessor_report": "High flight risk"'
        ),
    },
}


# ─── Content generators per step ──────────────────────────────────────────────

def _upload(p: str, ex: dict) -> dict:
    return {
        "title": f"POST {p}/upload",
        "description": "Upload a CSV file and receive a `session_id`. Pass this to every subsequent endpoint.",
        "curl": f'curl -X POST {_BASE}{p}/upload \\\n  -F "file=@your_dataset.csv"',
        "request": None,
        "response": '{\n  "session_id": "3f2a1b4c-...",\n  "rows": 1000,\n  "columns": 12,\n  "filename": "data.csv"\n}',
    }


def _explore(p: str, ex: dict) -> dict:
    return {
        "title": f"GET {p}/{{session_id}}/explore",
        "description": "Returns dataset profile — shape, missing values, column types, auto-detected target column.",
        "curl": f'SESSION_ID="3f2a1b4c-..."\n\ncurl {_BASE}{p}/$SESSION_ID/explore',
        "request": None,
        "response": (
            '{\n  "rows": 1000,\n  "columns": 15,\n  "missing_values": 23,\n  '
            f'"detected_target": "{ex["target"]}",\n  '
            '"numeric_columns": [...],\n  "categorical_columns": [...]\n}'
        ),
    }


def _preprocess(p: str, ex: dict) -> dict:
    return {
        "title": f"POST {p}/{{session_id}}/preprocess",
        "description": "Fits the preprocessing pipeline on the train split only (no data leakage).",
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/preprocess \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{\n    "target_column": "{ex["target"]}",\n    '
            f'"scaling_strategy": "standard",\n    "test_size": 0.2\n  }}\''
        ),
        "request": (
            '{\n  "target_column": "' + ex["target"] + '",     // required\n'
            '  "numeric_impute_strategy": "median",\n'
            '  "scaling_strategy": "standard",       // standard | minmax | none\n'
            '  "encoding_strategy": "ordinal",       // ordinal | onehot\n'
            '  "test_size": 0.2,\n'
            '  "drop_columns": []\n}'
        ),
        "response": (
            '{\n  "train_rows": 800,\n  "test_rows": 200,\n  '
            '"feature_count": 12,\n  "feature_names": [...],\n  '
            f'"class_labels": {ex["class_labels"]}\n}}'
        ),
    }


def _train_ml(p: str, ex: dict) -> dict:
    return {
        "title": f"POST {p}/{{session_id}}/train",
        "description": (
            "Train a classifier. Supported: `Logistic Regression`, `Decision Tree`, "
            "`Random Forest`, `XGBoost`. See `GET {p}/models` for hyperparameter defaults."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/train \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{"model_name": "Random Forest", "hyperparams": {{}}}}\''
        ),
        "request": (
            '{\n  "model_name": "Random Forest",   '
            '// Logistic Regression | Decision Tree | Random Forest | XGBoost\n'
            '  "hyperparams": {}                   // omit to use defaults\n}'
        ),
        "response": (
            '{\n  "model_name": "Random Forest",\n  "train_accuracy": 0.9475,\n  '
            '"test_accuracy": 0.9150,\n  "training_time_seconds": 1.23,\n  '
            '"hyperparams": {"n_estimators": 100, "max_depth": 10}\n}'
        ),
    }


def _train_dl(p: str, ex: dict) -> dict:
    return {
        "title": f"POST {p}/{{session_id}}/train",
        "description": (
            "Train an MLP neural network (sklearn MLPClassifier). "
            "Choose from preset architectures or set layer sizes manually."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/train \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{\n    "architecture_name": "Medium [128,64]",\n    '
            f'"activation": "relu",\n    "solver": "adam",\n    '
            f'"learning_rate_init": 0.001,\n    "max_iter": 200,\n    "alpha": 0.0001\n  }}\''
        ),
        "request": (
            '{\n  "architecture_name": "Medium [128,64]",  '
            '// Small [64] | Medium [128,64] | Large [256,128,64]\n'
            '  "activation": "relu",                       // relu | tanh | logistic\n'
            '  "solver": "adam",                           // adam | sgd | lbfgs\n'
            '  "learning_rate_init": 0.001,\n'
            '  "max_iter": 200,\n'
            '  "alpha": 0.0001                             // L2 regularisation\n}'
        ),
        "response": (
            '{\n  "architecture_name": "Medium [128,64]",\n  "train_accuracy": 0.9612,\n  '
            '"test_accuracy": 0.9250,\n  "training_time_seconds": 4.87,\n  '
            '"n_iter": 147,\n  "loss_curve": [0.689, 0.531, 0.412, ...]\n}'
        ),
    }


def _evaluate(p: str, ex: dict) -> dict:
    return {
        "title": f"GET {p}/{{session_id}}/evaluate  ·  POST {p}/{{session_id}}/predict",
        "description": (
            "**Evaluate** returns full metrics. "
            "**Predict** takes raw feature values and returns the prediction + probabilities."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'# Evaluate\ncurl {_BASE}{p}/$SESSION_ID/evaluate\n\n'
            f'# Predict\ncurl -X POST {_BASE}{p}/$SESSION_ID/predict \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{"features": {ex["features"]}}}\''
        ),
        "request": f'{{\n  "features": {ex["features"]}\n}}',
        "response": (
            '// Evaluate\n{\n  "accuracy": 0.9150,  "precision": 0.9132,\n  '
            '"recall": 0.9150,  "f1": 0.9138,  "roc_auc": 0.9612,\n  '
            '"confusion_matrix": [[172, 12], [5, 11]]\n}\n\n'
            f'// Predict\n{{\n  {ex["prediction"]}\n}}'
        ),
    }


def _explain(p: str, ex: dict) -> dict:
    return {
        "title": f"POST {p}/{{session_id}}/explain",
        "description": (
            "Compute SHAP global importance and LIME local explanation for a specific test instance. "
            "Requires train to have been run first."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/explain \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{"instance_index": 0, "num_features": 10}}\''
        ),
        "request": (
            '{\n  "instance_index": 0,    // index into test set (0-based)\n'
            '  "num_features": 10        // top-N features to return in LIME explanation\n}'
        ),
        "response": (
            '{\n  "explainer_type": "TreeExplainer",\n'
            '  "shap_feature_importance": [\n'
            '    {"feature": "CreditScore", "mean_abs_shap": 0.142}, ...\n  ],\n'
            '  "lime_explanation": [\n'
            '    {"feature": "CreditScore <= 680", "weight": -0.38}, ...\n  ],\n'
            '  "predicted_class": "1",\n'
            '  "shap_base_value": 0.62\n}'
        ),
    }


def _configure(p: str, ex: dict) -> dict:
    return {
        "title": f"POST {p}/{{session_id}}/configure",
        "description": (
            "Build the ChromaDB vector store from uploaded documents. "
            "Sets the RAG configuration (chunk size, top-k, temperature, model)."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/configure \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{"chunk_size": 512, "top_k": 4, "temperature": 0.0}}\''
        ),
        "request": (
            '{\n  "chunk_size": 512,\n  "top_k": 4,\n'
            '  "temperature": 0.0,\n'
            '  "llm_model": "meta-llama/llama-4-scout-17b-16e-instruct"  // Groq model\n}'
        ),
        "response": (
            '{\n  "chunks_indexed": 48,\n  "embedding_model": "all-MiniLM-L6-v2",\n'
            '  "chunk_size": 512,\n  "top_k": 4\n}'
        ),
    }


def _chat(p: str, ex: dict) -> dict:
    return {
        "title": f"POST {p}/{{session_id}}/chat",
        "description": (
            "Ask a question against the indexed documents. "
            "Retrieves top-k chunks, sends context to Groq LLM, returns grounded answer."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/chat \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{"question": "{ex["rag_question"]}"}}\''
        ),
        "request": f'{{\n  "question": "{ex["rag_question"]}"\n}}',
        "response": (
            '{\n  "question": "...",\n  "answer": "Based on the policy documents...",\n'
            '  "source_chunks": ["Chunk 1 text...", "Chunk 2 text..."],\n'
            '  "timestamp": "2026-07-08T10:30:00Z"\n}'
        ),
    }


def _history(p: str, ex: dict) -> dict:
    return {
        "title": f"GET {p}/{{session_id}}/history",
        "description": "Returns the full conversation or run history for the session.",
        "curl": f'SESSION_ID="3f2a1b4c-..."\n\ncurl {_BASE}{p}/$SESSION_ID/history',
        "request": None,
        "response": (
            '[\n  {\n    "question": "...",\n    "answer": "...",\n'
            '    "timestamp": "2026-07-08T10:30:00Z"\n  },\n  ...\n]'
        ),
    }


def _application(p: str, ex: dict) -> dict:
    domain_label = "employee record" if ex.get("decision_field") == "risk_level" else "loan application"
    return {
        "title": f"POST {p}/{{session_id}}/run  (submit {domain_label})",
        "description": (
            f"Submit the {domain_label} for analysis. "
            "The agent runs deterministic tools then synthesises a final recommendation via Groq LLM."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/run \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{"application": {ex["application"]}}}\''
        ),
        "request": f'{{\n  "application": {ex["application"]}\n}}',
        "response": (
            '{\n  "steps": [\n    {"tool": "validate", "result": "..."},\n'
            '    {"tool": "compute_risk", "result": "..."},\n'
            '    {"tool": "lookup_policy", "result": "..."}\n  ],\n'
            f'  "final_answer": "Based on analysis...",\n'
            f'  {ex["decision_example"]},\n'
            '  "timestamp": "2026-07-08T10:30:00Z"\n}'
        ),
    }


def _run(p: str, ex: dict) -> dict:
    return _application(p, ex)


def _panel(p: str, ex: dict) -> dict:
    domain_label = "employee record" if ex.get("decision_field") == "risk_level" else "loan application"
    return {
        "title": f"POST {p}/{{session_id}}/panel",
        "description": (
            f"Submit to the multi-agent panel. Three specialist agents analyse in parallel, "
            "then the supervisor synthesises a final decision."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -X POST {_BASE}{p}/$SESSION_ID/panel \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f'  -d \'{{"application": {ex["application"]}}}\''
        ),
        "request": f'{{\n  "application": {ex["application"]}\n}}',
        "response": (
            '{\n  ' + ex["specialist_reports"] + ',\n'
            '  "final_answer": "Panel consensus...",\n'
            f'  {ex["decision_example"]},\n'
            '  "timestamp": "2026-07-08T10:30:00Z"\n}'
        ),
    }


def _download(p: str, ex: dict) -> dict:
    return {
        "title": f"GET {p}/{{session_id}}/download/model  ·  GET {p}/{{session_id}}/download/bundle",
        "description": (
            "**model** — trained model `.pkl`. "
            "**bundle** — model + preprocessing pipeline together (recommended for inference)."
        ),
        "curl": (
            f'SESSION_ID="3f2a1b4c-..."\n\n'
            f'curl -OJ {_BASE}{p}/$SESSION_ID/download/model\n'
            f'curl -OJ {_BASE}{p}/$SESSION_ID/download/bundle'
        ),
        "request": None,
        "response": (
            '# Load bundle in any Python environment\n'
            'import joblib, pandas as pd\n\n'
            'bundle = joblib.load("bundle.pkl")\n'
            '# keys: model, pipeline, feature_names, class_labels\n\n'
            'raw = pd.DataFrame([{"Age": 35, ...}])\n'
            'transformed = bundle["pipeline"].transform(raw)\n'
            'pred = bundle["model"].predict(transformed)'
        ),
    }


# ─── Step router per tier ─────────────────────────────────────────────────────

def _get_content(app_id: str, step: str) -> dict | None:
    p = _prefix(app_id)
    t = _tier(app_id)
    ex = _EX[_domain(app_id)]

    generators = {
        # Common ML/DL/XAI steps
        "upload":     lambda: _upload(p, ex),
        "explore":    lambda: _explore(p, ex),
        "preprocess": lambda: _preprocess(p, ex),
        "train":      lambda: _train_dl(p, ex) if t == "dl" else _train_ml(p, ex),
        "evaluate":   lambda: _evaluate(p, ex),
        "download":   lambda: _download(p, ex),
        # XAI-specific
        "explain":    lambda: _explain(p, ex),
        # RAG-specific
        "configure":  lambda: _configure(p, ex),
        "chat":       lambda: _chat(p, ex),
        "history":    lambda: _history(p, ex),
        # Agent-specific
        "application": lambda: _application(p, ex),
        "run":         lambda: _run(p, ex),
        "decision":    lambda: _run(p, ex),       # same content — decision is part of run response
        # Multi-agent-specific
        "panel":       lambda: _panel(p, ex),
        "consensus":   lambda: _panel(p, ex),     # same content — consensus is part of panel response
    }

    gen = generators.get(step)
    return gen() if gen else None


# ─── Public entry point ───────────────────────────────────────────────────────

def render_api_reference(app_id: str, step: str) -> None:
    """
    Render a collapsed API reference expander at the bottom of the page.

    Args:
        app_id: e.g. "loan_dl", "hr_ml", "loan_rag"
        step:   e.g. "upload", "train", "chat", "run", "panel"
    """
    content = _get_content(app_id, step)
    if content is None:
        return

    p = _prefix(app_id)
    is_download = step == "download"

    st.divider()
    with st.expander("🔌 API Reference — use this step programmatically", expanded=False):
        st.caption(
            f"Live API: [`{_BASE}/docs`]({_BASE}/docs) — "
            "interactive Swagger UI with all endpoints."
        )
        st.markdown(f"#### `{content['title']}`")
        st.write(content["description"])

        st.markdown("**cURL**")
        st.code(content["curl"], language="bash")

        if content["request"]:
            st.markdown("**Request body**")
            st.code(content["request"], language="json")

        label = "Response / Usage" if is_download else "Example response"
        st.markdown(f"**{label}**")
        lang = "python" if is_download else "json"
        st.code(content["response"], language=lang)
