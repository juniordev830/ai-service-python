"""Core text processing helpers for the experimental AI service."""

import re
import unicodedata
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
_NEGATION_WORDS = {
    "not", "no", "never", "não", "nao", "nunca", "nem",
    "don't", "doesn't", "didn't", "isn't", "wasn't", "weren't",
    "can't", "cannot", "won't",
}
_CONTRAST_WORDS = {"but", "however", "mas", "porém", "contudo"}
MAX_TEXT_CHARACTERS = 10_000
MAX_BATCH_ITEMS = 100


def analyze_text(text: str) -> dict[str, Any]:
    """Return basic metadata and a lexicon-based, explicitly heuristic sentiment."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if len(text) > MAX_TEXT_CHARACTERS:
        raise ValueError(f"text must contain at most {MAX_TEXT_CHARACTERS} characters")
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Input text cannot be empty")

    words = cleaned_text.split()
    # Keep sentence punctuation as tokens so negation does not leak across sentences.
    # Canonically equivalent accents must match the same lexicon entries.
    # Keep the original cleaned text in the response.
    normalized_text = unicodedata.normalize("NFC", cleaned_text.casefold())
    tokens = re.findall(r"[a-zà-ÿ]+(?:['’][a-zà-ÿ]+)?|[.!?;,]", normalized_text)
    positive_count = 0
    negative_count = 0
    negation_remaining = 0

    for token in tokens:
        token = token.replace("’", "'")
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
    if len(texts) > MAX_BATCH_ITEMS:
        raise ValueError(f"batch must contain at most {MAX_BATCH_ITEMS} items")
    results = []
    for index, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError(f"texts[{index}] must be a string")
        if len(text) > MAX_TEXT_CHARACTERS:
            raise ValueError(f"texts[{index}] must contain at most {MAX_TEXT_CHARACTERS} characters")
        if text.strip():
            results.append(analyze_text(text))
    return results


if __name__ == "__main__":
    sample = "Portfolio project showcasing Python AI integration and testing"
    print("AI Analysis Result:", analyze_text(sample))
