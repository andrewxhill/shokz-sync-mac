from datetime import UTC, datetime
from pathlib import Path

import pytest

from shokz_sync.plan import Item


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Never touch the real config, state, or LaunchAgents."""
    monkeypatch.setenv("SHOKZ_SYNC_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("SHOKZ_SYNC_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("SHOKZ_SYNC_AGENTS_DIR", str(tmp_path / "agents"))


def item(source: str, ident: str, day: int, title: str | None = None) -> Item:
    return Item(
        source,
        ident,
        title or f"{source} {ident}",
        datetime(2026, 9, day, tzinfo=UTC),
        f"https://ex.com/{source}/{ident}",
    )


class FakeAdapter:
    """Serves canned items per URL and writes a tiny fake mp3 on fetch."""

    def __init__(self, items: dict[str, list[Item]], fail_list=(), fail_fetch=()):
        self.items, self.fail_list, self.fail_fetch = items, set(fail_list), set(fail_fetch)
        self.fetched: list[str] = []

    def newest(self, source, url, n):
        if url in self.fail_list:
            raise RuntimeError("feed down")
        return sorted(self.items[url], key=lambda i: i.published, reverse=True)[:n]

    def fetch(self, it: Item, dest: Path):
        if it.key in self.fail_fetch:
            raise RuntimeError("403")
        self.fetched.append(it.key)
        dest.write_bytes(b"ID3" + it.key.encode())
