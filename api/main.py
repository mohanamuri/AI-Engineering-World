"""
AI Engineering World — FastAPI entry point.

Run from the repo root:
    uvicorn api.main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""

from fastapi import FastAPI

# ── Tier 1-3: ML / DL / XAI ──────────────────────────────────────────────────
from applications.loan_ml.api import router as loan_ml_router
from applications.hr_ml.api import router as hr_ml_router
from applications.loan_dl.api import router as loan_dl_router
from applications.hr_dl.api import router as hr_dl_router
from applications.loan_xai.api import router as loan_xai_router
from applications.hr_xai.api import router as hr_xai_router

# ── Tier 4-6: RAG / Agent / Multi-Agent ──────────────────────────────────────
from applications.loan_rag.api import router as loan_rag_router
from applications.hr_rag.api import router as hr_rag_router
from applications.loan_agent.api import router as loan_agent_router
from applications.hr_agent.api import router as hr_agent_router
from applications.loan_multi_agent.api import router as loan_multi_agent_router
from applications.hr_multi_agent.api import router as hr_multi_agent_router

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

# Tier 1-3
app.include_router(loan_ml_router)
app.include_router(hr_ml_router)
app.include_router(loan_dl_router)
app.include_router(hr_dl_router)
app.include_router(loan_xai_router)
app.include_router(hr_xai_router)

# Tier 4-6
app.include_router(loan_rag_router)
app.include_router(hr_rag_router)
app.include_router(loan_agent_router)
app.include_router(hr_agent_router)
app.include_router(loan_multi_agent_router)
app.include_router(hr_multi_agent_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "AI Engineering World API",
        "version": "1.0.0",
        "docs": "/docs",
        "available_projects": [
            {"name": "Loan ML",           "prefix": "/api/loan-ml"},
            {"name": "HR ML",             "prefix": "/api/hr-ml"},
            {"name": "Loan DL",           "prefix": "/api/loan-dl"},
            {"name": "HR DL",             "prefix": "/api/hr-dl"},
            {"name": "Loan XAI",          "prefix": "/api/loan-xai"},
            {"name": "HR XAI",            "prefix": "/api/hr-xai"},
            {"name": "Loan RAG",          "prefix": "/api/loan-rag"},
            {"name": "HR RAG",            "prefix": "/api/hr-rag"},
            {"name": "Loan Agent",        "prefix": "/api/loan-agent"},
            {"name": "HR Agent",          "prefix": "/api/hr-agent"},
            {"name": "Loan Multi-Agent",  "prefix": "/api/loan-multi-agent"},
            {"name": "HR Multi-Agent",    "prefix": "/api/hr-multi-agent"},
        ],
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
