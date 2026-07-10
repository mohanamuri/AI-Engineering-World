from registry.applications import APPLICATIONS


def dashboard_stats() -> dict:
    live_count = sum(1 for a in APPLICATIONS if a["status"] == "live")

    return {
        "live": live_count,
        "tiers": 6,
        "techniques": 14,
        "models": 3,
    }
