"""
Application Runtime Registry

Maps application IDs to executable entry points.
"""

from applications.loan_ml.app import run as loan_ml
from applications.loan_dl.app import run as loan_dl
from applications.loan_xai.app import run as loan_xai
from applications.loan_rag.app import run as loan_rag

APPLICATION_RUNNERS = {
    "loan_ml": loan_ml,
    "loan_dl": loan_dl,
    "loan_xai": loan_xai,
    "loan_rag": loan_rag,
}