from pathlib import Path

from idea_miner.analysis import Analyzer
from idea_miner.loader import Conversation


def build_conversation(title: str, text: str) -> Conversation:
    mapping = {
        "node": {
            "message": {
                "content": {"parts": [text]},
            }
        }
    }
    return Conversation(
        title=title,
        create_time=1700000000.0,
        update_time=1700000500.0,
        mapping=mapping,
        raw={"title": title, "mapping": mapping},
    )


def test_theme_detection_and_sentiment(tmp_path: Path) -> None:
    conversations = [
        build_conversation("Toast operations", "Toast POS menu automation workflow"),
        build_conversation("n8n flows", "Automation workflows using n8n webhooks"),
        build_conversation("Data sync", "Data export pipeline to Google Sheet"),
    ]

    analyzer = Analyzer()
    aggregate = analyzer.aggregate(conversations)

    assert aggregate.total_conversations == 3
    assert aggregate.sentiment_counts["neutral"] == 3
    assert aggregate.theme_counts["Restaurant Operations & Toast POS"] == 1
    assert aggregate.theme_counts["Workflow Automation & n8n"] >= 1
    assert aggregate.theme_counts["Data Integration & Reporting"] == 1
    assert "Toast" in aggregate.theme_examples["Restaurant Operations & Toast POS"][0]


def test_iter_conversations_from_json(tmp_path: Path) -> None:
    data = [
        {
            "title": "Sample",
            "create_time": 1,
            "mapping": {
                "node": {
                    "message": {
                        "content": {"parts": ["Hello world"]},
                    }
                }
            },
        }
    ]
    json_path = tmp_path / "export.json"
    json_path.write_text(__import__("json").dumps(data), encoding="utf-8")

    from idea_miner.loader import iter_conversations

    conversations = list(iter_conversations([json_path]))
    assert len(conversations) == 1
    assert conversations[0].title == "Sample"
