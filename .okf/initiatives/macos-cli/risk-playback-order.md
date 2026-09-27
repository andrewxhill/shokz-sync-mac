---
type: Risk
title: Device playback order
description: What order the OpenSwim Pro plays files in (copy order, filename, or folders).
state: accepted
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T17:19:10Z }
verified: { by: human:andrewxhill, at: 2026-09-27T17:19:10Z }
---
# Question

Does the device play in FAT directory order (the order files were copied), by filename, or by folder? Does it remember the position in a long file?

# Cheapest evidence

Spike: copy three short, spoken-number MP3s in a known order whose names sort differently; listen. Pause mid-file, power-cycle, resume.

# Evidence

A spike copied four spoken test tracks (`.shipyard/macos-cli/playback-order/spike.py`), but the listening test was not run.

# Acceptance

On 2026-09-27 the owner said "you don't need to do this test". With one item per source and three sources, the device holds at most three files, so order barely matters. The tool still copies newest first, so copy order, mtime and the plan all agree.
