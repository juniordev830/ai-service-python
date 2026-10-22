"""
Unit tests for AI Service
"""

import pytest
from src.main import analyze_text, batch_analyze

def test_analyze_text_success():
    result = analyze_text("This is a great portfolio test")
    assert result["word_count"] == 6
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5

def test_analyze_text_short():
    result = analyze_text("Hello world")
    assert result["word_count"] == 2
    assert result["sentiment"] == "neutral"

def test_analyze_text_empty_raises_error():
    with pytest.raises(ValueError):
        analyze_text("   ")

def test_batch_analyze():
    texts = ["First test text", "Second sample", "  "]
    results = batch_analyze(texts)
    assert len(results) == 2
