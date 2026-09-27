---
type: Decision
title: No Docker in this project
description: Everything, including tests, runs directly on the host Mac; the global run-everything-in-Docker rule does not apply here.
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-27T15:33:39Z }
---
# Choice

No Docker, no compose files, no containers. Tools, tests and the CLI run on the host Mac.

# Why

- The user said so, emphatically (2026-09-27).
- The tool needs the host anyway: `/Volumes`, launchd, macOS notifications and the Keychain are not reachable from a container.

# Alternatives

- Tests in Docker, the tool on the host: rejected by the user.
