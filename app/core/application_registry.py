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

from applications.hr_ml.app import run as hr_ml
from applications.hr_dl.app import run as hr_dl
from applications.hr_xai.app import run as hr_xai
from applications.hr_rag.app import run as hr_rag
from applications.hr_agent.app import run_app as hr_agent
from applications.hr_multi_agent.app import run as hr_multi_agent

APPLICATION_RUNNERS = {
    "loan_ml": loan_ml,
    "loan_dl": loan_dl,
    "loan_xai": loan_xai,
    "loan_rag": loan_rag,
    "loan_agent": loan_agent,
    "loan_multi_agent": loan_multi_agent,
    "hr_ml": hr_ml,
    "hr_dl": hr_dl,
    "hr_xai": hr_xai,
    "hr_rag": hr_rag,
    "hr_agent": hr_agent,
    "hr_multi_agent": hr_multi_agent,
}