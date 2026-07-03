"""Shared constants for the loan eligibility application."""

NAVIGATION_SESSION_KEY = "loan_ml_navigation"
UPLOAD_PAGE_LABEL = "📤 Upload Dataset"

# Session state keys for downstream pipeline stages.
# Upload-stage keys live in services/data_loader.py (single source of truth).
PREPROCESS_RESULT_SESSION_KEY = "loan_ml_preprocess_result"
PREPROCESS_CONFIG_SESSION_KEY = "loan_ml_preprocess_config"

TRAIN_RESULT_SESSION_KEY = "loan_ml_train_result"

EVAL_RESULT_SESSION_KEY = "loan_ml_eval_result"

