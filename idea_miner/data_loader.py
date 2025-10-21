"""Utilities for loading ChatGPT conversation exports."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional
import zipfile


@dataclass
class Message:
    """Represents a single message in a conversation."""

    role: str
    content: str
    create_time: Optional[float] = None


@dataclass
class Conversation:
    """Represents a ChatGPT conversation export."""

    conversation_id: str
    title: str
    create_time: Optional[float]
    update_time: Optional[float]
    messages: List[Message]


def _iter_conversation_records(path: Path) -> Iterator[Dict]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if isinstance(data, dict):
        # Some exports wrap the conversations in a dictionary
        if "conversations" in data and isinstance(data["conversations"], list):
            yield from data["conversations"]
        else:
            raise ValueError(f"Unrecognized JSON structure in {path}")
    elif isinstance(data, list):
        yield from data
    else:
        raise ValueError(f"Unsupported JSON structure in {path}")


def _extract_messages(mapping: Dict[str, Dict]) -> List[Message]:
    messages: List[Message] = []
    for node in mapping.values():
        message = node.get("message")
        if not message:
            continue
        author = message.get("author", {})
        role = author.get("role", "unknown")
        content = message.get("content")
        if not content:
            continue
        parts = content.get("parts")
        if not parts:
            continue
        text = "\n\n".join(str(part) for part in parts if part)
        if not text.strip():
            continue
        messages.append(
            Message(
                role=role,
                content=text.strip(),
                create_time=message.get("create_time"),
            )
        )
    # Sort messages by timestamp when available to ensure deterministic order
    messages.sort(key=lambda msg: (msg.create_time or 0.0))
    return messages


def _load_conversation(record: Dict) -> Conversation:
    mapping = record.get("mapping") or {}
    messages = _extract_messages(mapping)
    return Conversation(
        conversation_id=record.get("conversation_id") or record.get("id", ""),
        title=record.get("title", "Untitled Conversation"),
        create_time=record.get("create_time"),
        update_time=record.get("update_time"),
        messages=messages,
    )


def load_conversation_files(paths: Iterable[Path]) -> List[Conversation]:
    """Load conversations from a sequence of JSON or ZIP files."""

    conversations: List[Conversation] = []
    for path in paths:
        if path.suffix.lower() == ".zip":
            conversations.extend(_load_zip(path))
        elif path.suffix.lower() == ".json":
            for record in _iter_conversation_records(path):
                conversations.append(_load_conversation(record))
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    return conversations


def _load_zip(path: Path) -> List[Conversation]:
    conversations: List[Conversation] = []
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".json"):
                continue
            with zf.open(name) as fp:
                text = fp.read().decode("utf-8")
            data = json.loads(text)
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict) and "conversations" in data:
                records = data["conversations"]
            else:
                continue
            for record in records:
                conversations.append(_load_conversation(record))
    return conversations


__all__ = ["Conversation", "Message", "load_conversation_files"]
