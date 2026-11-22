import pytest
from src.main import analyze_text


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        ("not not good", "positive"),
        ("não nunca ruim", "negative"),
        ("not not bad", "negative"),
        ("not not good but terrible", "neutral"),
        ("not good", "negative"),
        ("not good. good", "neutral"),
    ],
)
def test_double_negation_parity(sample, expected):
    result = analyze_text(sample)
    assert result["sentiment"] == expected
    assert result["method"] == "lexicon_heuristic"
