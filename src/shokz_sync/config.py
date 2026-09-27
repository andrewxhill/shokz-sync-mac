"""User configuration: ~/.config/shokz-sync/config.toml."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import tomli_w

KINDS = ("rss", "youtube")


def config_dir() -> Path:
    return Path(os.environ.get("SHOKZ_SYNC_CONFIG_DIR", Path.home() / ".config" / "shokz-sync"))


def config_path() -> Path:
    return config_dir() / "config.toml"


@dataclass
class Source:
    name: str
    url: str
    kind: str
    enabled: bool = True


@dataclass
class Config:
    per_source: int = 1
    total: int = 5
    download_every_hours: int = 24
    youtube_cookies_from: str = "chrome"  # browser for the bot-check fallback; "" = never
    device: str = "SWIM PRO"
    library: Path = field(default_factory=lambda: Path.home() / "Music" / "ShokzSync")
    sources: list[Source] = field(default_factory=list)

    @property
    def enabled_sources(self) -> list[Source]:
        return [s for s in self.sources if s.enabled]

    def find(self, name: str) -> Source | None:
        return next((s for s in self.sources if s.name.lower() == name.lower()), None)


def infer_kind(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host == "youtu.be" or host == "youtube.com" or host.endswith(".youtube.com"):
        return "youtube"
    return "rss"


def load(path: Path | None = None) -> Config:
    path = path or config_path()
    if not path.exists():
        return Config()
    raw = tomllib.loads(path.read_text())
    cfg = Config(
        per_source=int(raw.get("per_source", 1)),
        total=int(raw.get("total", 5)),
        download_every_hours=int(raw.get("download_every_hours", 24)),
        youtube_cookies_from=str(raw.get("youtube_cookies_from", "chrome")),
        device=str(raw.get("device", "SWIM PRO")),
        library=Path(os.path.expanduser(raw.get("library", "~/Music/ShokzSync"))),
    )
    for s in raw.get("sources", []):
        kind = s.get("kind") or infer_kind(s["url"])
        if kind not in KINDS:
            raise ValueError(f"source {s['name']!r}: unknown kind {kind!r} (use rss or youtube)")
        cfg.sources.append(Source(s["name"], s["url"], kind, bool(s.get("enabled", True))))
    if cfg.per_source < 1 or cfg.total < 1 or cfg.download_every_hours < 1:
        raise ValueError("per_source, total and download_every_hours must be at least 1")
    return cfg


def save(cfg: Config, path: Path | None = None) -> None:
    path = path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    home = str(Path.home())
    library = str(cfg.library)
    if library.startswith(home + os.sep):
        library = "~" + library[len(home) :]
    doc = {
        "per_source": cfg.per_source,
        "total": cfg.total,
        "download_every_hours": cfg.download_every_hours,
        "youtube_cookies_from": cfg.youtube_cookies_from,
        "device": cfg.device,
        "library": library,
        "sources": [
            {"name": s.name, "url": s.url, "kind": s.kind, "enabled": s.enabled}
            for s in cfg.sources
        ],
    }
    tmp = path.with_suffix(".toml.tmp")
    tmp.write_text(tomli_w.dumps(doc))
    os.replace(tmp, path)
