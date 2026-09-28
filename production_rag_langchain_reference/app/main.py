"""
FastAPI application entry point for the production RAG system.

Initializes all components and sets up middleware.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.api.routes import router
from app.core.logging import configure_logging

# Configure logging first
configure_logging()

# Create FastAPI app
app = FastAPI(
    title="Production RAG Reference (LangChain Edition)",
    version="0.1.0",
    description="Production-grade RAG system using LangChain",
)

# Include routers
app.include_router(router, prefix="/v1")


@app.get("/health")
def health():
    """Health check endpoint for load balancers."""
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint.

    Use this with monitoring systems like Prometheus:
    scrape_configs:
      - job_name: 'rag'
        static_configs:
          - targets: ['localhost:8000']
    """
    return JSONResponse(
        content=generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST,
    )


# Error handlers can be added here for consistent error responses
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Catch-all error handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
