---
id: 20261117-http-client
title: HTTP backend client
tags: [backend]
created: 2026-11-17
updated: 2026-11-26
related: [20261117-project-structure, 20261117-config-format]
summary: How lemonpie talks to AI backends — a unified OpenAI-compatible HTTP client (client.py) supporting Ollama, llama.cpp, LM Studio, vLLM, and hosted APIs.
---

# HTTP backend client

> Summary: How lemonpie talks to AI backends — a unified OpenAI-compatible HTTP client (`client.py`) supporting Ollama, llama.cpp, LM Studio, vLLM, and hosted APIs.

## Context

All backend communication is encapsulated in `src/lemonpie/client.py` using `httpx2` (no vendor SDK).

## Supported backends

Any server exposing the OpenAI-compatible `/v1/chat/completions` endpoint works:

- **Ollama** (local, default) — `http://127.0.0.1:11434`
- **llama.cpp** server
- **LM Studio**
- **vLLM**
- Hosted APIs (OpenAI, Anthropic-compatible, etc.) — requires `api_key` in config

The `backend` field in `config.json` is recorded by `lmConfig --init` for identification only;
 it does not change HTTP behavior.

## Configuration

| Config field | Used for |
|---|---|
| `server` | Base URL — the client appends `/v1/chat/completions` |
| `api_key` | Bearer token; `null` for unauthenticated local servers. `LEMONPIE_API_KEY` overrides it at runtime |
| `backend` | Backend name (identification only; set by `lmConfig --init`) |

## Authentication

`build_client(server_host, timeout, api_key)` sends `Authorization: Bearer <api_key>` on every request when a key is set. `main.py` resolves the key with `config.resolve_api_key`, so `LEMONPIE_API_KEY` wins over the config value. `lmConfig --init` probes `GET /v1/models` through the same client; a 401/403 response triggers its API key prompt.

## Streaming

LemonPie uses streaming responses for real-time terminal output. Each token is printed
as it arrives rather than waiting for the full completion.

## Model resolution

Before calling the backend, `models.py` resolves any alias to its canonical model name.
This is a pure lookup against the `models` list in config — no network call.

## Related

- [Project structure](../architecture/project-structure.md) — see-also: `main.py` orchestrates calls into this module.
- [Config file format](../config/config-format.md) — prerequisite: `server`, `api_key`, and `backend` come from config.
