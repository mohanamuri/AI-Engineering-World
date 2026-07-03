from registry.applications import APPLICATIONS
from services.platform_stats import dashboard_stats


def total_modules():

    return dashboard_stats()["modules"]


def total_projects():

    return dashboard_stats()["applications"]


def total_models():

    return dashboard_stats()["models"]


def applications():

    return APPLICATIONS