"""Malformed or deeply nested JSON must raise a stable validation error."""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from src.report import load_texts, cli_main


def test_deeply_nested_json_is_rejected_with_value_error():
    with TemporaryDirectory() as folder:
        path = Path(folder) / "nested.json"
        path.write_text("[" * 1200 + "0" + "]" * 1200, encoding="utf-8")
        with pytest.raises(ValueError, match="valid UTF-8 JSON"):
            load_texts(path)


def test_deeply_nested_json_reports_clean_cli_error(capsys):
    with TemporaryDirectory() as folder:
        path = Path(folder) / "nested.json"
        path.write_text("[" * 1200 + "0" + "]" * 1200, encoding="utf-8")
        with pytest.raises(SystemExit) as error:
            cli_main([str(path)])
        assert error.value.code == 2
        captured = capsys.readouterr()
        assert "Input must be valid UTF-8 JSON" in captured.err
        assert captured.out == ""
