---
type: Risk
title: macOS junk files on the device
description: How to keep AppleDouble ._ files and Spotlight/fseventsd/Trashes folders off the FAT device.
state: settled
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T17:21:47Z }
---
# Question

Does copying from Python (`shutil.copyfile`) avoid `._*` files? Does `.metadata_never_index` stop Spotlight? Do `.fseventsd`/`.Trashes` confuse the player, and does `dot_clean` or deleting them after copy suffice?

# Cheapest evidence

Spike on the real device: copy with shutil.copyfile, list hidden files, add .metadata_never_index, replug, list again.

# Evidence

Spike `.shipyard/macos-cli/playback-order/spike.py`, 2026-09-27:

- On mount, before any write, macOS created `.fseventsd/` and `.Spotlight-V100/`, and `mdutil -s` reported "Indexing enabled."
- Copying with `shutil.copyfile` still produced a `._<name>` file for every file written, including `._.metadata_never_index`. The cause is the `com.apple.provenance` xattr that macOS attaches to every file a process writes. Skipping `cp` does not avoid it.
- `dot_clean -m "/Volumes/SWIM PRO"` removed all five `._*` files and the xattr.
- A `.metadata_never_index` file was written; its effect on Spotlight is checked on the next mount.

- On the next mount, `mdutil -s` reported "Indexing and searching disabled." `.metadata_never_index` works with no sudo. `.Spotlight-V100` stays as a small, static folder.
- A manual load of three real episodes (`shutil.copyfile` newest first, then `sync`, then `dot_clean -m`) left 0 `._*` files, and `cmp` matched all three byte for byte.

# Answer

After each sync: ensure `.metadata_never_index` exists, run `dot_clean -m` on the volume, then `sync`. Leave `.fseventsd`, `.Spotlight-V100`, `SYSTEM/` and `System Volume Information/` alone. Whether the dot-folders confuse the player is covered by the owner's first real listen; reopen this Risk if it plays or lists junk.
