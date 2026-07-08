"""
Start the AI Engineering World FastAPI server locally.

Usage:
    python run_api.py

Or with auto-reload during development:
    uvicorn api.main:app --reload --port 8000

Local Swagger UI  → http://localhost:8000/docs
Live API (Render) → https://ai-engineering-world.onrender.com/docs
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
