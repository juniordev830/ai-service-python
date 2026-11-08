"""Privacy-minded aggregate reports over the existing lexicon text analyzer.

No external APIs, model inference or persistence is performed. The sentiment
labels are heuristic demonstrations, not validated predictions.
"""

from __future__ import annotations

import argparse
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


def cli_main(argv: Sequence[str] | None = None) -> int:
    """Entry point: print JSON summary to stdout, errors to stderr."""
    parser = argparse.ArgumentParser(
        description="Summarize sentiment labels in a local JSON list of text samples"
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON file containing strings")
    args = parser.parse_args(argv)

    try:
        texts = load_texts(args.input)
        summary = summarize_texts(texts)
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli_main())
