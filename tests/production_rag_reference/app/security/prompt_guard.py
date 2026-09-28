import re

PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+hidden\s+instructions",
    r"developer\s+message",
    r"bypass\s+(security|access|authorization)",
]

def detect_prompt_injection(text: str) -> bool:
    value = text.lower()
    return any(re.search(p, value) for p in PATTERNS)

def sanitize_user_query(text: str) -> str:
    return " ".join(text.strip().split())

def validate_query(text: str) -> None:
    if detect_prompt_injection(text):
        raise ValueError("Potential prompt-injection attempt detected")
