"""Install the two LaunchAgents: a scheduled download and a sync on mount."""

from __future__ import annotations

import os
import plistlib
import subprocess
from pathlib import Path

DOWNLOAD = "dev.shokz-sync.download"
MOUNT = "dev.shokz-sync.mount"
PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"


def agents_dir() -> Path:
    return Path(os.environ.get("SHOKZ_SYNC_AGENTS_DIR", Path.home() / "Library" / "LaunchAgents"))


def log_path() -> Path:
    return Path.home() / "Library" / "Logs" / "shokz-sync.log"


def render(program: str, every_hours: int = 24) -> dict[str, dict]:
    log = str(log_path())
    common = {
        "EnvironmentVariables": {"PATH": PATH},
        "StandardOutPath": log,
        "StandardErrorPath": log,
        "ProcessType": "Background",
    }
    return {
        DOWNLOAD: {
            "Label": DOWNLOAD,
            "ProgramArguments": [program, "download"],
            "StartInterval": every_hours * 60 * 60,
            "RunAtLoad": True,
            **common,
        },
        MOUNT: {
            "Label": MOUNT,
            "ProgramArguments": [program, "sync", "--auto"],
            "StartOnMount": True,
            **common,
        },
    }


def _domain() -> str:
    return f"gui/{os.getuid()}"


def install(program: str, every_hours: int = 24) -> list[Path]:
    d = agents_dir()
    d.mkdir(parents=True, exist_ok=True)
    log_path().parent.mkdir(parents=True, exist_ok=True)
    written = []
    for label, plist in render(program, every_hours).items():
        path = d / f"{label}.plist"
        subprocess.run(["launchctl", "bootout", f"{_domain()}/{label}"], capture_output=True)
        path.write_bytes(plistlib.dumps(plist))
        proc = subprocess.run(
            ["launchctl", "bootstrap", _domain(), str(path)], capture_output=True, text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(f"launchctl bootstrap {label}: {proc.stderr.strip()}")
        written.append(path)
    return written


def uninstall() -> list[Path]:
    removed = []
    for label in (DOWNLOAD, MOUNT):
        subprocess.run(["launchctl", "bootout", f"{_domain()}/{label}"], capture_output=True)
        path = agents_dir() / f"{label}.plist"
        if path.exists():
            path.unlink()
            removed.append(path)
    return removed


def loaded(label: str) -> bool:
    proc = subprocess.run(
        ["launchctl", "print", f"{_domain()}/{label}"], capture_output=True, text=True
    )
    return proc.returncode == 0
