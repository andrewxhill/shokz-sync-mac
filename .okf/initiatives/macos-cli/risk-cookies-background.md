---
type: Risk
title: Browser cookies from a background job
description: Whether yt-dlp can read browser cookies from a launchd job without a Keychain prompt.
state: settled
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T18:35:53Z }
---
# Question

Do any of the owner's sources need a login? If so, does `--cookies-from-browser` under launchd trigger a Keychain prompt, and does an exported cookies file avoid it and stay valid long enough?

# Cheapest evidence

Try the owner's real sources without cookies first; only if one fails, spike cookies-from-browser under launchd versus a cookies.txt file.

# Evidence

The owner's sources (2026-09-27) are all public: three podcast RSS feeds and one YouTube channel. Listing and resolving the YouTube channel worked with no cookies (see [risk-ytdlp-deps](risk-ytdlp-deps.md)).

# Answer

No source needs a login, so v1 sends no cookies and has no browser setting. The Keychain question does not arise. If YouTube later demands sign-in, reopen this Risk.

# Reopened 2026-09-27

After a day of heavy testing from this Mac (dozens of YouTube requests), every YouTube video request now fails: `Sign in to confirm you're not a bot`. Three retries in a row failed. The tool degrades as designed: Nate & Koa keeps its current episode and `status` shows the error. Only YouTube sources are affected.

Options:
- **Wait.** IP-based bot checks usually lift within hours. In normal use the tool makes about 2 YouTube requests a day. Evidence needed: does tomorrow's scheduled run succeed?
- **Opt-in browser cookies**: `youtube_cookies_from = "chrome"` passes yt-dlp `cookiesfrombrowser`. macOS asks once for Keychain access to "Chrome Safe Storage"; "Always Allow" should carry over to the launchd runs of the same binary (unverified).
- **Rejected by the owner:** wrapping Playwright or a headless browser.
- Not yet evaluated: a PO-token provider plugin (bgutil); the stale Nate & Koa RSS feed as a fallback.

# Resolution 2026-09-27

- **Finding episodes**: YouTube's channel RSS feed (`https://www.youtube.com/feeds/videos.xml?channel_id=UC4hpU89Ex6O877-24QpWlOw`) returned HTTP 200 with 15 entries, including 2026-09-12 `FZ_Ce-9eUOo`, *while* yt-dlp was bot-checked. It has exact publish times. Discovery now uses it, so the daily check no longer calls yt-dlp at all.
- **Downloading**: only a new episode calls yt-dlp, about once per upload. On a bot check it retries with Chrome cookies. The owner approved Chrome and rejected Playwright or headless browsers ("I don't want to care about this thing running most of the time").
- Residual: the first cookie retry shows a macOS Keychain prompt for "Chrome Safe Storage" via `/usr/bin/security`; "Always Allow" persists. This is not yet seen live, because no new upload has needed it. `status` shows the error if it fails.
