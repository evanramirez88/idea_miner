"""Reporting utilities for Idea Miner."""
from __future__ import annotations

from typing import List

from .analyzer import (
    AggregateMetrics,
    KeywordSummary,
    SentimentBreakdown,
    ThemeOverview,
    TimelinePoint,
)


def build_text_report(
    metrics: AggregateMetrics,
    keywords: KeywordSummary,
    sentiment: SentimentBreakdown,
    themes: ThemeOverview,
    timeline: List[TimelinePoint],
    initiatives: List[str],
) -> str:
    lines: List[str] = []
    lines.append("=== Idea Miner Summary ===")
    lines.append("")
    lines.append("Key Metrics:")
    lines.append(f"  Conversations: {metrics.conversation_count}")
    lines.append(f"  Messages: {metrics.message_count}")
    lines.append(f"  Participants: {', '.join(metrics.participants) if metrics.participants else 'N/A'}")
    lines.append(f"  First Interaction: {metrics.first_interaction or 'Unknown'}")
    lines.append(f"  Last Interaction: {metrics.last_interaction or 'Unknown'}")
    lines.append("")

    lines.append("Top Keywords:")
    for token, count in keywords.tokens[:10]:
        lines.append(f"  {token}: {count}")
    if keywords.bigrams:
        lines.append("")
        lines.append("Top Bigrams:")
        for bigram, count in keywords.bigrams[:5]:
            lines.append(f"  {bigram}: {count}")
    lines.append("")

    lines.append("Sentiment:")
    lines.append(f"  Positive: {sentiment.positive}")
    lines.append(f"  Neutral: {sentiment.neutral}")
    lines.append(f"  Negative: {sentiment.negative}")
    lines.append(f"  Average Compound: {sentiment.average_compound:.3f}")
    lines.append("")

    lines.append("Themes:")
    for theme, count in themes.counts.items():
        keyword_list = ", ".join(themes.top_keywords.get(theme, []))
        lines.append(f"  {theme}: {count} ({keyword_list})")
    lines.append("")

    if timeline:
        lines.append("Timeline (Conversations per month):")
        for point in timeline:
            lines.append(f"  {point.label}: {point.conversations}")
        lines.append("")

    lines.append("Strategic Initiatives:")
    for idea in initiatives:
        lines.append(f"  - {idea}")

    return "\n".join(lines)


def build_markdown_report(
    metrics: AggregateMetrics,
    keywords: KeywordSummary,
    sentiment: SentimentBreakdown,
    themes: ThemeOverview,
    timeline: List[TimelinePoint],
    initiatives: List[str],
) -> str:
    lines: List[str] = []
    lines.append("# Idea Miner Report")
    lines.append("")
    lines.append("## Key Metrics")
    lines.append(f"- **Conversations:** {metrics.conversation_count}")
    lines.append(f"- **Messages:** {metrics.message_count}")
    participant_text = ", ".join(metrics.participants) if metrics.participants else "N/A"
    lines.append(f"- **Participants:** {participant_text}")
    lines.append(f"- **First Interaction:** {metrics.first_interaction or 'Unknown'}")
    lines.append(f"- **Last Interaction:** {metrics.last_interaction or 'Unknown'}")
    lines.append("")

    lines.append("## Top Keywords")
    if keywords.tokens:
        lines.append("| Keyword | Count |")
        lines.append("| --- | ---: |")
        for token, count in keywords.tokens[:15]:
            lines.append(f"| {token} | {count} |")
    else:
        lines.append("No keyword data available.")
    if keywords.bigrams:
        lines.append("")
        lines.append("### Top Bigrams")
        lines.append("| Bigram | Count |")
        lines.append("| --- | ---: |")
        for bigram, count in keywords.bigrams[:10]:
            lines.append(f"| {bigram} | {count} |")
    lines.append("")

    lines.append("## Sentiment")
    lines.append(f"- Positive messages: **{sentiment.positive}**")
    lines.append(f"- Neutral messages: **{sentiment.neutral}**")
    lines.append(f"- Negative messages: **{sentiment.negative}**")
    lines.append(f"- Average compound score: **{sentiment.average_compound:.3f}**")
    lines.append("")

    lines.append("## Themes")
    for theme, count in themes.counts.items():
        keywords_for_theme = themes.top_keywords.get(theme)
        if keywords_for_theme:
            lines.append(f"- **{theme}** ({count} conversations): {', '.join(keywords_for_theme)}")
        else:
            lines.append(f"- **{theme}** ({count} conversations)")
    lines.append("")

    if timeline:
        lines.append("## Timeline")
        lines.append("| Month | Conversations |")
        lines.append("| --- | ---: |")
        for point in timeline:
            lines.append(f"| {point.label} | {point.conversations} |")
        lines.append("")

    lines.append("## Strategic Initiatives")
    for idea in initiatives:
        lines.append(f"- {idea}")

    return "\n".join(lines)
