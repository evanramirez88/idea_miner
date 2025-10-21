"""Command line interface for Idea Miner."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from . import (
    aggregate_metrics,
    build_markdown_report,
    build_text_report,
    build_timeline,
    derive_theme_overview,
    generate_keyword_summary,
    load_conversation_files,
    suggest_initiatives,
    summarize_sentiment,
)


def _resolve_paths(path_args: Iterable[str]) -> List[Path]:
    paths = []
    for arg in path_args:
        path = Path(arg)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        paths.append(path)
    if not paths:
        raise ValueError("At least one export file must be provided")
    return paths


def run_analysis(paths: Iterable[Path]) -> dict:
    conversations = load_conversation_files(paths)
    metrics = aggregate_metrics(conversations)
    keywords = generate_keyword_summary(conversations)
    sentiment = summarize_sentiment(conversations)
    themes = derive_theme_overview(conversations)
    timeline = build_timeline(conversations)
    initiatives = suggest_initiatives(themes, sentiment)
    return {
        "metrics": metrics,
        "keywords": keywords,
        "sentiment": sentiment,
        "themes": themes,
        "timeline": timeline,
        "initiatives": initiatives,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze ChatGPT exports and synthesize insights")
    parser.add_argument("paths", nargs="+", help="Paths to JSON or ZIP exports")
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the report to. Defaults to stdout.",
    )

    args = parser.parse_args(argv)
    paths = _resolve_paths(args.paths)
    results = run_analysis(paths)

    if args.format == "markdown":
        report = build_markdown_report(**results)
    else:
        report = build_text_report(**results)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
