from pathlib import Path

import pytest
import yt_dlp

from shokz_sync.sources import youtube
from shokz_sync.sources.youtube import YouTube, YouTubeError, feed_url, parse_feed

FEED = (Path(__file__).parent / "fixtures" / "youtube.xml").read_bytes()
BOT = yt_dlp.utils.DownloadError("ERROR: [youtube] x: Sign in to confirm you’re not a bot. See")
CH = "UC4hpU89Ex6O877-24QpWlOw"


def test_feed_url_for_channel_playlist_and_handle():
    assert feed_url(f"https://www.youtube.com/channel/{CH}/videos").endswith(f"channel_id={CH}")
    assert feed_url("https://www.youtube.com/playlist?list=PLabc").endswith("playlist_id=PLabc")
    page = f'<link rel="canonical" href="https://www.youtube.com/channel/{CH}">'
    assert feed_url("https://www.youtube.com/@nk", get_page=lambda u: page).endswith(CH)
    with pytest.raises(YouTubeError):
        feed_url("https://www.youtube.com/@nk", get_page=lambda u: "<html>")


def test_parse_feed_newest_first_and_skips_shorts():
    items = parse_feed("NK", FEED, 5)
    assert [i.id for i in items] == ["FZ_Ce-9eUOo", "xKPT3J2oUx8"]
    assert items[0].url == "https://www.youtube.com/watch?v=FZ_Ce-9eUOo"
    assert items[0].published.isoformat() == "2026-09-12T00:29:28+00:00"


class FakeYDL:
    """Stands in for yt_dlp.YoutubeDL: bot-checks unless cookies are passed."""

    calls: list[dict] = []
    block_even_with_cookies = False

    def __init__(self, opts):
        self.opts = opts
        FakeYDL.calls.append(opts)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def download(self, urls):
        if "cookiesfrombrowser" not in self.opts or FakeYDL.block_even_with_cookies:
            raise BOT
        Path(self.opts["outtmpl"].replace("%(ext)s", "mp3")).write_bytes(b"ID3")


@pytest.fixture
def fake(monkeypatch):
    FakeYDL.calls = []
    FakeYDL.block_even_with_cookies = False
    monkeypatch.setattr(youtube.yt_dlp, "YoutubeDL", FakeYDL)


ITEM = parse_feed("NK", FEED, 1)[0]


def test_bot_check_retries_download_with_browser_cookies(fake, tmp_path):
    yt = YouTube("chrome")
    yt.fetch(ITEM, tmp_path / "a.mp3")
    assert (tmp_path / "a.mp3").read_bytes() == b"ID3"
    assert "cookiesfrombrowser" not in FakeYDL.calls[0]
    assert FakeYDL.calls[-1]["cookiesfrombrowser"] == ("chrome", None, None, None)
    FakeYDL.calls = []
    yt.fetch(ITEM, tmp_path / "b.mp3")  # cookies stick for the rest of the run
    assert len(FakeYDL.calls) == 1 and "cookiesfrombrowser" in FakeYDL.calls[0]


def test_no_cookie_fallback_when_disabled(fake, tmp_path):
    with pytest.raises(YouTubeError, match="bot check"):
        YouTube("").fetch(ITEM, tmp_path / "a.mp3")
    assert all("cookiesfrombrowser" not in c for c in FakeYDL.calls)


def test_still_blocked_with_cookies_reports_error(fake, tmp_path):
    FakeYDL.block_even_with_cookies = True
    with pytest.raises(YouTubeError, match="bot check"):
        YouTube("chrome").fetch(ITEM, tmp_path / "a.mp3")
    assert not (tmp_path / "a.mp3").exists()
