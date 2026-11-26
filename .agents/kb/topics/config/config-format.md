---
id: 20261117-config-format
title: Config file format
tags: [config]
created: 2026-11-17
updated: 2026-11-26
related: [20261117-config-paths, 20261117-cli-commands, 20261117-http-client]
summary: JSON schema for lemonpie's config file — backend, server URL, API key, default model, and model alias list.
---

# Config file format

> Summary: JSON schema for lemonpie's config file — backend, server URL, API key, default model, and model alias list.

## Context

LemonPie stores its settings in a single JSON file. The file is created by `lmConfig --init`
on first use. `docs/config.example.json` in the repo is a reference template.

## Schema

```json
{
  "backend": "ollama",
  "server": "http://localhost:11434",
  "api_key": null,
  "default": "qwen2.5-coder:3b",
  "models": [
    { "alias": "qwen", "name": "qwen2.5-coder:3b" },
    { "alias": null,   "name": "qwen2.5-coder:1.5b-base" }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `backend` | string | Backend identifier (`"ollama"`, or any OpenAI-compatible server name) |
| `server` | string | Server URL for the OpenAI-compatible `/v1/chat/completions` endpoint |
| `api_key` | string \| null | Optional API key — `null` for local servers, required for hosted APIs. `LEMONPIE_API_KEY` overrides it at runtime |
| `default` | string | Canonical model name used when no `-m` flag is given |
| `models` | array | Registered models; each has `alias` (nullable string) and `name` (full identifier) |

## Rules

- `default` must be the **full** model identifier (e.g. `qwen2.5-coder:3b`), not an alias.
- `alias` is optional — set to `null` to register a model without a shorthand.
- Aliases are resolved by `models.py` before any API call.
- Writes use atomic tmp-then-replace for safety. The temp file is created with mode `0600`, so the saved config is owner-only on POSIX (it may hold an API key).
- Environment overrides win at runtime and are never written to the file: `LEMONPIE_HOST` overrides `server`, `LEMONPIE_API_KEY` overrides `api_key`.
- `lmConfig --api-key` / `--remove-api-key` set or clear `api_key`; `lmConfig --show` masks it.
- `lmConfig --init` guides through backend selection, server setup, and model listing interactively. If the server answers 401/403 it prompts for an API key (hidden input) and saves the key only after it authenticates.

## Related

- [Config and data paths](config-paths.md) — prerequisite: where this file lives on each OS.
- [CLI commands](../cli/cli-commands.md) — see-also: `lmConfig` is the primary way to modify this file.
- [HTTP backend client](../backend/client.md) — see-also: `backend` and `server` are consumed here.
