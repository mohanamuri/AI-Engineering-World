from registry.applications import APPLICATIONS


def dashboard_stats() -> dict:
    live_count = sum(1 for a in APPLICATIONS if a["status"] == "Live")

    return {
        "live": live_count,
        "tiers": 6,
        "models": 3,
        "open_source": "100%",
    }
