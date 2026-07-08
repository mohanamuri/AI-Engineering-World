from core.application_registry import APPLICATION_RUNNERS
from core.launcher import current_app

from pages.dashboard import render
from pages.documentation import render as render_docs


def route():

    app = current_app()

    if app == "dashboard":
        render()
        return

    if app == "documentation":
        render_docs()
        return

    if app in APPLICATION_RUNNERS:
        APPLICATION_RUNNERS[app]()
        return

    render()