"""Core text processing helpers for the experimental AI service."""

import re
from typing import Any

_POSITIVE_WORDS = {
    "amazing", "awesome", "excellent", "good", "great", "happy", "love",
    "nice", "positive", "wonderful", "ótimo", "ótima", "excelente",
    "bom", "boa", "feliz", "adoro", "amei", "gostei",
}
_NEGATIVE_WORDS = {
    "awful", "bad", "hate", "horrible", "sad", "terrible", "worst",
    "negative", "poor", "ruim", "péssimo", "péssima", "triste",
    "odeio", "detestei", "odiei",
}


def analyze_text(text: str) -> dict[str, Any]:
    """Return basic metadata and a lexicon-based, explicitly heuristic sentiment."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Input text cannot be empty")

    words = cleaned_text.split()
    tokens = re.findall(r"[a-zà-ÿ]+", cleaned_text.casefold())
    positive_count = sum(token in _POSITIVE_WORDS for token in tokens)
    negative_count = sum(token in _NEGATIVE_WORDS for token in tokens)
    score = positive_count - negative_count

    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # This is a heuristic score, not a statistically calibrated probability.
    confidence = min(0.95, round(0.5 + 0.1 * abs(score), 2))

    return {
        "text": cleaned_text,
        "word_count": len(words),
        "sentiment": sentiment,
        "confidence": confidence,
        "language": "undetermined",
        "method": "lexicon_heuristic",
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
