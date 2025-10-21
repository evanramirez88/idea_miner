"""Reporting utilities for Idea Miner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .analysis import AggregateAnalysis, summarize_for_markdown


def save_json_report(analysis: AggregateAnalysis, path: Path) -> None:
    """Persist the aggregate analysis to a JSON file."""

    serializable = {
        "summary": {
            "total_conversations": analysis.total_conversations,
            "total_messages": analysis.total_messages,
            "total_words": analysis.total_words,
            "average_sentiment": analysis.sentiment_average,
            "time_span": analysis.time_span,
        },
        "sentiment": analysis.sentiment_counts,
        "top_keywords": analysis.top_keywords,
        "themes": {
            "counts": analysis.theme_counts,
            "examples": analysis.theme_examples,
            "ideas": analysis.ideas,
        },
    }

    path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def save_markdown_report(analysis: AggregateAnalysis, path: Path) -> None:
    """Persist a Markdown version of the analysis."""

    markdown = summarize_for_markdown(analysis)
    path.write_text(markdown, encoding="utf-8")
