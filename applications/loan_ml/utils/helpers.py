"""Shared presentation-neutral helpers for the loan ML application."""


def format_bytes(size_bytes: int) -> str:
    """Return a compact human-readable representation of a byte count."""
    if size_bytes < 0:
        raise ValueError("Byte count cannot be negative.")
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
