"""Tests for the JSON aggregation CLI: no external services or NLP models."""

import json

import pytest

from src.report import MAX_INPUT_BYTES, cli_main, load_texts, summarize_texts


def test_mixed_sentiments_and_empty_items_are_counted():
    original = ["Adorei, ótimo trabalho!", "I hate this", "registro normal", "  ", ""]
    report = summarize_texts(original)
    assert report["submitted"] == 5
    assert report["analyzed"] == 3
    assert report["ignored_empty"] == 2
    assert report["sentiments"] == {"positive": 1, "negative": 1, "neutral": 1}
    assert report["total_words"] == 8
    assert report["longest_text_words"] == 3
    assert report["method"] == "lexicon_heuristic"
    assert original[0] == "Adorei, ótimo trabalho!"


def test_empty_batch_generates_explicit_zeros():
    report = summarize_texts([])
    assert report["analyzed"] == 0
    assert report["sentiments"] == {"positive": 0, "negative": 0, "neutral": 0}
    assert report["total_words"] == 0
    assert report["longest_text_words"] == 0


def test_does_not_leak_original_text_into_report():
    sensitive_example = "Minha anotação pessoal fictícia: odeio atrasos!"
    output = json.dumps(summarize_texts([sensitive_example]), ensure_ascii=False)
    assert sensitive_example not in output
    assert "anotação pessoal" not in output
    assert "lexicon_heuristic" in output


def test_batch_limits_and_invalid_items():
    with pytest.raises(TypeError):
        summarize_texts("not a list")
    with pytest.raises(TypeError):
        summarize_texts(["texto válido", 42])
    with pytest.raises(ValueError, match="100"):
        summarize_texts(["ótimo"] * 101)
    with pytest.raises(ValueError, match="10000"):
        summarize_texts(["x" * 10_001])


def test_load_valid_local_json(tmp_path):
    file = tmp_path / "sample.json"
    file.write_text(json.dumps(["ótimo", "ruim"], ensure_ascii=False), encoding="utf-8")
    assert load_texts(file) == ["ótimo", "ruim"]


@pytest.mark.parametrize("payload", ['{"text":"ótimo"}', '[true]', '[] not json', '\xff'])
def test_rejects_wrong_json_shapes_or_encoding(tmp_path, payload):
    file = tmp_path / "bad.json"
    file.write_bytes(payload.encode("latin1"))
    with pytest.raises(ValueError):
        load_texts(file)


def test_utf8_bom_is_accepted_without_altering_accented_text(tmp_path):
    file = tmp_path / "bom.json"
    file.write_bytes(bytes([0xEF, 0xBB, 0xBF]) + '["ótimo", "não gostei"]'.encode("utf-8"))
    assert load_texts(file) == ["ótimo", "não gostei"]


def test_utf16_bom_is_not_accepted_as_utf8(tmp_path):
    file = tmp_path / "utf16.json"
    file.write_bytes('["bom"]'.encode("utf-16"))
    with pytest.raises(ValueError, match="UTF-8 JSON"):
        load_texts(file)


def test_rejects_oversized_local_file(tmp_path):
    file = tmp_path / "large.json"
    file.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
    with pytest.raises(ValueError, match="exceeds"):
        load_texts(file)


def test_cli_writes_json_summary_without_repeating_text(tmp_path, capsys):
    file = tmp_path / "samples.json"
    file.write_text(json.dumps(["boa notícia", "ruim", " "]), encoding="utf-8")
    result = cli_main([str(file)])
    assert result == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    parsed = json.loads(captured.out)
    assert parsed["sentiments"]["positive"] == 1
    assert parsed["sentiments"]["negative"] == 1
    assert parsed["ignored_empty"] == 1
    assert "boa notícia" not in captured.out


def test_cli_errors_exit_with_nonzero_code(tmp_path, capsys):
    missing = tmp_path / "nonexistent.json"
    with pytest.raises(SystemExit) as exc:
        cli_main([str(missing)])
    assert exc.value.code == 2
    assert "Error:" in capsys.readouterr().err


def test_sentiment_percentages_use_analyzed_samples_only():
    report = summarize_texts(["good", "bad", "ordinary", " ", ""])
    assert report["analyzed"] == 3
    assert report["sentiment_percentages"] == {
        "positive": 33.33,
        "negative": 33.33,
        "neutral": 33.33,
    }


def test_empty_report_percentages_are_zero():
    report = summarize_texts([" ", ""])
    assert report["analyzed"] == 0
    assert report["sentiment_percentages"] == {
        "positive": 0.0,
        "negative": 0.0,
        "neutral": 0.0,
    }
