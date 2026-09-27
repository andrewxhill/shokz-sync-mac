"""Durable state: ~/Library/Application Support/shokz-sync/state.json, plus a run lock."""

from __future__ import annotations

import fcntl
import json
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .plan import Item

WANTED, DROPPED, SKIPPED = "wanted", "dropped", "skipped"


def state_dir() -> Path:
    default = Path.home() / "Library" / "Application Support" / "shokz-sync"
    return Path(os.environ.get("SHOKZ_SYNC_STATE_DIR", default))


class Busy(Exception):
    """Another shokz-sync run holds the lock."""


@contextmanager
def lock(name: str, wait: float = 0, directory: Path | None = None) -> Iterator[None]:
    """Exclusive lock `name`. Raises Busy if not acquired within `wait` seconds."""
    directory = directory or state_dir()
    directory.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + wait
    with open(directory / f"{name}.lock", "w") as fh:
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError as e:
                if time.monotonic() >= deadline:
                    raise Busy(f"another shokz-sync {name} is in progress") from e
                time.sleep(0.5)
        yield


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class State:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or state_dir() / "state.json"
        self.items: dict[str, dict] = {}
        self.sources: dict[str, dict] = {}
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self.items = raw.get("items", {})
            self.sources = raw.get("sources", {})

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({"items": self.items, "sources": self.sources}, indent=2))
        os.replace(tmp, self.path)

    # items

    def put(self, item: Item, status: str, file: str | None, duration: float | None) -> None:
        self.items[item.key] = {
            "source": item.source,
            "id": item.id,
            "title": item.title,
            "published": item.published.isoformat(),
            "url": item.url,
            "file": file,
            "duration": duration,
            "status": status,
        }

    def set_status(self, key: str, status: str) -> None:
        self.items[key]["status"] = status

    def keys(self, status: str) -> set[str]:
        return {k for k, v in self.items.items() if v["status"] == status}

    def as_item(self, key: str) -> Item:
        v = self.items[key]
        published = datetime.fromisoformat(v["published"])
        return Item(v["source"], v["id"], v["title"], published, v["url"])

    def wanted(self, source: str | None = None) -> list[dict]:
        """Wanted records, newest first."""
        rows = [
            v
            for v in self.items.values()
            if v["status"] == WANTED and (source is None or v["source"] == source)
        ]
        return sorted(rows, key=lambda v: v["published"], reverse=True)

    def wanted_items(self, source: str) -> list[Item]:
        return [self.as_item(f"{v['source']}:{v['id']}") for v in self.wanted(source)]

    # sources

    def source_ok(self, name: str) -> None:
        now = _now()
        self.sources[name] = {"last_run": now, "last_ok": now, "last_error": None}

    def source_error(self, name: str, error: str) -> None:
        prev = self.sources.get(name, {})
        self.sources[name] = {
            "last_run": _now(),
            "last_ok": prev.get("last_ok"),
            "last_error": error,
        }
