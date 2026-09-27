"""Mirror the planned files onto the headphones' FAT volume."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

AUDIO = {".mp3", ".m4a", ".aac", ".wav", ".flac", ".wma"}
RESERVE = 50 * 1024 * 1024
NEVER_INDEX = ".metadata_never_index"


def find(name: str, volumes: Path = Path("/Volumes")) -> Path | None:
    p = volumes / name
    return p if p.is_dir() and os.path.ismount(p) else None


def dot_clean(volume: Path) -> None:
    """Strip the ._ AppleDouble files macOS writes for com.apple.provenance."""
    subprocess.run(["dot_clean", "-m", str(volume)], capture_output=True)


def tracks(volume: Path) -> list[Path]:
    return sorted(
        p
        for p in volume.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in AUDIO
    )


@dataclass
class Result:
    copied: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    no_space: list[str] = field(default_factory=list)


def sync(
    files: list[Path],
    volume: Path,
    reserve: int = RESERVE,
    clean: Callable[[Path], None] = dot_clean,
    on_copy: Callable[[Path], None] = lambda p: None,
) -> Result:
    """Copy `files` (newest first) to the volume root, then remove other audio there.

    Deletion happens after copying, so an interrupted or space-limited sync never leaves the
    device with fewer tracks than before. Only root-level audio files are ever deleted.
    """
    res = Result()
    for p in volume.glob("*.part"):
        p.unlink(missing_ok=True)
    wanted = {f.name for f in files}

    def copy_all(todo: list[Path]) -> list[Path]:
        left = []
        for f in todo:
            dest = volume / f.name
            size = f.stat().st_size
            if dest.exists() and dest.stat().st_size == size:
                continue
            if shutil.disk_usage(volume).free < size + reserve:
                left.append(f)
                continue
            on_copy(f)
            part = volume / (f.name + ".part")
            shutil.copyfile(f, part)
            os.replace(part, dest)
            res.copied.append(f.name)
        return left

    def delete_unwanted() -> None:
        for p in tracks(volume):
            if p.name not in wanted:
                p.unlink()
                res.deleted.append(p.name)

    left = copy_all(files)
    delete_unwanted()
    if left:  # room may have been freed by the deletes
        left = copy_all(left)
    res.no_space = [f.name for f in left]

    (volume / NEVER_INDEX).touch(exist_ok=True)
    os.sync()
    clean(volume)
    os.sync()
    return res
