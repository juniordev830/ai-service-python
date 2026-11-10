"""CSV reports expose numeric distributions without source text."""

import csv
import io
import json

import pytest

from src.report import cli_main, compare_texts, report_to_csv, summarize_texts


def read_rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def test_summary_csv_uses_analyzed_count_as_denominator():
    rows = read_rows(report_to_csv(summarize_texts(["good", "bad", " "])))
    assert rows == [
        {"sentiment": "positive", "count": "1", "percent": "50.0"},
        {"sentiment": "negative", "count": "1", "percent": "50.0"},
        {"sentiment": "neutral", "count": "0", "percent": "0.0"},
    ]


def test_comparison_csv_preserves_counts_and_signed_deltas():
    rows = read_rows(report_to_csv(compare_texts(["good", "bad"], ["good"])))
    assert rows[0] == {
        "sentiment": "positive", "current_count": "1", "baseline_count": "1",
        "count_delta": "0", "current_percent": "50.0", "baseline_percent": "100.0",
        "percentage_point_delta": "-50.0",
    }
    assert rows[1]["count_delta"] == "1"
    assert rows[1]["percentage_point_delta"] == "50.0"


def test_empty_summary_and_baseline_export_undefined_rates_as_blank_cells():
    rows = read_rows(report_to_csv(summarize_texts([" "])))
    assert all(row["count"] == "0" and row["percent"] == "" for row in rows)
    comparison = read_rows(report_to_csv(compare_texts(["good"], [])))
    assert all(row["baseline_percent"] == "" and row["percentage_point_delta"] == ""
               for row in comparison)


def test_csv_excludes_original_text_including_formula_like_samples():
    report = compare_texts(['=HYPERLINK("private") good', "secret,with\nlines"], ["@private bad"])
    original = json.dumps(report)
    text = report_to_csv(report)
    assert "private" not in text
    assert "secret" not in text
    assert "HYPERLINK" not in text
    assert len(read_rows(text)) == 3
    assert json.dumps(report) == original


@pytest.mark.parametrize("baseline", [False, True])
def test_cli_exports_csv_with_optional_baseline(tmp_path, capsys, baseline):
    sample = tmp_path / "samples.json"
    sample.write_text('["good", "bad"]', encoding="utf-8")
    args = [str(sample), "--format", "csv"]
    if baseline:
        args += ["--baseline", str(sample)]
    assert cli_main(args) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    rows = read_rows(captured.out)
    assert len(rows) == 3
    assert rows[0]["current_percent" if baseline else "percent"] == "50.0"


def test_cli_invalid_format_and_invalid_input_emit_no_csv(tmp_path, capsys):
    sample = tmp_path / "bad.json"
    sample.write_text('{"invalid":true}', encoding="utf-8")
    for fmt in ("csv", "xml"):
        with pytest.raises(SystemExit) as error:
            cli_main([str(sample), "--format", fmt])
        assert error.value.code == 2
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err
