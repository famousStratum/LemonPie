---
id: 20261117-config-paths
title: Config and data paths
tags: [config]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-config-format, 20261117-session-storage]
summary: Where lemonpie stores its config file and session data on Linux, macOS, and Windows, and how to override them.
---

# Config and data paths

> Summary: Where lemonpie stores its config file and session data on Linux, macOS, and Windows, and how to override them.

## Context

LemonPie uses [`platformdirs`](https://pypi.org/project/platformdirs/) via `paths.py` to
resolve OS-appropriate directories. Nothing is stored in the project folder.

## Default paths

| OS | Config dir | Sessions dir |
|---|---|---|
| Linux | `~/.config/lemonpie/` | `~/.local/share/lemonpie/sessions/` |
| macOS | `~/Library/Application Support/lemonpie/` | `~/Library/Application Support/lemonpie/sessions/` |
| Windows | `%LOCALAPPDATA%\lemonpie\` | `%LOCALAPPDATA%\lemonpie\sessions\` |

## Environment variable overrides

Both directories can be overridden at runtime:

| Variable | Overrides |
|---|---|
| `LEMONPIE_CONFIG_DIR` | Config directory |
| `LEMONPIE_SESSIONS_DIR` | Sessions directory |

Useful for testing, CI runs, or containerized environments where the default OS path
isn't appropriate.

## Related

- [Config file format](config-format.md) — see-also: what the config file at this path contains.
- [Session storage](../sessions/session-storage.md) — see-also: how session files are written under the sessions dir.
