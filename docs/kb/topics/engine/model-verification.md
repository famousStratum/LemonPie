---
id: 20261117-model-verification
title: Model verification state machine
tags: [engine, cli]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-cli-commands, 20261117-ollama-client, 20261117-config-format]
summary: State machine for lmConfig --add-model — server reachability, model installation check, pull offer, and --force override.
---

# Model verification state machine

> Summary: State machine for `lmConfig --add-model` — server reachability, model installation check, pull offer, and `--force` override.

## Context

Defined in `docs/design/model-verification.md`. Status: **Ready**.
Governs the logic inside `lmConfig --add-model` before writing a model entry to config.

## State machine

```
lmConfig --add-model <alias> <model>
             │
             ▼
       Can contact server?
        /              \
      NO                YES
      │                  │
      │             model installed?
      │              /          \
      │            YES           NO
      │             │             │
      │             ▼             ▼
      │            ADD         offer pull
      │                           │
      │                      ┌────┴────┐
      │                      │         │
      │                     YES        NO
      │                      │          │
      │                    pull       abort
      │                      │
      │                 success?
      │                 /      \
      │               YES       NO
      │                │         │
      │               ADD      abort
      │
      ▼
   abort
   "use --force to add without verification"
```

## --force behaviour

`--force` is a broad override:
- Skip server reachability check
- Skip model installation check
- Overwrite existing alias conflicts

## Related

- [CLI commands](../cli/cli-commands.md) — prerequisite: `--add-model` and `--force` flags.
- [HTTP backend client](ollama-client.md) — prerequisite: server reachability check calls into this.
- [Config file format](../config/config-format.md) — supports: a successful run appends to the `models` list.
