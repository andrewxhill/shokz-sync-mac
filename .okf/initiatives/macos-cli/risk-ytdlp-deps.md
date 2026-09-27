---
type: Risk
title: yt-dlp dependencies on macOS
description: What yt-dlp needs today on macOS (ffmpeg, a JavaScript runtime for YouTube).
state: settled
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T16:13:49Z }
---
# Question

Which external tools does current yt-dlp need for the owner's sources (ffmpeg for mp3 extraction, deno or another JS runtime for YouTube), and how should `doctor` check them?

# Cheapest evidence

Read the current yt-dlp README; run a download of one track per source type on this Mac.

# Evidence

Checked on 2026-09-27:

- Homebrew's `yt-dlp` here is 2025.06.12 and already fails on YouTube channel tabs ("Unsupported lockup view model"). Pinning and updating yt-dlp is part of the tool's job.
- `yt-dlp[default]` 2026.08.19 (it bundles `yt_dlp_ejs` 0.8.0) plus Homebrew `deno` 2.9.1 solves YouTube's JS challenges. Plain `yt-dlp` without the `[default]` extra reports "No supported JavaScript runtime", even with deno on PATH.
- No cookies or login were needed to list or resolve the Nate & Koa channel videos.
- **Auto-dubbed audio trap**: YouTube offers about 20 dubbed audio tracks per video. The selector `ba[format_note*=original]` picked `251-19` (en-US, original, 114k opus). Always select the original track.
- ffmpeg is on Homebrew (`/opt/homebrew/bin/ffmpeg`) and is needed to extract mp3.

# Answer

Depend on `yt-dlp[default]` as a Python package, with a `doctor` check for `deno` and `ffmpeg` on PATH. Use the format `ba[format_note*=original]/ba` and extract to mp3.
