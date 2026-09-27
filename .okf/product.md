---
type: Product
title: shokz-sync-mac
description: A macOS CLI that keeps a Shokz OpenSwim Pro loaded with fresh music and podcasts, synced when it is plugged in.
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T15:33:39Z }
sources:
  - id: upstream
    resource: https://github.com/garrickgan/shokz-sync
    title: shokz-sync (Linux bash original, MIT), read at commit 1a16762
    author: human:garrickgan
---
# Problem

The OpenSwim Pro is a screenless MP3 player. In the water you can only skip forward or back, so the experience is decided by what is on the device, and in what order, before you swim. Loading it by hand is tedious.

# Who it serves

One user: the repo owner, on their own Mac. It is not distributed to others.

# Shape

A macOS port of shokz-sync[^upstream], rewritten, with a nicer CLI. It downloads new tracks from configured sources on a schedule and syncs the newest ones to the headphones when they mount. There is no GUI.

# Initiatives

* [macos-cli](initiatives/macos-cli/initiative.md) - the whole product for now

[^upstream]: shokz-sync (Linux bash original)
