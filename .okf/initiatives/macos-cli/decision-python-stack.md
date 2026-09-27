---
type: Decision
title: Python stack for the CLI
description: Rewrite in Python with yt-dlp as a library and off-the-shelf CLI and parsing libraries, installed via uv.
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T15:33:39Z }
sources:
  - id: upstream
    resource: https://github.com/garrickgan/shokz-sync
    title: shokz-sync (Linux bash original, MIT), read at commit 1a16762
    author: human:garrickgan
---
# Choice

Python, packaged for `uv tool install`. Buy, don't build:

- **yt-dlp** as a Python dependency, used as a library: it returns each item's id, upload date and playlist index, which fixes ordering and collisions without mtime hacks.
- **Typer** and **Rich** for commands, colour and progress.
- **feedparser** for podcast RSS, including `<guid>` and publish dates.
- **tomllib** (stdlib) to read config; **tomli-w** to write it.
- Notifications via `osascript`, launchd via `plistlib` (stdlib).

The custom code is the glue: config, the sync planner, and state. That glue is the product; nothing off the shelf does "keep the newest N on a USB player".

# Alternatives

- **Keep bash**: macOS ships bash 3.2, and nearly every upstream command is GNU-only, so it would be a rewrite anyway, in a worse language.
- **Go**: single binary, but yt-dlp would stay a subprocess and lose its structured metadata.

# Why

Structured metadata from yt-dlp is what makes the bug fixes clean. Upstream already used Python for RSS parsing[^upstream].

[^upstream]: shokz-sync (Linux bash original)
