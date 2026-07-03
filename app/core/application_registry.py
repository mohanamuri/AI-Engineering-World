"""
Application Runtime Registry

Maps application IDs to executable entry points.
"""

from applications.loan_ml.app import run as loan_ml
from applications.loan_dl.app import run as loan_dl

APPLICATION_RUNNERS = {
    "loan_ml": loan_ml,
    "loan_dl": loan_dl,
}