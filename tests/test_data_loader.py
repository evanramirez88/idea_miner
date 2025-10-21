from pathlib import Path
import json
import zipfile

from idea_miner.data_loader import load_conversation_files


def _sample_conversation() -> dict:
    return {
        "conversation_id": "abc123",
        "title": "Sample",
        "create_time": 1700000000.0,
        "update_time": 1700003600.0,
        "mapping": {
            "1": {
                "id": "1",
                "message": {
                    "author": {"role": "user"},
                    "content": {"parts": ["Hello there"]},
                    "create_time": 1700000000.0,
                },
                "parent": None,
                "children": ["2"],
            },
            "2": {
                "id": "2",
                "message": {
                    "author": {"role": "assistant"},
                    "content": {"parts": ["Hi! Let's plan." ]},
                    "create_time": 1700000300.0,
                },
                "parent": "1",
                "children": [],
            },
        },
    }


def test_load_conversation_files(tmp_path: Path) -> None:
    payload = [_sample_conversation()]
    path = tmp_path / "export.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    conversations = load_conversation_files([path])
    assert len(conversations) == 1
    conv = conversations[0]
    assert conv.conversation_id == "abc123"
    assert conv.title == "Sample"
    assert len(conv.messages) == 2
    assert conv.messages[0].content == "Hello there"
    assert conv.messages[1].role == "assistant"


def test_load_zip_file(tmp_path: Path) -> None:
    payload = [_sample_conversation()]
    json_bytes = json.dumps(payload).encode("utf-8")
    zip_path = tmp_path / "export.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("data.json", json_bytes)

    conversations = load_conversation_files([zip_path])
    assert len(conversations) == 1
    assert conversations[0].title == "Sample"
