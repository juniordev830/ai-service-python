"""Privacy-minded aggregate reports over the existing lexicon text analyzer.

No external APIs, model inference or persistence is performed. The sentiment
labels are heuristic demonstrations, not validated predictions.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from typing import Any, Sequence

from .main import batch_analyze

MAX_INPUT_BYTES = 2_000_000
SENTIMENT_LABELS = ("positive", "negative", "neutral")


def summarize_texts(texts: list[str]) -> dict[str, Any]:
    """Return aggregate statistics without including any of the original text.

    Empty/whitespace-only strings are ignored by the existing analyzer.
    Validation and batch size limits are delegated to batch_analyze.
    """
    if not isinstance(texts, list):
        raise TypeError("texts must be a list")
    results = batch_analyze(texts)
    counts = {label: 0 for label in SENTIMENT_LABELS}
    total_words = 0
    longest_text_words = 0
    for result in results:
        sentiment = result["sentiment"]
        if sentiment not in counts:
            raise ValueError("Unexpected sentiment label in analysis result")
        counts[sentiment] += 1
        words = result["word_count"]
        total_words += words
        longest_text_words = max(longest_text_words, words)

    return {
        "method": "lexicon_heuristic",
        "submitted": len(texts),
        "analyzed": len(results),
        "ignored_empty": len(texts) - len(results),
        "sentiments": counts,
        "total_words": total_words,
        "longest_text_words": longest_text_words,
        "notice": "Heuristic demonstration; not a calibrated AI prediction.",
    }


def load_texts(path: Path) -> list[str]:
    """Read a local UTF-8 JSON list, size-capped before parsing."""
    if not path.is_file():
        raise ValueError("Input path must reference an existing regular file")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"Input exceeds {MAX_INPUT_BYTES} bytes")
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"Input exceeds {MAX_INPUT_BYTES} bytes")
    try:
        data: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Input must be valid UTF-8 JSON") from exc

    if not isinstance(data, list):
        raise ValueError("Input JSON root must be a list of strings")
    if any(not isinstance(text, str) for text in data):
        raise ValueError("Every item in input JSON must be a string")
    return data


def compare_texts(current: list[str], baseline: list[str]) -> dict[str, Any]:
    """Compare label shares between batches without exposing source text.

    Shares use analyzed samples, excluding empty entries. An empty side has
    no defined percentage; do not imply a zero rate or a measured change.
    """
    current_summary = summarize_texts(current)
    baseline_summary = summarize_texts(baseline)
    changes = {}
    for label in SENTIMENT_LABELS:
        current_count = current_summary["sentiments"][label]
        baseline_count = baseline_summary["sentiments"][label]
        current_rate = (100 * current_count / current_summary["analyzed"]
                        if current_summary["analyzed"] else None)
        baseline_rate = (100 * baseline_count / baseline_summary["analyzed"]
                         if baseline_summary["analyzed"] else None)
        changes[label] = {
            "count_delta": current_count - baseline_count,
            "current_percent": round(current_rate, 2) if current_rate is not None else None,
            "baseline_percent": round(baseline_rate, 2) if baseline_rate is not None else None,
            "percentage_point_delta": (
                round(current_rate - baseline_rate, 2)
                if current_rate is not None and baseline_rate is not None else None
            ),
        }
    return {
        "current": current_summary,
        "baseline": baseline_summary,
        "changes": changes,
        "notice": "Descriptive heuristic comparison; not statistical significance or a quality score.",
    }


def report_to_csv(report: dict[str, Any]) -> str:
    """Export label distributions from summarize_texts/compare_texts.

    Only fixed labels and numeric aggregates are exported. Source text and
    user-controlled file names are never written to spreadsheet cells.
    """
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    if "changes" in report:
        writer.writerow([
            "sentiment", "current_count", "baseline_count", "count_delta",
            "current_percent", "baseline_percent", "percentage_point_delta",
        ])
        for label in SENTIMENT_LABELS:
            change = report["changes"][label]
            writer.writerow([
                label, report["current"]["sentiments"][label],
                report["baseline"]["sentiments"][label], change["count_delta"],
                change["current_percent"], change["baseline_percent"],
                change["percentage_point_delta"],
            ])
    else:
        writer.writerow(["sentiment", "count", "percent"])
        for label in SENTIMENT_LABELS:
            count = report["sentiments"][label]
            percent = round(100 * count / report["analyzed"], 2) if report["analyzed"] else None
            writer.writerow([label, count, percent])
    return output.getvalue()


def cli_main(argv: Sequence[str] | None = None) -> int:
    """Print JSON summary or CSV distributions to stdout, errors to stderr."""
    parser = argparse.ArgumentParser(
        description="Summarize sentiment labels in a local JSON list of text samples"
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON file containing strings")
    parser.add_argument("--baseline", type=Path, help="Compare with a previous UTF-8 JSON batch")
    parser.add_argument("--format", choices=("json", "csv"), default="json",
                        help="Output format (default: json); CSV exports label distributions")
    args = parser.parse_args(argv)

    try:
        texts = load_texts(args.input)
        summary = (compare_texts(texts, load_texts(args.baseline))
                   if args.baseline is not None else summarize_texts(texts))
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")

    if args.format == "csv":
        print(report_to_csv(summary), end="")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli_main())
