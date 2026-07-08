"""
AI Engineering World — FastAPI entry point.

Run from the repo root:
    uvicorn api.main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""

from fastapi import FastAPI
from applications.loan_ml.api import router as loan_ml_router
from applications.hr_ml.api import router as hr_ml_router
from applications.loan_dl.api import router as loan_dl_router
from applications.hr_dl.api import router as hr_dl_router
from applications.loan_xai.api import router as loan_xai_router
from applications.hr_xai.api import router as hr_xai_router

app = FastAPI(
    title="AI Engineering World API",
    description=(
        "REST API exposing the ML pipelines built in AI Engineering World. "
        "Each project's services are wrapped as API endpoints — "
        "same logic, different entry point."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(loan_ml_router)
app.include_router(hr_ml_router)
app.include_router(loan_dl_router)
app.include_router(hr_dl_router)
app.include_router(loan_xai_router)
app.include_router(hr_xai_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "AI Engineering World API",
        "version": "1.0.0",
        "docs": "/docs",
        "available_projects": [
            {"name": "Loan ML", "prefix": "/api/loan-ml"},
        ],
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
