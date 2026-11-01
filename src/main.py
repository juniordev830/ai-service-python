"""Core text processing helpers for the experimental AI service."""

from typing import Any


def analyze_text(text: str) -> dict[str, Any]:
    """Return basic metadata and a clearly heuristic sentiment label."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Input text cannot be empty")

    words = cleaned_text.split()
    word_count = len(words)
    confidence = min(0.99, round(0.5 + (word_count * 0.05), 2))
    sentiment = "positive" if word_count > 3 else "neutral"

    return {
        "text": cleaned_text,
        "word_count": word_count,
        "sentiment": sentiment,
        "confidence": confidence,
        "language": "undetermined",
    }


def batch_analyze(texts: list[str]) -> list[dict[str, Any]]:
    """Analyze a list of strings, ignoring empty or whitespace-only samples."""
    if not isinstance(texts, list):
        raise TypeError("texts must be a list of strings")
    results = []
    for index, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError(f"texts[{index}] must be a string")
        if text.strip():
            results.append(analyze_text(text))
    return results


if __name__ == "__main__":
    sample = "Portfolio project showcasing Python AI integration and testing"
    print("AI Analysis Result:", analyze_text(sample))
