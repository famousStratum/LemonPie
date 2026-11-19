---
id: 20261117-session-storage
title: Session storage
tags: [sessions]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-config-paths, 20261117-cli-commands]
summary: How chat sessions are persisted locally — file location, write strategy, and history format.
---

# Session storage

> Summary: How chat sessions are persisted locally — file location, write strategy, and history format.

## Context

LemonPie keeps chat history across invocations by writing session files to the OS sessions
directory (resolved by `paths.py`). All persistence logic lives in `sessions/storage.py`.

## Storage location

Session files are written under the sessions directory (see [Config and data paths](../config/config-paths.md)).
Overridable via `LEMONPIE_SESSIONS_DIR`.

## Write strategy

Writes are **atomic**: the new content is written to a temporary file, then `os.replace()`
swaps it in. This prevents corruption if the process is interrupted mid-write.

## Session history format

Session history is a list of `{role, content}` message objects — the same structure Ollama's
chat API expects. This makes it straightforward to replay a session.

## Operations

- **List sessions** — `lm -l` enumerates session files.
- **Print history** — `lm -p` loads and displays the current session.
- **New session** — `lm -n` creates a fresh session file.
- **Continue session** — a prompt without `-n` appends to the current session.

## Related

- [Config and data paths](../config/config-paths.md) — prerequisite: sessions dir location and override.
- [CLI commands](../cli/cli-commands.md) — see-also: `-l`, `-p`, `-n` flags interact with storage.
