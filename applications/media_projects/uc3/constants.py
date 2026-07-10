"""Session-state constants for Media Projects — UC3: Image Intelligence."""

NAVIGATION_SESSION_KEY  = "media_uc3_nav"
UPLOAD_SESSION_KEY      = "media_uc3_upload"       # {"bytes": ..., "filename": ...}
ANALYSIS_SESSION_KEY    = "media_uc3_analysis"     # ImageAnalysis
QA_HISTORY_SESSION_KEY  = "media_uc3_qa_history"   # list[{"q": str, "a": str}]
CONFIG_SESSION_KEY      = "media_uc3_config"        # ImageConfig
