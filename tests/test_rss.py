from pathlib import Path

from shokz_sync.sources.rss import _is_mp3, parse

FEED = (Path(__file__).parent / "fixtures" / "feed.xml").read_bytes()


def test_parse_orders_newest_first_and_ignores_video():
    items = parse("Pod", FEED, 5)
    assert [i.title for i in items] == ["Newest episode", "No guid", "Old episode"]
    assert items[0].id == "g-new"
    assert items[0].url == "https://ex.com/new.mp3"
    assert items[0].published.isoformat() == "2026-09-17T15:38:13+00:00"


def test_parse_falls_back_to_enclosure_url_for_id():
    no_guid = next(i for i in parse("Pod", FEED, 5) if i.title == "No guid")
    assert no_guid.id == "https://ex.com/noguid.mp3"


def test_parse_limits_n():
    assert len(parse("Pod", FEED, 1)) == 1


def test_mp3_sniffing(tmp_path):
    (tmp_path / "a").write_bytes(b"ID3\x04rest")
    (tmp_path / "b").write_bytes(b"\xff\xfb\x90\x00")
    (tmp_path / "c").write_bytes(b"<html>")
    assert _is_mp3(tmp_path / "a") and _is_mp3(tmp_path / "b")
    assert not _is_mp3(tmp_path / "c")


def test_youtube_errors_are_short():
    from shokz_sync.sources.youtube import _short

    bot = Exception(
        "ERROR: [youtube] x: Sign in to confirm you’re not a bot. Use --cookies. See url"
    )
    assert _short(bot) == "YouTube wants a sign-in (bot check); set youtube_cookies_from"
    assert _short(Exception("ERROR: [youtube] x: Video unavailable. See url")) == (
        "[youtube] x: Video unavailable"
    )
