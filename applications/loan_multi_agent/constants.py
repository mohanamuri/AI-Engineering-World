"""Shared constants for the loan eligibility Multi-Agent System application."""

NAVIGATION_SESSION_KEY = "loan_mas_navigation"
APPLICATION_PAGE_LABEL = "📋 Application"

# Session keys
APPLICATION_SESSION_KEY = "loan_mas_application"       # dict — current application
PANEL_RESULT_SESSION_KEY = "loan_mas_panel_result"     # PanelRunResult — latest run
HISTORY_SESSION_KEY = "loan_mas_history"               # list[PanelRunResult]
AGENT_CONFIG_SESSION_KEY = "loan_mas_config"           # AgentConfig
