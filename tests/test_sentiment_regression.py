"""Regression tests for multilingual sentiment and bounded batch processing."""

import pytest

from src.main import MAX_BATCH_ITEMS, MAX_TEXT_CHARACTERS, analyze_text, batch_analyze


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        ("ótimo", "positive"),
        ("péssimo", "negative"),
        ("registro sem adjetivos", "neutral"),
        ("não é bom", "negative"),
        ("not bad", "positive"),
        ("good. not bad", "positive"),
        ("not good, excellent", "neutral"),
        ("good mas ruim", "neutral"),
        ("I don't like this", "neutral"),
    ],
)
def test_sentiment_regression(sample, expected):
    result = analyze_text(sample)
    assert result["sentiment"] == expected
    assert result["method"] == "lexicon_heuristic"


@pytest.mark.parametrize("sample", ["", " ", "\n\t"])
def test_empty_text_is_rejected(sample):
    with pytest.raises(ValueError, match="empty"):
        analyze_text(sample)


def test_invalid_input_types_are_rejected():
    with pytest.raises(TypeError):
        analyze_text(None)
    with pytest.raises(TypeError):
        batch_analyze("good")
    with pytest.raises(TypeError, match=r"texts\[1\]"):
        batch_analyze(["good", None])


def test_character_limits_are_enforced():
    assert analyze_text("a" * MAX_TEXT_CHARACTERS)["word_count"] == 1
    with pytest.raises(ValueError, match="at most"):
        analyze_text("a" * (MAX_TEXT_CHARACTERS + 1))


def test_batch_limits_and_empty_filtering():
    assert len(batch_analyze(["good"] * MAX_BATCH_ITEMS)) == MAX_BATCH_ITEMS
    assert batch_analyze(["", "  ", "good"])[0]["sentiment"] == "positive"
    with pytest.raises(ValueError, match="at most"):
        batch_analyze(["good"] * (MAX_BATCH_ITEMS + 1))


def test_whitespace_is_trimmed_without_mutating_input():
    original = "  bom trabalho  "
    result = analyze_text(original)
    assert result["text"] == "bom trabalho"
    assert original == "  bom trabalho  "
