"""Command line interface for the Idea Miner application."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .analysis import Analyzer
from .loader import iter_conversations
from .report import save_json_report, save_markdown_report


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze ChatGPT conversation exports")
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more JSON or ZIP exports to analyze",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis_output"),
        help="Directory where reports will be written (default: analysis_output)",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:
    args = _parse_args(argv)
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = [Path(path) for path in args.paths]
    analyzer = Analyzer()
    conversations = list(iter_conversations(paths))
    if not conversations:
        raise SystemExit("No conversations were discovered in the provided paths.")

    aggregate = analyzer.aggregate(conversations)

    json_path = output_dir / "analysis_report.json"
    md_path = output_dir / "analysis_report.md"

    save_json_report(aggregate, json_path)
    save_markdown_report(aggregate, md_path)

    print(f"Analysis complete. Reports saved to {output_dir}.")
    print(f"- JSON: {json_path}")
    print(f"- Markdown: {md_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
