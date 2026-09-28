from pathlib import Path

def load_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def load_documents(directory: str) -> list[dict]:
    # Add PDF/DOCX/HTML/object-store loaders in a real implementation.
    return [
        {"source": str(p), "title": p.stem, "text": load_text_file(str(p))}
        for p in Path(directory).glob("**/*.txt")
    ]
