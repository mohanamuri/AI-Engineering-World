"""Shared constants for Prompt Engineering — UC1: Zero-shot vs Few-shot."""

NAVIGATION_SESSION_KEY = "prompt_uc1_nav"

# PromptConfig stored between pages
CONFIG_SESSION_KEY = "prompt_uc1_config"

# Last run results: PromptResult
ZERO_SHOT_RESULT_KEY = "prompt_uc1_zero_shot"
FEW_SHOT_RESULT_KEY  = "prompt_uc1_few_shot"

# User's task input (persisted across pages)
TASK_SESSION_KEY = "prompt_uc1_task"
