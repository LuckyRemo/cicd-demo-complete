"""Command-line entry point for the demo package."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict

from .stats import summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pycicd-demo",
        description="Count words in a string or on stdin.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to analyse. When omitted, text is read from stdin.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="How many frequent words to show (default: 5).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()

    if not text.strip():
        print("error: input text is empty", file=sys.stderr)
        return 2
    if args.top < 1:
        print("error: --top must be >= 1", file=sys.stderr)
        return 2

    summary = summarize(text, top_n=args.top)
    if args.json:
        print(json.dumps(asdict(summary), ensure_ascii=False))
        return 0

    print(f"words:          {summary.words}")
    print(f"unique words:   {summary.unique_words}")
    print(f"reading time:   {summary.reading_minutes} min")
    print("top words:")
    for word, count in summary.top:
        print(f"  {word:<12} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
