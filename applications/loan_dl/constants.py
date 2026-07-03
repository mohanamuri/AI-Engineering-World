"""Shared constants for the loan eligibility deep-learning application."""

NAVIGATION_SESSION_KEY = "loan_dl_navigation"
UPLOAD_PAGE_LABEL = "📤 Upload Dataset"

# Dataset session keys — separate from loan_ml so both apps can coexist.
DATAFRAME_SESSION_KEY = "loan_dl_dataframe"
DATASET_METADATA_SESSION_KEY = "loan_dl_dataset_metadata"
DATASET_FINGERPRINT_SESSION_KEY = "loan_dl_dataset_fingerprint"

# Pipeline stage session keys.
PREPROCESS_RESULT_SESSION_KEY = "loan_dl_preprocess_result"
PREPROCESS_CONFIG_SESSION_KEY = "loan_dl_preprocess_config"
TRAIN_RESULT_SESSION_KEY = "loan_dl_train_result"
EVAL_RESULT_SESSION_KEY = "loan_dl_eval_result"
