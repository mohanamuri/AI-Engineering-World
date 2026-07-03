"""
Application Loader

Loads all registered applications
from the central registry.
"""

from registry.applications import APPLICATIONS


def load_applications():
    """
    Return all registered applications.
    """
    return APPLICATIONS


def get_application(app_id):
    """
    Return one application by id.
    """

    for app in APPLICATIONS:

        if app["id"] == app_id:
            return app

    return None