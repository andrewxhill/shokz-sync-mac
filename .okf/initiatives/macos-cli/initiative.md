---
type: Initiative
title: macOS CLI port of shokz-sync
description: Port shokz-sync to macOS as a Python CLI with nicer commands, launchd automation and the upstream bugs fixed.
phase: production
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T18:22:38Z }
verified:
  - { by: human:andrew@textile.io, at: 2026-09-27T18:39:52Z }
  - { by: human:andrew@textile.io, at: 2026-09-27T17:33:40Z }
sources:
  - id: upstream
    resource: https://github.com/garrickgan/shokz-sync
    title: shokz-sync (Linux bash original, MIT), read at commit 1a16762
    author: human:garrickgan
---
# Scope

Port shokz-sync[^upstream] to macOS as a CLI. Keep its ideas (yt-dlp with a download archive, podcast RSS, keep the newest N on the device) and rewrite the code.

# Settled

The user delegated these answers to the agent on 2026-09-27.

- **Audience**: the owner only. Polish matters, packaging beyond one install command does not.
- **Language**: Python, installed with `uv tool install`. See [decision-python-stack](decision-python-stack.md).
- **Home**: fresh code in this repo, crediting upstream (MIT). No fork.
- **Automation**: `install` writes two launchd agents (scheduled download, sync on mount); `uninstall` removes them.
- **Commands**: `status`, `sources add|rm|list|enable|disable`, `download`, `sync`, `run`, `skip <track>`, `doctor`, `install`, `uninstall`. One TOML config. Coloured output and progress.
- **The rule: the newest item from each source, at most 5 in total.** Two global settings, `per_source = 1` and `total = 5`:
  - For each enabled source, take its newest item.
  - If that gives more than 5, keep the 5 with the most recent publish or like dates.
  - Load the device newest first. The local library mirrors exactly the same set.
  - Download only what that set needs; never backfill.
  - When a newer item arrives, the one it displaces leaves the device and the local library.
  - The set is recomputed from the feeds on every download. A skipped item never comes back, and skipping lets the source's next-newest item (even one shown before) take its place.
  - This replaces upstream's `MAX_DEVICE_TRACKS`, `MAX_DOWNLOADS_PER_SOURCE` and `MAX_NEW_PER_SYNC`.
- **Upstream bugs are fixed, not ported**:
  - Order tracks by an explicit key (like or playlist position, upload date, podcast publish date), not by file mtime.
  - Name files by stable ID so equal titles cannot collide or be silently dropped.
  - Plan the sync first; delete from the device only what the new tracks need room for, so the device is never left short.
  - Identify podcast episodes by `<guid>`, not enclosure URL.
  - Record each source's last run and last error; never swallow yt-dlp failures.
  - No browser cookies in v1: every source is public (see [risk-cookies-background](risk-cookies-background.md)).
- **Sources**: use the podcast's RSS feed when it is current, and YouTube otherwise. The owner's list, 2026-09-27 (they dropped the triathlon podcast):
  - Dwarkesh Podcast: RSS `https://apple.dwarkesh-podcast.workers.dev/feed.rss`
  - Skirious problems: RSS `https://anchor.fm/s/ed0abed0/podcast/rss`
  - Nate & Koa Podcast: YouTube `https://www.youtube.com/channel/UC4hpU89Ex6O877-24QpWlOw`. Its RSS feed is stale: the newest RSS item is from 2026-05-19, while YouTube has 2026-09-12.
- **No import** of an old `sources.conf` or `import-opml`: the owner does not run the Linux tool.
- **No Docker**: see [decision-no-docker](../../decision-no-docker.md).

# Definition of done

On the owner's real headphones: add a SoundCloud source and a podcast, plug the headphones into the Mac, and without typing anything the newest tracks land on the device in the intended order, macOS junk files (`._*` and friends) are cleaned up, and a notification appears. `shokz-sync status` shows the device, pending tracks and per-source health.

# Out of scope

Any GUI, menu-bar app or web UI; a database; Linux support; distribution to others.

# Risks

* [risk-device-mount](risk-device-mount.md) - does the device mount when charging from the Mac, and under what name
* [risk-playback-order](risk-playback-order.md) - what order the device plays files in
* [risk-launchd-mount-trigger](risk-launchd-mount-trigger.md) - can a launchd agent fire on mount and write to the volume
* [risk-cookies-background](risk-cookies-background.md) - browser cookies from a background job without a Keychain prompt
* [risk-ytdlp-deps](risk-ytdlp-deps.md) - what yt-dlp needs on macOS today (ffmpeg, a JS runtime)
* [risk-macos-junk-files](risk-macos-junk-files.md) - keeping `._*`, `.Spotlight-V100`, `.fseventsd`, `.Trashes` off the device

[^upstream]: shokz-sync (Linux bash original)
