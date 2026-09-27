---
type: Risk
title: launchd fires on mount and can write
description: Whether a LaunchAgent with StartOnMount runs on plug-in and gets removable-volume access.
state: settled
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T17:33:04Z }
---
# Question

Does a user LaunchAgent with `StartOnMount` fire when the headphones mount? Does its process get macOS removable-volume (TCC) access, and to which binary is the grant attached when the program is a uv-installed Python?

# Cheapest evidence

Spike: a LaunchAgent that on mount lists `/Volumes` and writes a file to the device, then logs the result.

# Evidence

Spike `.shipyard/macos-cli/launchd-mount-trigger/`, 2026-09-27:

- A user LaunchAgent with `StartOnMount` was loaded via `launchctl bootstrap gui/$UID`.
- Attaching a 20 MB MS-DOS (FAT) disk image `SPIKEFAT` fired the job within a second. It listed `/Volumes` and wrote `probe.txt` to the volume with no prompt.
- The agent fired once per mount, not at load.

# Answer

Yes. `StartOnMount` fires on any mount, so the job must check for `/Volumes/SWIM PRO` and exit quietly otherwise.

Residual: a disk image is not a USB removable volume, and macOS may still ask for removable-volume access the first time the real headphones mount. This is covered by the definition of done (first real plug-in), and `doctor` reports it. It is not a design risk: the fix is a one-time Allow.
