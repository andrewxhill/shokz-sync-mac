---
type: Risk
title: Device mounts when charging from the Mac
description: Whether the OpenSwim Pro appears under /Volumes when charged from the Mac, and under what name.
state: settled
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T16:13:49Z }
---
# Question

When the OpenSwim Pro is on its charging cable plugged into the Mac, does it mount as a drive? What is its volume name and filesystem, and how much space is free?

# Cheapest evidence

Plug it in; run `diskutil list`, `ls /Volumes` and `diskutil info` on the volume.

# Evidence

Observed on 2026-09-27 with the owner's headphones on the charging cable plugged into the Mac:

- It mounts at `/Volumes/SWIM PRO` from `/dev/disk4s1`: MS-DOS FAT32, USB, external, removable, 31.3 GB with 29 GiB free.
- Volume UUID `5661B9E6-98D6-35DD-8BF5-60CCC330A968`. Match the device on the volume name, with the UUID as a stronger check.
- The factory contents are `SYSTEM/allsong.lst` and `System Volume Information/WPSettings.dat`.
- `SYSTEM/allsong.lst` is the device's own index, JSON-like: `"musicNum":"000000000","dirNum":"000000000","List":[]`. The tool must never delete `SYSTEM/` or `System Volume Information/`.

# Answer

Yes. Charging at the Mac mounts the device, so plug-in is a usable sync trigger.
