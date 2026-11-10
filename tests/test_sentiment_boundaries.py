"""Regression tests for the heuristic sentiment analyzer."""

import pytest

from src.main import (
    MAX_BATCH_ITEMS,
    MAX_TEXT_CHARACTERS,
    analyze_text,
    batch_analyze,
)


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        ("not good", "negative"),
        ("não gostei", "negative"),
        ("not bad", "positive"),
        ("good, not bad", "positive"),
        ("not good. excellent", "neutral"),
        ("bad but great", "neutral"),
        ("ordinary words", "neutral"),
    ],
)
def test_sentiment_and_negation_boundaries(sample, expected):
    assert analyze_text(sample)["sentiment"] == expected


def test_trimmed_text_and_word_count():
    result = analyze_text("  very good  ")
    assert result["text"] == "very good"
    assert result["word_count"] == 2
    assert result["method"] == "lexicon_heuristic"


def test_empty_and_non_string_inputs():
    with pytest.raises(ValueError):
        analyze_text("  ")
    with pytest.raises(TypeError):
        analyze_text(None)


def test_text_length_boundary():
    assert analyze_text("a" * MAX_TEXT_CHARACTERS)["word_count"] == 1
    with pytest.raises(ValueError):
        analyze_text("a" * (MAX_TEXT_CHARACTERS + 1))


def test_batch_skips_blank_entries_without_losing_order():
    results = batch_analyze(["good", " ", "bad"])
    assert [result["sentiment"] for result in results] == ["positive", "negative"]


def test_batch_size_and_item_types():
    assert len(batch_analyze(["ok"] * MAX_BATCH_ITEMS)) == MAX_BATCH_ITEMS
    with pytest.raises(ValueError):
        batch_analyze(["ok"] * (MAX_BATCH_ITEMS + 1))
    with pytest.raises(TypeError, match=r"texts\\[1\\]"):
        batch_analyze(["good", 123])
