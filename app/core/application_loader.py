"""
Application Loader

Provides access to the project/app hierarchy from the central registry.
"""

from registry.applications import APPLICATIONS, PROJECTS


def load_projects():
    """Return all registered projects with their capability tiers."""
    return PROJECTS


def load_applications():
    """Return flat list of all apps (backward compatible)."""
    return APPLICATIONS


def get_application(app_id: str) -> dict | None:
    """Return one application by id from the flat list."""
    for app in APPLICATIONS:
        if app["id"] == app_id:
            return app
    return None


def get_live_applications() -> list[dict]:
    """Return only apps with status 'Live'."""
    return [app for app in APPLICATIONS if app["status"] == "Live"]
