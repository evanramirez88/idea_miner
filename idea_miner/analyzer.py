"""Core analysis routines for the Idea Miner project."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re
from typing import Dict, Iterable, List, Mapping, Tuple

from .data_loader import Conversation, Message

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_']+")
_STOPWORDS = {
    "the",
    "to",
    "of",
    "in",
    "on",
    "or",
    "is",
    "are",
    "be",
    "was",
    "were",
    "if",
    "but",
    "so",
    "do",
    "does",
    "did",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "have",
    "will",
    "your",
    "about",
    "into",
    "they",
    "them",
    "when",
    "what",
    "where",
    "why",
    "how",
    "an",
    "a",
    "i",
    "me",
    "my",
    "you",
    "it",
    "its",
    "we",
    "us",
    "he",
    "she",
    "they",
    "them",
    "also",
    "there",
    "their",
    "would",
    "could",
    "should",
    "been",
    "being",
    "very",
    "just",
    "like",
    "need",
    "more",
    "some",
    "such",
    "than",
    "then",
    "even",
    "into",
    "onto",
    "because",
    "while",
    "make",
    "made",
    "much",
    "many",
    "using",
    "used",
    "use",
    "can",
    "any",
    "each",
    "other",
    "over",
    "really",
    "we",
    "our",
    "ours",
    "per",
    "via",
    "etc",
    "may",
    "every",
    "as",
    "user",
    "assistant",
    "file",
    "files",
    "analysis",
    "analyze",
    "project",
    "projects",
    "let",
    "lets",
    "these",
    "those",
    "by",
    "api",
    "py",
}

THEME_KEYWORDS: Mapping[str, Tuple[str, ...]] = {
    "Restaurant Management & Toast POS": (
        "toast",
        "restaurant",
        "pos",
        "menu",
        "order",
        "service",
        "inventory",
        "kitchen",
    ),
    "Workflow Automation & n8n": (
        "n8n",
        "automation",
        "workflow",
        "webhook",
        "trigger",
    ),
    "Cape Cod Cable Contractors": (
        "cable",
        "contractor",
        "fiber",
        "network",
        "installation",
    ),
    "Business Consulting & Strategy": (
        "consulting",
        "strategy",
        "ccrc",
        "client",
        "proposal",
    ),
    "Web & App Development": (
        "react",
        "frontend",
        "website",
        "app",
        "component",
        "ui",
    ),
    "Data Integration & Reporting": (
        "sheet",
        "spreadsheet",
        "dashboard",
        "export",
        "report",
        "analytics",
        "data",
    ),
}

_SENTIMENT_POSITIVE = {
    "great",
    "good",
    "excellent",
    "positive",
    "success",
    "improve",
    "improved",
    "amazing",
    "awesome",
    "love",
    "like",
    "win",
    "growth",
    "happy",
    "excited",
    "optimistic",
    "helpful",
    "efficient",
    "productive",
}

_SENTIMENT_NEGATIVE = {
    "bad",
    "poor",
    "negative",
    "issue",
    "problem",
    "slow",
    "bug",
    "difficult",
    "hard",
    "concern",
    "confused",
    "frustrated",
    "angry",
    "fail",
    "failure",
    "broken",
    "delay",
    "risk",
    "blocked",
}


@dataclass
class KeywordSummary:
    tokens: List[Tuple[str, int]]
    bigrams: List[Tuple[str, int]]


@dataclass
class SentimentBreakdown:
    positive: int
    neutral: int
    negative: int
    average_compound: float


@dataclass
class ThemeOverview:
    counts: Dict[str, int]
    top_keywords: Dict[str, List[str]]


@dataclass
class TimelinePoint:
    label: str
    conversations: int


@dataclass
class AggregateMetrics:
    conversation_count: int
    message_count: int
    participants: List[str]
    first_interaction: str | None
    last_interaction: str | None



def _normalize_token(token: str) -> str:
    token = token.lower().strip("'_#")
    return token


def _tokenize(messages: Iterable[Message]) -> List[str]:
    tokens: List[str] = []
    for message in messages:
        for match in _WORD_RE.finditer(message.content):
            token = _normalize_token(match.group())
            if token and token not in _STOPWORDS:
                tokens.append(token)
    return tokens


def aggregate_metrics(conversations: List[Conversation]) -> AggregateMetrics:
    message_count = sum(len(conv.messages) for conv in conversations)
    participants = sorted(
        {msg.role for conv in conversations for msg in conv.messages if msg.role}
    )
    timestamps = [msg.create_time for conv in conversations for msg in conv.messages if msg.create_time]
    def _format_ts(ts: float | None) -> str | None:
        if ts is None:
            return None
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")

    first = _format_ts(min(timestamps)) if timestamps else None
    last = _format_ts(max(timestamps)) if timestamps else None
    return AggregateMetrics(
        conversation_count=len(conversations),
        message_count=message_count,
        participants=participants,
        first_interaction=first,
        last_interaction=last,
    )


def generate_keyword_summary(conversations: List[Conversation], top_n: int = 20) -> KeywordSummary:
    tokens = _tokenize(msg for conv in conversations for msg in conv.messages)
    token_counts = Counter(tokens)

    bigram_counts: Counter[str] = Counter()
    for conv in conversations:
        for msg in conv.messages:
            words = [tok for tok in _tokenize([msg])]
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                if words[i] == words[i + 1]:
                    continue
                bigram_counts[bigram] += 1

    top_tokens = token_counts.most_common(top_n)
    top_bigrams = bigram_counts.most_common(min(top_n // 2 or 1, len(bigram_counts)))
    return KeywordSummary(tokens=top_tokens, bigrams=top_bigrams)


def summarize_sentiment(conversations: List[Conversation]) -> SentimentBreakdown:
    positive = neutral = negative = 0
    scores: List[float] = []
    for conv in conversations:
        for msg in conv.messages:
            score = _sentiment_score(msg.content)
            scores.append(score)
            if score >= 0.2:
                positive += 1
            elif score <= -0.2:
                negative += 1
            else:
                neutral += 1
    average = float(sum(scores) / len(scores)) if scores else 0.0
    return SentimentBreakdown(
        positive=positive,
        neutral=neutral,
        negative=negative,
        average_compound=average,
    )


def _sentiment_score(text: str) -> float:
    tokens = [
        _normalize_token(match.group())
        for match in _WORD_RE.finditer(text)
    ]
    if not tokens:
        return 0.0
    score = 0
    for token in tokens:
        if token in _SENTIMENT_POSITIVE:
            score += 1
        elif token in _SENTIMENT_NEGATIVE:
            score -= 1
    magnitude = math.sqrt(len(tokens))
    if magnitude == 0:
        return 0.0
    normalized = score / magnitude
    return max(-1.0, min(1.0, normalized))


def derive_theme_overview(conversations: List[Conversation]) -> ThemeOverview:
    counts: Dict[str, int] = {theme: 0 for theme in THEME_KEYWORDS}
    counts["Other"] = 0
    keyword_accumulator: Dict[str, Counter[str]] = {theme: Counter() for theme in counts}

    for conv in conversations:
        conv_tokens = _tokenize(conv.messages)
        theme_hit = False
        for theme, keywords in THEME_KEYWORDS.items():
            matches = [tok for tok in conv_tokens if tok in keywords]
            if matches:
                counts[theme] += 1
                keyword_accumulator[theme].update(matches)
                theme_hit = True
        if not theme_hit:
            counts["Other"] += 1
            keyword_accumulator["Other"].update(conv_tokens)

    top_keywords = {
        theme: [token for token, _ in counter.most_common(5)]
        for theme, counter in keyword_accumulator.items()
        if counter
    }
    return ThemeOverview(counts=counts, top_keywords=top_keywords)


def build_timeline(conversations: List[Conversation]) -> List[TimelinePoint]:
    bucket: Dict[str, int] = defaultdict(int)
    for conv in conversations:
        if conv.create_time:
            dt = datetime.fromtimestamp(conv.create_time, tz=timezone.utc)
        elif conv.messages and conv.messages[0].create_time:
            dt = datetime.fromtimestamp(conv.messages[0].create_time, tz=timezone.utc)
        else:
            continue
        label = dt.strftime("%Y-%m")
        bucket[label] += 1
    timeline = [TimelinePoint(label=label, conversations=count) for label, count in sorted(bucket.items())]
    return timeline


def suggest_initiatives(themes: ThemeOverview, sentiment: SentimentBreakdown) -> List[str]:
    suggestions: List[str] = []
    for theme, count in themes.counts.items():
        if theme == "Other" or count == 0:
            continue
        if theme == "Restaurant Management & Toast POS":
            suggestions.append(
                "Develop a modular Toast POS integration toolkit with menu syncing, analytics, and deployment playbooks."
            )
        elif theme == "Workflow Automation & n8n":
            suggestions.append(
                "Package reusable n8n workflow templates for lead capture, CRM sync, and operations automation."
            )
        elif theme == "Cape Cod Cable Contractors":
            suggestions.append(
                "Create a field operations dashboard for cable installations with scheduling and hardware inventory tracking."
            )
        elif theme == "Business Consulting & Strategy":
            suggestions.append(
                "Build a consulting discovery workspace to consolidate proposals, research, and financial models."
            )
        elif theme == "Web & App Development":
            suggestions.append(
                "Launch a design system starter kit for React/Next.js tailored to Cape Cod businesses."
            )
        elif theme == "Data Integration & Reporting":
            suggestions.append(
                "Offer a data pipeline accelerator combining Google Sheets, databases, and BI dashboards."
            )
    if sentiment.average_compound < 0:
        suggestions.append(
            "Prioritize customer feedback loops—sentiment skews negative, so dedicate sprints to support and quality fixes."
        )
    elif sentiment.average_compound < 0.15:
        suggestions.append(
            "Sentiment is mixed; introduce regular check-ins and success stories to reinforce positive outcomes."
        )
    else:
        suggestions.append(
            "Sentiment trends positive—consider launching premium services or bundled offerings while momentum is high."
        )
    return suggestions


__all__ = [
    "KeywordSummary",
    "SentimentBreakdown",
    "ThemeOverview",
    "TimelinePoint",
    "AggregateMetrics",
    "aggregate_metrics",
    "generate_keyword_summary",
    "summarize_sentiment",
    "derive_theme_overview",
    "build_timeline",
    "suggest_initiatives",
]
