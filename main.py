"""Root entry point for Streamlit Community Cloud deployment.

Streamlit Cloud requires the main file to be at the repository root.
This shim adds the necessary paths and delegates to app/main.py.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
APP_ROOT = PROJECT_ROOT / "app"

for p in (str(PROJECT_ROOT), str(APP_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import main  # noqa: E402

main()
