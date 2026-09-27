# Initiative

* [macOS CLI port of shokz-sync](initiative.md) - scope, settled choices, definition of done

# Design

* [shokz-sync-mac design](design.md) - components, data flow, failure behavior, tests

# Decisions

* [Python stack for the CLI](decision-python-stack.md) - Python, yt-dlp as a library, Typer/Rich, uv

# Risks

* [Device mounts when charging from the Mac](risk-device-mount.md) - whether and how it mounts
* [Device playback order](risk-playback-order.md) - copy order vs filename vs folders
* [launchd fires on mount and can write](risk-launchd-mount-trigger.md) - StartOnMount and removable-volume access
* [Browser cookies from a background job](risk-cookies-background.md) - Keychain prompt under launchd
* [yt-dlp dependencies on macOS](risk-ytdlp-deps.md) - ffmpeg and a JS runtime
* [macOS junk files on the device](risk-macos-junk-files.md) - ._ files and Spotlight folders
