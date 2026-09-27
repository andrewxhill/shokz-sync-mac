# Update Log

## 2026-09-27
* **Gate**: The owner approved the revised [design](initiatives/macos-cli/design.md) by asking to ship it ("commit it all! push it all"). The initiative is back in production; the real-device plug-in check remains in the definition of done.
* **Update**: YouTube discovery now uses YouTube's own RSS feed; yt-dlp only downloads, with a Chrome-cookie fallback on the bot check. Settled [cookies](initiatives/macos-cli/risk-cookies-background.md).
* **Rename**: The product is now `shokz-sync-mac` (repo and package), and the command is `shokz-sync`. Config, state and the log moved to `shokz-sync` paths.
* **Reopened**: [cookies](initiatives/macos-cli/risk-cookies-background.md), after YouTube started a bot check.
* **Update**: The download schedule is now the config setting `download_every_hours`, default 24 (was a fixed 6 h), at the owner's request. The [design](initiatives/macos-cli/design.md) was updated to match.
* **Production**: Built `shokzsync` (src/, tests/, 29 passing). Installed it with the three sources and the launchd agents. Verified end to end: launchd download, and a FAT image named SWIM PRO that triggered the mount agent, which synced 3 episodes with 0 `._` files.
* **Gate reopened**: Production refined the [design](initiatives/macos-cli/design.md) (two locks, fetch outside the lock, file-rename reuse, empty-library guard) and the skip rule in the [initiative](initiatives/macos-cli/initiative.md). The Design is back to draft and the initiative back to scout, awaiting the owner's yes.
* **Gate**: The owner said "build it all, stop dragging your feet". The [design](initiatives/macos-cli/design.md) is frozen as stable and [macos-cli](initiatives/macos-cli/initiative.md) is in production.
* **Update**: Settled [launchd mount trigger](initiatives/macos-cli/risk-launchd-mount-trigger.md) with a FAT disk-image spike.
* **Update**: Settled [junk files](initiatives/macos-cli/risk-macos-junk-files.md). Manually loaded the three newest episodes onto the device.
* **Update**: The owner accepted [playback order](initiatives/macos-cli/risk-playback-order.md) without a listening test.
* **Update**: Settled [device mount](initiatives/macos-cli/risk-device-mount.md), [yt-dlp deps](initiatives/macos-cli/risk-ytdlp-deps.md) and [cookies](initiatives/macos-cli/risk-cookies-background.md); recorded the owner's sources; added partial evidence on [junk files](initiatives/macos-cli/risk-macos-junk-files.md).
* **Update**: [macos-cli](initiatives/macos-cli/initiative.md) now keeps the newest item per source, at most 5 in total, on the device and in the local library.
* **Creation**: Framed the [shokzsync](product.md) product and the [macos-cli](initiatives/macos-cli/initiative.md) initiative; moved it to scout with six open Risks.
* **Decision**: [No Docker](decision-no-docker.md) and [Python stack](initiatives/macos-cli/decision-python-stack.md).

## 2026-09-25
* **Initialization**: Created the empty bundle from the template.
