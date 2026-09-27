# Shokz Sync for Mac

**Automatically load podcasts and YouTube audio onto Shokz OpenSwim and OpenSwim Pro headphones from a Mac.**

The OpenSwim headphones have no screen and no app store, only an MP3 player you fill over USB. `shokz-sync` downloads the newest episode of each show you follow. When you plug the headphones into your Mac to charge, it swaps in the new episodes and notifies you when it's safe to unplug. You never have to drag files in Finder.

- Podcast RSS feeds and YouTube channels or playlists
- Syncs itself when the headphones are plugged in; downloads once a day
- Keeps the newest episode of each show (up to 5 in total), newest first
- Finds new YouTube uploads through YouTube's own RSS feed, and picks the original-language audio rather than the auto-dubbed tracks
- If YouTube asks for a sign-in (its bot check), retries using your Chrome login; macOS asks once for Keychain access, so click Always Allow
- Cleans up the hidden `._` files and Spotlight indexing macOS adds to the headphones
- A command-line tool with nothing running in the background between jobs

A macOS rewrite of the Linux [garrickgan/shokz-sync](https://github.com/garrickgan/shokz-sync) (MIT). How this repo is built, and where its design notes live, is in [AGENTS.md](AGENTS.md).

## Install

Requires macOS, [Homebrew](https://brew.sh) and [uv](https://docs.astral.sh/uv/).

```bash
brew install ffmpeg deno      # deno lets yt-dlp read YouTube
git clone https://github.com/andrewxhill/shokz-sync-mac.git
cd shokz-sync-mac
uv tool install .             # installs the `shokz-sync` command
```

## Set up

```bash
shokz-sync sources add "Dwarkesh" https://apple.dwarkesh-podcast.workers.dev/feed.rss
shokz-sync sources add "Nate & Koa" https://www.youtube.com/channel/UC4hpU89Ex6O877-24QpWlOw
shokz-sync install            # download daily, sync on plug-in
```

Then plug in the headphones. The first time, macOS may ask whether shokz-sync can access removable volumes. Allow it.

To find a podcast's RSS feed, search for it on [Apple Podcasts](https://podcasts.apple.com). For YouTube, use the channel or playlist URL.

## Commands

| Command | What it does |
|---|---|
| `shokz-sync status` | What's on the headphones, what's queued, and each source's health |
| `shokz-sync sources list\|add\|rm\|enable\|disable` | Manage podcast feeds and YouTube channels |
| `shokz-sync run` | Download now, and sync if the headphones are connected |
| `shokz-sync skip "part of title"` | Never load that episode; the next-newest takes its place |
| `shokz-sync doctor` | Check tools, config, the headphones, and automation |
| `shokz-sync uninstall` | Remove the background jobs (keeps your settings and episodes) |

## Settings

`~/.config/shokz-sync/config.toml`:

| Setting | Default | Meaning |
|---|---|---|
| `per_source` | `1` | Newest episodes to keep from each source |
| `total` | `5` | Most episodes on the headphones |
| `download_every_hours` | `24` | Download schedule; rerun `shokz-sync install` after changing it |
| `device` | `"SWIM PRO"` | The headphones' volume name under `/Volumes` |
| `library` | `"~/Music/ShokzSync"` | Where episodes are kept on the Mac |
| `youtube_cookies_from` | `"chrome"` | Browser whose YouTube login is used only when YouTube's bot check blocks a download; `""` turns it off |

The Mac keeps exactly the same set of episodes as the headphones, so old ones never pile up.

## How it runs

There's no daemon. Two macOS LaunchAgents start the command only when needed:

- `dev.shokz-sync.download` runs `shokz-sync download` on the schedule.
- `dev.shokz-sync.mount` runs `shokz-sync sync --auto` whenever any drive mounts, and exits at once unless it's the headphones.

Output goes to `~/Library/Logs/shokz-sync.log`. State lives in `~/Library/Application Support/shokz-sync/`.

## Develop

```bash
uv run pytest
uv run ruff check src tests
```
