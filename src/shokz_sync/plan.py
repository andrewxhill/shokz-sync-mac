"""Which items belong on the device. Pure: no I/O."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Item:
    source: str
    id: str
    title: str
    published: datetime  # timezone-aware
    url: str  # enclosure URL (rss) or video URL (youtube)

    @property
    def key(self) -> str:
        return f"{self.source}:{self.id}"


def choose(
    candidates: dict[str, list[Item]], skipped: set[str], per_source: int, total: int
) -> list[Item]:
    """Newest `per_source` items from each source, then the newest `total` overall.

    Skipped items never count, so the next-newest item from that source takes the slot.
    The result is ordered newest first, which is also the copy order.
    """
    picked: list[Item] = []
    for items in candidates.values():
        fresh = [i for i in items if i.key not in skipped]
        fresh.sort(key=lambda i: i.published, reverse=True)
        picked.extend(fresh[:per_source])
    picked.sort(key=lambda i: i.published, reverse=True)
    return picked[:total]
