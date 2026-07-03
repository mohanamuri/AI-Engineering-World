from registry.applications import APPLICATIONS


def dashboard_stats():

    return {

        "modules":3,

        "applications":len(APPLICATIONS),

        "models":len(APPLICATIONS),

        "deployments":0,

        "status":"Active"

    }