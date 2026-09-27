"""Keep the local library equal to the planned set."""

from __future__ import annotations

import hashlib
import re
import shutil
import unicodedata
from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass, field
from pathlib import Path

from . import plan
from .config import Config
from .sources import Adapter
from .state import DROPPED, SKIPPED, WANTED, State

_PUNCT = str.maketrans(
    {"\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'", "\u201c": "'", "\u201d": "'"}
)
_BAD = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def filename(item: plan.Item) -> str:
    """'<Source> - <Title> [abc123].mp3': ASCII, FAT-safe, collision-proof."""

    def fold(s: str) -> str:
        s = s.translate(_PUNCT)
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
        s = _BAD.sub(" ", s)
        return re.sub(r"\s+", " ", s).strip(" .")

    tag = hashlib.sha1(item.key.encode()).hexdigest()[:6]
    stem = f"{fold(item.source)} - {fold(item.title)}"[:120].rstrip(" .-")
    return f"{stem} [{tag}].mp3"


def duration(path: Path) -> float | None:
    try:
        from mutagen.mp3 import MP3

        return float(MP3(path).info.length)
    except Exception:
        return None


@dataclass
class Report:
    downloaded: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)  # source -> message


def refresh(
    cfg: Config,
    adapters: Mapping[str, Adapter],
    open_state: Callable[[], State] = State,
    commit_lock: Callable[[], AbstractContextManager] = nullcontext,
    on_fetch: Callable[[plan.Item], None] = lambda item: None,
) -> Report:
    """Fetch the planned set into the library, then commit state and prune under the lock.

    Network work happens outside `commit_lock`, so a plug-in sync is never blocked by a
    slow download. The commit re-reads state so a concurrent `skip` is not lost.
    """
    report = Report()
    lib = cfg.library
    lib.mkdir(parents=True, exist_ok=True)
    snap = open_state()
    skipped = snap.keys(SKIPPED)

    errors: dict[str, str] = {}
    candidates: dict[str, list[plan.Item]] = {}
    for src in cfg.enabled_sources:
        extra = sum(1 for k in skipped if k.startswith(src.name + ":"))
        try:
            n = cfg.per_source + extra
            candidates[src.name] = adapters[src.kind].newest(src.name, src.url, n)
        except Exception as e:  # one bad source must not stop the others
            errors[src.name] = str(e) or type(e).__name__
            candidates[src.name] = snap.wanted_items(src.name)

    ready: list[tuple[plan.Item, str]] = []
    for item in plan.choose(candidates, skipped, cfg.per_source, cfg.total):
        name = filename(item)
        prev = snap.items.get(item.key, {}).get("file")
        if not (lib / name).exists() and prev and (lib / prev).exists():
            (lib / prev).rename(lib / name)  # naming changed; don't download again
        if not (lib / name).exists():
            on_fetch(item)
            try:
                adapters[_kind(cfg, item.source)].fetch(item, lib / name)
            except Exception as e:
                errors[item.source] = f"download failed: {e}"
                # keep what this source already had rather than leaving a gap
                for old in snap.wanted(item.source)[: cfg.per_source]:
                    if old["file"] and (lib / old["file"]).exists():
                        ready.append((snap.as_item(f"{old['source']}:{old['id']}"), old["file"]))
                continue
            report.downloaded.append(name)
        ready.append((item, name))

    with commit_lock():
        st = open_state()
        for src in cfg.enabled_sources:
            if src.name in errors:
                st.source_error(src.name, errors[src.name])
            else:
                st.source_ok(src.name)
        report.errors = errors
        skipped_now = st.keys(SKIPPED)
        keep: set[str] = set()
        for item, name in ready:
            if item.key in skipped_now or item.key in keep:
                continue
            keep.add(item.key)
            st.put(item, WANTED, name, duration(lib / name))
        for key in st.keys(WANTED) - keep:
            st.set_status(key, DROPPED)
        _prune(lib, {st.items[k]["file"] for k in keep}, report)
        st.save()
    return report


def _kind(cfg: Config, source: str) -> str:
    src = cfg.find(source)
    if src is None:
        raise KeyError(source)
    return src.kind


def _prune(lib: Path, keep_files: set[str], report: Report) -> None:
    for p in lib.iterdir():
        if p.name in keep_files:
            continue
        if p.is_dir() and p.name.startswith(".yt-"):
            shutil.rmtree(p, ignore_errors=True)
        elif p.is_file() and (p.suffix == ".mp3" or p.name.endswith(".part")):
            p.unlink()
            if p.suffix == ".mp3":
                report.removed.append(p.name)


def skip(state: State, cfg: Config, query: str) -> list[dict]:
    """Mark the one wanted item whose title matches; return all matches."""
    q = query.lower()
    matches = [v for v in state.wanted() if q in v["title"].lower()]
    if len(matches) == 1:
        v = matches[0]
        state.set_status(f"{v['source']}:{v['id']}", SKIPPED)
        if v["file"]:
            (cfg.library / v["file"]).unlink(missing_ok=True)
        state.save()
    return matches
