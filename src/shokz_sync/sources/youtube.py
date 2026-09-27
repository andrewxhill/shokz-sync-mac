"""YouTube channels and playlists: found via YouTube's RSS feed, downloaded with yt-dlp."""

from __future__ import annotations

import calendar
import re
import shutil
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import feedparser
import yt_dlp

from ..plan import Item
from .rss import USER_AGENT

# YouTube serves ~20 auto-dubbed tracks per video; always take the original.
AUDIO_FORMAT = "ba[format_note*=original]/ba"


class _Silent:
    """yt-dlp prints errors to stderr even when quiet; we report them ourselves."""

    def debug(self, msg: str) -> None: ...
    def info(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...


_QUIET = {"quiet": True, "no_warnings": True, "noprogress": True, "logger": _Silent()}


class YouTubeError(Exception):
    pass


def _is_bot_check(err: Exception) -> bool:
    return "not a bot" in str(err)


def _short(err: Exception) -> str:
    """First sentence of a yt-dlp error, without its FAQ links."""
    msg = str(err).removeprefix("ERROR: ").strip().splitlines()[0]
    if "not a bot" in msg:
        return "YouTube wants a sign-in (bot check); set youtube_cookies_from"
    return msg.split(". ")[0].rstrip(".")


FEED = "https://www.youtube.com/feeds/videos.xml?{}={}"
_CANONICAL = re.compile(
    r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[\w-]{22})"'
)
_EXTERNAL_ID = re.compile(r'"externalId":"(UC[\w-]{22})"')


def feed_url(url: str, get_page=None) -> str:
    """YouTube's own RSS feed for a channel or playlist URL.

    Reading the feed is a plain HTTP request that YouTube's bot check does not gate, so new
    episodes are found without yt-dlp. @handles are resolved from the channel page.
    """
    if "feeds/videos.xml" in url:
        return url
    q = parse_qs(urlparse(url).query)
    if "list" in q:
        return FEED.format("playlist_id", q["list"][0])
    m = re.search(r"/channel/(UC[\w-]{22})", url)
    if m:
        return FEED.format("channel_id", m.group(1))
    page = (get_page or _get)(url)
    m = _CANONICAL.search(page) or _EXTERNAL_ID.search(page)
    if not m:
        raise YouTubeError(f"could not find a channel id for {url}")
    return FEED.format("channel_id", m.group(1))


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_feed(source: str, data: bytes | str, n: int) -> list[Item]:
    feed = feedparser.parse(data)
    items: list[Item] = []
    for e in feed.entries:
        vid, stamp = e.get("yt_videoid"), e.get("published_parsed")
        if not vid or stamp is None or "/shorts/" in e.get("link", ""):
            continue
        published = datetime.fromtimestamp(calendar.timegm(stamp), UTC)
        url = f"https://www.youtube.com/watch?v={vid}"
        items.append(Item(source, vid, e.get("title") or vid, published, url))
    items.sort(key=lambda i: i.published, reverse=True)
    return items[:n]


class YouTube:
    """Finds videos through YouTube's RSS feed and downloads them with yt-dlp.

    A download first runs without a login. On YouTube's bot check it retries once with the
    browser's YouTube cookies (yt-dlp's cookiesfrombrowser) and keeps using them this run.
    """

    def __init__(self, cookies_from: str | None = None) -> None:
        self.cookies_from = cookies_from or None
        self._with_cookies = False

    def _opts(self, **extra) -> dict:
        opts = {**_QUIET, **extra}
        if self._with_cookies:
            opts["cookiesfrombrowser"] = (self.cookies_from, None, None, None)
        return opts

    def _run(self, work):
        try:
            return work()
        except yt_dlp.utils.DownloadError as err:
            if _is_bot_check(err) and self.cookies_from and not self._with_cookies:
                self._with_cookies = True
                try:
                    return work()
                except yt_dlp.utils.DownloadError as err2:
                    raise YouTubeError(_short(err2)) from err2
            raise YouTubeError(_short(err)) from err

    def newest(self, source: str, url: str, n: int) -> list[Item]:
        try:
            items = parse_feed(source, _get(feed_url(url)), n)
        except YouTubeError:
            raise
        except Exception as e:
            raise YouTubeError(f"feed unavailable: {e}") from e
        if not items:
            raise YouTubeError("no videos found")
        return items

    def fetch(self, item: Item, dest: Path) -> None:
        """Download the original-language audio track as mp3 to dest."""
        with tempfile.TemporaryDirectory(dir=dest.parent, prefix=".yt-") as tmp:
            opts = {
                "format": AUDIO_FORMAT,
                "outtmpl": str(Path(tmp) / "audio.%(ext)s"),
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "5"}
                ],
            }

            def work() -> None:
                with yt_dlp.YoutubeDL(self._opts(**opts)) as ydl:
                    ydl.download([item.url])

            self._run(work)
            out = Path(tmp) / "audio.mp3"
            if not out.exists():
                raise YouTubeError("yt-dlp produced no mp3 (is ffmpeg installed?)")
            shutil.move(out, dest)
