from registry.applications import APPLICATIONS, PROJECTS


def dashboard_stats() -> dict:
    live_count = sum(1 for a in APPLICATIONS if a["status"] == "Live")
    max_tiers = max((len(p["apps"]) for p in PROJECTS), default=0)

    return {
        "projects": len(PROJECTS),
        "capabilities": max_tiers,
        "live": live_count,
        "applications": len(APPLICATIONS),
        "status": "Active",
    }
