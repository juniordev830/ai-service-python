"""Batch comparisons must retain privacy and use comparable denominators."""

import json

import pytest

from src.report import cli_main, compare_texts


def test_different_batch_sizes_compare_shares_not_just_counts():
    report = compare_texts(["good", "bad", "plain", " "], ["good"])
    positive = report["changes"]["positive"]
    assert positive == {
        "count_delta": 0, "current_percent": 33.33,
        "baseline_percent": 100.0, "percentage_point_delta": -66.67,
    }
    assert report["current"]["ignored_empty"] == 1
    assert report["changes"]["negative"]["percentage_point_delta"] == 33.33


@pytest.mark.parametrize("current,baseline", [([], ["good"]), (["bad"], [" "]), ([], [])])
def test_empty_batches_have_undefined_rates_and_changes(current, baseline):
    report = compare_texts(current, baseline)
    for change in report["changes"].values():
        assert change["percentage_point_delta"] is None
        if not report["current"]["analyzed"]:
            assert change["current_percent"] is None
        if not report["baseline"]["analyzed"]:
            assert change["baseline_percent"] is None


def test_comparison_is_private_and_does_not_mutate_inputs():
    current = ["good private-current", "bad"]
    baseline = ["plain private-baseline"]
    before = json.dumps([current, baseline])
    output = json.dumps(compare_texts(current, baseline))
    assert "private-current" not in output
    assert "private-baseline" not in output
    assert json.dumps([current, baseline]) == before


@pytest.mark.parametrize("current,baseline", [(["good"] * 101, []), ([], ["bad"] * 101)])
def test_each_batch_is_independently_bounded(current, baseline):
    with pytest.raises(ValueError, match="100 items"):
        compare_texts(current, baseline)


def test_cli_comparison_and_missing_baseline(tmp_path, capsys):
    current = tmp_path / "current.json"
    baseline = tmp_path / "baseline.json"
    current.write_text('["good", "bad"]', encoding="utf-8")
    baseline.write_text('["bad"]', encoding="utf-8")
    assert cli_main([str(current), "--baseline", str(baseline)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["changes"]["positive"]["percentage_point_delta"] == 50
    with pytest.raises(SystemExit) as error:
        cli_main([str(current), "--baseline", str(tmp_path / "missing.json")])
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Error:" in captured.err
