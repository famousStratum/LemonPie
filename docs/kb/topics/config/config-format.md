---
id: 20261117-config-format
title: Config file format
tags: [config]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-config-paths, 20261117-cli-commands, 20261117-ollama-client]
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
| `api_key` | string \| null | Optional API key — `null` for local servers, required for hosted APIs |
| `default` | string | Canonical model name used when no `-m` flag is given |
| `models` | array | Registered models; each has `alias` (nullable string) and `name` (full identifier) |

## Rules

- `default` must be the **full** model identifier (e.g. `qwen2.5-coder:3b`), not an alias.
- `alias` is optional — set to `null` to register a model without a shorthand.
- Aliases are resolved by `engine/models.py` before any API call.
- Writes use atomic tmp-then-replace for safety.
- `lmConfig --init` guides through backend selection, server setup, and model listing interactively.

## Related

- [Config and data paths](config-paths.md) — prerequisite: where this file lives on each OS.
- [CLI commands](../cli/cli-commands.md) — see-also: `lmConfig` is the primary way to modify this file.
- [Ollama client](../engine/ollama-client.md) — see-also: `backend` and `server` are consumed here.
