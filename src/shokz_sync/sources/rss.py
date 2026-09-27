"""Podcast RSS feeds via feedparser."""

from __future__ import annotations

import calendar
import shutil
import subprocess
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import feedparser

from ..plan import Item

USER_AGENT = "Mozilla/5.0 (Macintosh) shokz-sync"


class FeedError(Exception):
    pass


def parse(source: str, data: bytes | str, n: int) -> list[Item]:
    feed = feedparser.parse(data)
    if feed.bozo and not feed.entries:
        raise FeedError(f"could not parse feed: {feed.bozo_exception}")
    items: list[Item] = []
    for e in feed.entries:
        audio = next(
            (x for x in e.get("enclosures", []) if x.get("type", "").startswith("audio")), None
        )
        stamp = e.get("published_parsed") or e.get("updated_parsed")
        if audio is None or not audio.get("href") or stamp is None:
            continue
        published = datetime.fromtimestamp(calendar.timegm(stamp), UTC)
        ident = e.get("id") or audio["href"]
        items.append(Item(source, ident, e.get("title", "untitled"), published, audio["href"]))
    items.sort(key=lambda i: i.published, reverse=True)
    return items[:n]


def newest(source: str, url: str, n: int) -> list[Item]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    items = parse(source, data, n)
    if not items:
        raise FeedError("feed has no audio episodes")
    return items


def _is_mp3(path: Path) -> bool:
    with open(path, "rb") as fh:
        head = fh.read(3)
    return head == b"ID3" or (len(head) >= 2 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0)


def fetch(item: Item, dest: Path) -> None:
    """Download the enclosure to dest (an .mp3 path), converting non-mp3 audio with ffmpeg."""
    part = dest.with_name(dest.name + ".part")
    req = urllib.request.Request(item.url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(part, "wb") as out:
            shutil.copyfileobj(resp, out, length=1 << 20)
        if _is_mp3(part):
            part.replace(dest)
            return
        conv = dest.with_name(dest.name + ".conv.mp3")
        proc = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(part),
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "5",
                str(conv),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            conv.unlink(missing_ok=True)
            raise FeedError(f"not playable audio: {proc.stderr.strip()[:200]}")
        conv.replace(dest)
    finally:
        part.unlink(missing_ok=True)
