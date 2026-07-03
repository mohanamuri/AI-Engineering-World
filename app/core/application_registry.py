"""
Application Runtime Registry

Maps application IDs to executable entry points.
"""

from applications.loan_ml.app import run as loan_ml
from applications.loan_dl.app import run as loan_dl
from applications.loan_xai.app import run as loan_xai
from applications.loan_rag.app import run as loan_rag
from applications.loan_agent.app import run_app as loan_agent
from applications.loan_multi_agent.app import run as loan_multi_agent

APPLICATION_RUNNERS = {
    "loan_ml": loan_ml,
    "loan_dl": loan_dl,
    "loan_xai": loan_xai,
    "loan_rag": loan_rag,
    "loan_agent": loan_agent,
    "loan_multi_agent": loan_multi_agent,
}