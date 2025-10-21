from idea_miner.analyzer import (
    THEME_KEYWORDS,
    aggregate_metrics,
    derive_theme_overview,
    generate_keyword_summary,
    summarize_sentiment,
    suggest_initiatives,
)
from idea_miner.data_loader import Conversation, Message


def _conversation(theme_word: str, score_adjust: float = 0.5) -> Conversation:
    messages = [
        Message(role="user", content=f"We need help with {theme_word} systems", create_time=1700000000.0),
        Message(role="assistant", content="Sure, let's improve workflows!", create_time=1700000300.0),
        Message(role="assistant", content="This is excellent", create_time=1700000400.0),
    ]
    return Conversation(
        conversation_id=f"conv-{theme_word}",
        title=f"About {theme_word}",
        create_time=1700000000.0,
        update_time=1700000500.0,
        messages=messages,
    )


def test_keyword_summary() -> None:
    conversations = [_conversation("toast")]
    summary = generate_keyword_summary(conversations, top_n=5)
    assert summary.tokens
    tokens = {token for token, _ in summary.tokens}
    assert "toast" in tokens


def test_theme_overview_and_initiatives() -> None:
    conversations = [_conversation(next(iter(THEME_KEYWORDS["Restaurant Management & Toast POS"])))]
    themes = derive_theme_overview(conversations)
    assert themes.counts["Restaurant Management & Toast POS"] == 1
    sentiment = summarize_sentiment(conversations)
    ideas = suggest_initiatives(themes, sentiment)
    assert any("Toast" in idea or "POS" in idea for idea in ideas)


def test_aggregate_metrics() -> None:
    conversations = [_conversation("toast")]
    metrics = aggregate_metrics(conversations)
    assert metrics.conversation_count == 1
    assert metrics.message_count == 3
    assert "assistant" in metrics.participants
