"""Source adapters. Each exposes newest(source, url, n) and fetch(item, dest)."""

from __future__ import annotations

from typing import Protocol

from ..plan import Item


class Adapter(Protocol):
    def newest(self, source: str, url: str, n: int) -> list[Item]: ...
    def fetch(self, item: Item, dest) -> None: ...


def adapters(youtube_cookies_from: str | None = None) -> dict[str, Adapter]:
    from . import rss
    from .youtube import YouTube

    return {"rss": rss, "youtube": YouTube(youtube_cookies_from)}  # type: ignore[dict-item]
