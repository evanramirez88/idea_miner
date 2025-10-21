"""Core analytics for synthesizing conversation exports."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .loader import Conversation

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")
STOP_WORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "your",
    "about",
    "will",
    "there",
    "their",
    "into",
    "would",
    "could",
    "should",
    "while",
    "which",
    "when",
    "where",
    "what",
    "been",
    "they",
    "them",
    "you",
    "are",
    "was",
    "were",
    "its",
    "it's",
    "but",
    "can",
    "our",
    "out",
    "all",
    "any",
    "how",
    "why",
    "who",
    "get",
    "just",
    "like",
    "more",
    "also",
    "than",
    "some",
    "into",
    "over",
    "such",
    "per",
    "via",
    "each",
    "able",
    "make",
    "need",
    "use",
    "used",
    "using",
    "based",
    "even",
    "most",
    "many",
    "much",
    "very",
    "every",
    "across",
    "next",
    "then",
    "been",
}


@dataclass
class Theme:
    name: str
    keywords: Sequence[str]
    opportunity: str


THEMES: Sequence[Theme] = (
    Theme(
        name="Restaurant Operations & Toast POS",
        keywords=("toast", "restaurant", "pos", "menu", "kiosk", "order"),
        opportunity=(
            "Develop tooling that automates menu updates, pricing experiments, "
            "and integration testing for Toast POS deployments."
        ),
    ),
    Theme(
        name="Workflow Automation & n8n",
        keywords=("automation", "n8n", "workflow", "trigger", "zapier", "webhook"),
        opportunity=(
            "Build reusable workflow templates and monitoring dashboards that "
            "highlight automation health and ROI."
        ),
    ),
    Theme(
        name="Cape Cod Cable & Field Services",
        keywords=("cable", "contractor", "installation", "network", "field", "truck"),
        opportunity=(
            "Create a scheduling and inventory optimization assistant for field "
            "service crews operating across Cape Cod."
        ),
    ),
    Theme(
        name="Data Integration & Reporting",
        keywords=("data", "pipeline", "sheet", "export", "sync", "report"),
        opportunity=(
            "Offer a data observability layer that tracks freshness, schema "
            "changes, and business KPIs across exports."
        ),
    ),
    Theme(
        name="Web & Application Development",
        keywords=("react", "frontend", "component", "website", "tailwind", "typescript"),
        opportunity=(
            "Launch a component library plus scaffolding CLI for rapid "
            "application prototypes used in consulting engagements."
        ),
    ),
)


@dataclass
class ConversationAnalysis:
    conversation: Conversation
    text: str
    tokens: List[str]
    sentiment_scores: List[float]

    @property
    def average_sentiment(self) -> float:
        return mean(self.sentiment_scores) if self.sentiment_scores else 0.0


@dataclass
class AggregateAnalysis:
    total_conversations: int
    total_messages: int
    total_words: int
    top_keywords: List[Tuple[str, int]]
    sentiment_counts: Dict[str, int]
    sentiment_average: float
    theme_counts: Dict[str, int]
    theme_examples: Dict[str, List[str]]
    time_span: Optional[Tuple[str, str]]
    ideas: Dict[str, str]


class SimpleSentimentAnalyzer:
    """Lightweight lexicon-based sentiment scoring."""

    POSITIVE = {
        "improve",
        "great",
        "good",
        "excellent",
        "success",
        "win",
        "help",
        "happy",
        "support",
        "optimize",
        "love",
        "efficient",
        "faster",
        "benefit",
        "insight",
    }

    NEGATIVE = {
        "issue",
        "problem",
        "bug",
        "slow",
        "difficult",
        "error",
        "risk",
        "fail",
        "conflict",
        "delay",
        "broken",
        "complex",
        "concern",
        "challenge",
    }

    def score(self, tokens: Sequence[str]) -> float:
        if not tokens:
            return 0.0
        positive = sum(1 for token in tokens if token in self.POSITIVE)
        negative = sum(1 for token in tokens if token in self.NEGATIVE)
        if positive == 0 and negative == 0:
            return 0.0
        return (positive - negative) / (positive + negative)


class Analyzer:
    """Perform aggregate analytics over conversations."""

    def __init__(self) -> None:
        self._sentiment = SimpleSentimentAnalyzer()

    def _extract_text(self, conversation: Conversation) -> List[str]:
        messages = []
        for node in conversation.mapping.values():
            message = node.get("message") if isinstance(node, dict) else None
            if not message:
                continue
            content = message.get("content") if isinstance(message, dict) else None
            if not content:
                continue
            parts = content.get("parts") if isinstance(content, dict) else None
            if not isinstance(parts, list):
                continue
            for part in parts:
                if isinstance(part, str) and part.strip():
                    messages.append(part.strip())
        return messages

    def _tokenize(self, text: str) -> List[str]:
        tokens = [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]
        return [token for token in tokens if len(token) > 2 and token not in STOP_WORDS]

    def analyze_conversation(self, conversation: Conversation) -> ConversationAnalysis:
        messages = self._extract_text(conversation)
        joined = "\n".join(messages)
        tokens = self._tokenize(joined)
        sentiment_scores = [
            self._sentiment.score(self._tokenize(message)) for message in messages
        ]
        return ConversationAnalysis(
            conversation=conversation,
            text=joined,
            tokens=tokens,
            sentiment_scores=sentiment_scores,
        )

    def aggregate(self, conversations: Iterable[Conversation]) -> AggregateAnalysis:
        analyses: List[ConversationAnalysis] = []
        total_messages = 0
        keyword_counter: Counter[str] = Counter()
        theme_counts: Dict[str, int] = defaultdict(int)
        theme_examples: Dict[str, List[str]] = defaultdict(list)
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        sentiment_average_values: List[float] = []
        create_times: List[float] = []

        for conversation in conversations:
            convo_analysis = self.analyze_conversation(conversation)
            analyses.append(convo_analysis)
            total_messages += conversation.message_count
            keyword_counter.update(convo_analysis.tokens)
            sentiment_average_values.extend(convo_analysis.sentiment_scores)
            create_time = conversation.create_time
            if isinstance(create_time, (int, float)):
                create_times.append(float(create_time))

            sentiment_label = self._classify_sentiment(convo_analysis.average_sentiment)
            sentiment_counts[sentiment_label] += 1

            token_set = set(convo_analysis.tokens)
            for theme in THEMES:
                if any(keyword in token_set for keyword in theme.keywords):
                    theme_counts[theme.name] += 1
                    if len(theme_examples[theme.name]) < 5:
                        theme_examples[theme.name].append(conversation.title)

        total_conversations = len(analyses)
        total_words = sum(len(analysis.tokens) for analysis in analyses)
        sentiment_average = (
            mean(sentiment_average_values) if sentiment_average_values else 0.0
        )
        time_span = self._format_time_span(create_times) if create_times else None

        ideas = {theme.name: theme.opportunity for theme in THEMES if theme.name in theme_counts}

        return AggregateAnalysis(
            total_conversations=total_conversations,
            total_messages=total_messages,
            total_words=total_words,
            top_keywords=keyword_counter.most_common(25),
            sentiment_counts=dict(sentiment_counts),
            sentiment_average=sentiment_average,
            theme_counts=dict(theme_counts),
            theme_examples=dict(theme_examples),
            time_span=time_span,
            ideas=ideas,
        )

    def _classify_sentiment(self, score: float) -> str:
        if score >= 0.05:
            return "positive"
        if score <= -0.05:
            return "negative"
        return "neutral"

    def _format_time_span(self, create_times: Sequence[float]) -> Tuple[str, str]:
        start = datetime.fromtimestamp(min(create_times), tz=timezone.utc)
        end = datetime.fromtimestamp(max(create_times), tz=timezone.utc)
        return start.isoformat(), end.isoformat()


def summarize_for_markdown(analysis: AggregateAnalysis) -> str:
    """Create a Markdown summary of the aggregate analysis."""

    lines: List[str] = []
    lines.append("# Idea Miner Report")
    lines.append("")
    lines.append("## Overview")
    lines.append(
        f"* **Conversations:** {analysis.total_conversations}\n"
        f"* **Messages:** {analysis.total_messages}\n"
        f"* **Analyzed Words:** {analysis.total_words}\n"
        f"* **Average Sentiment:** {analysis.sentiment_average:.3f}"
    )
    if analysis.time_span:
        lines.append(
            f"* **Time Span:** {analysis.time_span[0]} to {analysis.time_span[1]}"
        )

    lines.append("")
    lines.append("## Sentiment Distribution")
    total = sum(analysis.sentiment_counts.values()) or 1
    for label in ("positive", "neutral", "negative"):
        count = analysis.sentiment_counts.get(label, 0)
        percentage = (count / total) * 100
        lines.append(f"* **{label.title()}**: {count} ({percentage:.1f}%)")

    lines.append("")
    lines.append("## Recurring Themes")
    if analysis.theme_counts:
        lines.append("| Theme | Conversations | Example Titles | Opportunity |")
        lines.append("| --- | ---: | --- | --- |")
        for theme in THEMES:
            if theme.name not in analysis.theme_counts:
                continue
            examples = "; ".join(analysis.theme_examples.get(theme.name, [])) or "—"
            idea = analysis.ideas.get(theme.name, "—")
            lines.append(
                f"| {theme.name} | {analysis.theme_counts[theme.name]} | {examples} | {idea} |"
            )
    else:
        lines.append("No recurring themes detected with the current keyword mapping.")

    lines.append("")
    lines.append("## Top Keywords")
    if analysis.top_keywords:
        lines.append(
            ", ".join(
                f"{keyword} ({count})" for keyword, count in analysis.top_keywords[:20]
            )
        )
    else:
        lines.append("No keywords extracted.")

    lines.append("")
    lines.append("## Strategic Ideas")
    if analysis.ideas:
        for theme_name, idea in analysis.ideas.items():
            lines.append(f"* **{theme_name}:** {idea}")
    else:
        lines.append("Themes were not detected strongly enough to suggest ideas.")

    return "\n".join(lines)
