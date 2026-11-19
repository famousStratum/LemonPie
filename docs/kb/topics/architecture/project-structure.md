---
id: 20261117-project-structure
title: Project structure
tags: [architecture]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-ollama-client, 20261117-cli-commands, 20261117-session-storage]
summary: Source layout of the lemonpie package — what each module does and how they relate.
---

# Project structure

> Summary: Source layout of the lemonpie package — what each module does and how they relate.

## Context

LemonPie is packaged as `lemonpie-cli` on PyPI. The importable package lives under
`src/lemonpie/` and exposes three entry points: `lm`, `lemonpie` (both → `main:main`),
and `lmConfig` (→ `cli.config_cmd:main`).

## Module map

```
src/lemonpie/
  main.py           # CLI session manager — entry point for `lm` / `lemonpie`
  config.py         # Config load, save, and schema
  paths.py          # OS-appropriate config/data directory resolution (via platformdirs)
  time_utils.py     # Timestamp helpers
  cli/
    parser.py       # Argument parsing for `lm`
    ui.py           # Terminal helpers — confirmation prompts, output formatting
    config_cmd.py   # Config manager — entry point for `lmConfig`
  engine/
    models.py       # Model finding and alias resolution
    ollama.py       # Ollama HTTP client — streaming chat, model ops
  sessions/
    storage.py      # Session persistence — atomic read/write of history files
```

## Key relationships

- `main.py` orchestrates: it uses `cli/parser.py` for args, `config.py` for settings,
  `engine/models.py` to resolve the target model, `engine/ollama.py` to stream responses,
  and `sessions/storage.py` to persist history.
- `paths.py` is a pure utility — both `config.py` and `sessions/storage.py` import it
  to find the right OS directory without duplicating platform logic.
- `cli/config_cmd.py` is an independent entry point; it imports `config.py` and `paths.py`
  but does not depend on `main.py`.

## Build system

Built with **hatchling** + **hatch-vcs** (version derived from git tags).
Version is written to `src/lemonpie/_version.py` at build time.
See `pyproject.toml` for the full build configuration.

## Related

- [Ollama client](../engine/ollama-client.md) — supports: `main.py` calls into this for all LLM I/O.
- [CLI commands](../cli/cli-commands.md) — supports: `parser.py` and `config_cmd.py` define the user-facing API.
- [Session storage](../sessions/session-storage.md) — supports: `storage.py` handles all history persistence.
