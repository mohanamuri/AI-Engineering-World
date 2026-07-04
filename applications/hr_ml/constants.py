"""Shared constants for the HR Analytics ML application."""

NAVIGATION_SESSION_KEY = "hr_ml_navigation"
UPLOAD_PAGE_LABEL = "📤 Upload Dataset"

# Session state keys
PREPROCESS_RESULT_SESSION_KEY = "hr_ml_preprocess_result"
PREPROCESS_CONFIG_SESSION_KEY = "hr_ml_preprocess_config"

TRAIN_RESULT_SESSION_KEY = "hr_ml_train_result"

EVAL_RESULT_SESSION_KEY = "hr_ml_eval_result"

# IBM HR dataset specifics
TARGET_COLUMN = "Attrition"
RECOMMENDED_DROP_COLUMNS = ("EmployeeCount", "Over18", "StandardHours", "EmployeeNumber")
