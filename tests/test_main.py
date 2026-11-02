"""Regression tests for the experimental text analysis helpers."""

import pytest

from src.main import analyze_text, batch_analyze


def test_analyze_text_success():
    result = analyze_text("This is a great portfolio test")
    assert result["word_count"] == 6
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5
    assert result["language"] == "undetermined"


def test_analyze_text_short():
    result = analyze_text("Hello world")
    assert result["word_count"] == 2
    assert result["sentiment"] == "neutral"


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_analyze_text_empty_raises_error(text):
    with pytest.raises(ValueError):
        analyze_text(text)


@pytest.mark.parametrize("text", [None, 42, ["not", "text"]])
def test_analyze_text_rejects_non_strings(text):
    with pytest.raises(TypeError, match="text must be a string"):
        analyze_text(text)


def test_batch_analyze_ignores_empty_samples():
    results = batch_analyze(["First test text", "Second sample", "  "])
    assert len(results) == 2


def test_batch_analyze_rejects_non_list():
    with pytest.raises(TypeError, match="texts must be a list of strings"):
        batch_analyze("not a list")


def test_batch_analyze_rejects_non_string_item():
    with pytest.raises(TypeError, match=r"texts\[1\] must be a string"):
        batch_analyze(["valid text", None])


def test_sentiment_detects_negative_words_independently_of_text_length():
    result = analyze_text("This is a terrible and bad experience")
    assert result["sentiment"] == "negative"
    assert result["confidence"] > 0.5
    assert result["method"] == "lexicon_heuristic"


def test_sentiment_is_case_insensitive_and_ignores_punctuation():
    result = analyze_text("GREAT!!!")
    assert result["sentiment"] == "positive"


def test_balanced_positive_and_negative_terms_are_neutral():
    result = analyze_text("good but bad")
    assert result["sentiment"] == "neutral"
    assert result["confidence"] == 0.5


def test_sentiment_supports_basic_portuguese_terms():
    assert analyze_text("Estou feliz, gostei!")["sentiment"] == "positive"
    assert analyze_text("Estou triste e ruim")["sentiment"] == "negative"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("not good", "negative"),
        ("never excellent", "negative"),
        ("não gostei", "negative"),
        ("não é ruim", "positive"),
        ("not good. terrible", "negative"),
        ("not good but great", "neutral"),
    ],
)
def test_sentiment_handles_simple_negation_and_scope(text, expected):
    result = analyze_text(text)
    assert result["sentiment"] == expected
    assert result["method"] == "lexicon_heuristic"


def test_language_is_not_claimed_without_language_detection():
    result = analyze_text("Olá, este é um texto em português")
    assert result["language"] == "undetermined"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("I don't love this update", "negative"),
        ("This isn't good", "negative"),
        ("I can’t hate this", "positive"),
        ("nao gostei do atendimento", "negative"),
        ("I won't hate this", "positive"),
    ],
)
def test_negations_with_contractions_and_ascii_portuguese(text, expected):
    assert analyze_text(text)["sentiment"] == expected


def test_oversized_text_is_rejected_before_processing():
    with pytest.raises(ValueError, match="at most 10000 characters"):
        analyze_text("a" * 10001)


def test_batch_limits_number_of_items():
    with pytest.raises(ValueError, match="at most 100 items"):
        batch_analyze(["good"] * 101)


def test_batch_accepts_maximum_size_and_checks_each_item_length():
    assert len(batch_analyze(["good"] * 100)) == 100
    with pytest.raises(ValueError, match="at most 10000 characters"):
        batch_analyze(["good", "x" * 10001])
