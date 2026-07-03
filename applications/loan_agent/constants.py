"""Shared constants for the loan eligibility AI Agent application."""

NAVIGATION_SESSION_KEY = "loan_agent_navigation"
APPLICATION_PAGE_LABEL = "📋 Application"

# Session keys
APPLICATION_SESSION_KEY = "loan_agent_application"       # dict — current application form
RUN_RESULT_SESSION_KEY = "loan_agent_run_result"         # AgentRunResult — latest run
HISTORY_SESSION_KEY = "loan_agent_history"               # list[AgentRunResult]
AGENT_CONFIG_SESSION_KEY = "loan_agent_config"           # AgentConfig
