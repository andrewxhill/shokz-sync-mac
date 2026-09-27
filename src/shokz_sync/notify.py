"""macOS notifications via osascript."""

from __future__ import annotations

import subprocess


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def notify(message: str, title: str = "Shokz Sync") -> None:
    script = f"display notification {_quote(message)} with title {_quote(title)}"
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)
    except Exception:
        pass
