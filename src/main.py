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
_NEGATION_WORDS = {"not", "no", "never", "não", "nunca", "nem"}
_CONTRAST_WORDS = {"but", "however", "mas", "porém", "contudo"}


def analyze_text(text: str) -> dict[str, Any]:
    """Return basic metadata and a lexicon-based, explicitly heuristic sentiment."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Input text cannot be empty")

    words = cleaned_text.split()
    # Keep sentence punctuation as tokens so negation does not leak across sentences.
    tokens = re.findall(r"[a-zà-ÿ]+|[.!?;,]", cleaned_text.casefold())
    positive_count = 0
    negative_count = 0
    negation_remaining = 0

    for token in tokens:
        if token in {".", "!", "?", ";", ","} or token in _CONTRAST_WORDS:
            negation_remaining = 0
            continue
        if token in _NEGATION_WORDS:
            negation_remaining = 3
            continue

        is_positive = token in _POSITIVE_WORDS
        is_negative = token in _NEGATIVE_WORDS
        if is_positive or is_negative:
            # A nearby negation flips a known sentiment word's polarity.
            if negation_remaining > 0:
                is_positive, is_negative = is_negative, is_positive
            positive_count += int(is_positive)
            negative_count += int(is_negative)

        if negation_remaining > 0:
            negation_remaining -= 1

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
