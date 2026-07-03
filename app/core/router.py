from core.application_registry import APPLICATION_RUNNERS
from core.launcher import current_app

from pages.dashboard import render


def route():

    app = current_app()

    if app == "dashboard":
        render()
        return

    if app in APPLICATION_RUNNERS:
        APPLICATION_RUNNERS[app]()
        return

    render()