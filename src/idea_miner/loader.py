"""Utilities for loading conversation export files."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional
import zipfile


@dataclass
class Conversation:
    """Represents a single conversation export entry."""

    title: str
    create_time: Optional[float]
    update_time: Optional[float]
    mapping: Dict[str, Dict]
    raw: Dict

    @property
    def message_count(self) -> int:
        return sum(
            1 for node in self.mapping.values() if node.get("message") is not None
        )


class UnsupportedFormatError(ValueError):
    """Raised when a provided path is not a supported conversation export."""


def _load_json(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_json_from_zip(zip_path: Path) -> Iterator[Dict]:
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".json"):
                continue
            with archive.open(name) as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    for entry in data:
                        yield entry
                elif isinstance(data, dict):
                    # Some exports may store a single conversation per file.
                    yield data


def iter_conversations(paths: Iterable[Path]) -> Iterator[Conversation]:
    """Yield :class:`Conversation` objects for the given paths."""

    for path in paths:
        resolved = path.resolve()
        if not resolved.exists():
            raise FileNotFoundError(resolved)

        if resolved.is_dir():
            yield from iter_conversations(sorted(resolved.iterdir()))
            continue

        suffix = resolved.suffix.lower()
        if suffix == ".json":
            for raw in _load_json(resolved):
                if not isinstance(raw, dict):
                    continue
                mapping = raw.get("mapping") or {}
                yield Conversation(
                    title=raw.get("title") or "Untitled conversation",
                    create_time=raw.get("create_time"),
                    update_time=raw.get("update_time"),
                    mapping=mapping,
                    raw=raw,
                )
        elif suffix == ".zip":
            for raw in _load_json_from_zip(resolved):
                if not isinstance(raw, dict):
                    continue
                mapping = raw.get("mapping") or {}
                yield Conversation(
                    title=raw.get("title") or "Untitled conversation",
                    create_time=raw.get("create_time"),
                    update_time=raw.get("update_time"),
                    mapping=mapping,
                    raw=raw,
                )
        else:
            raise UnsupportedFormatError(
                f"Unsupported file type: {resolved.suffix}. Expected .json or .zip"
            )
