from pathlib import Path
import sys

# Streamlit runs this file with ``app/`` as the import root. Add the repository
# root as well so sibling packages such as ``applications`` are importable.
APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
for import_root in (APP_ROOT, PROJECT_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from core.launcher import current_app
import streamlit as st

from theme.styles import apply_theme

from components.header import show_header
from components.sidebar import render_sidebar

from core.session import initialize

from core.router import route


def main():

    initialize()

    apply_theme()

    render_sidebar()

    if current_app() == "dashboard":
        show_header()

    route()


if __name__ == "__main__":

    main()
