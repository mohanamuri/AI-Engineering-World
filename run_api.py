"""
Start the AI Engineering World FastAPI server.

Usage:
    python run_api.py

Or with auto-reload during development:
    uvicorn api.main:app --reload --port 8000

Swagger UI → http://localhost:8000/docs
ReDoc       → http://localhost:8000/redoc
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
