"""Shared constants for the loan eligibility explainability application."""

NAVIGATION_SESSION_KEY = "loan_xai_navigation"
UPLOAD_PAGE_LABEL = "📤 Upload Dataset"

# Dataset session keys — independent from loan_ml and loan_dl.
DATAFRAME_SESSION_KEY = "loan_xai_dataframe"
DATASET_METADATA_SESSION_KEY = "loan_xai_dataset_metadata"
DATASET_FINGERPRINT_SESSION_KEY = "loan_xai_dataset_fingerprint"

# Pipeline stage session keys.
PREPROCESS_RESULT_SESSION_KEY = "loan_xai_preprocess_result"
PREPROCESS_CONFIG_SESSION_KEY = "loan_xai_preprocess_config"
TRAIN_RESULT_SESSION_KEY = "loan_xai_train_result"
EXPLAIN_RESULT_SESSION_KEY = "loan_xai_explain_result"
