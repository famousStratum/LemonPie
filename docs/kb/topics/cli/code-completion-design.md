---
id: 20261117-code-completion-design
title: Code completion design
tags: [cli, design]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-cli-commands, 20261117-config-format, 20261117-model-verification]
summary: Design for --autocomplete mode — role enforcement, config additions, output filtering, retry policy, and model sizing tradeoffs.
---

# Code completion design

> Summary: Design for `--autocomplete` mode — role enforcement, config additions, output filtering, retry policy, and model sizing tradeoffs.

## Context

Design doc: `docs/design/code-completion.md`. Status: **Draft**.
Not yet implemented. Planned for a future release. See also: `docs/ROADMAP.md`.

## Goal

A `--autocomplete` flag that forces the model to return only code, with no explanations —
useful as a lightweight IDE-like autocomplete from the terminal.

```bash
lm -n "<prefix>" --autocomplete          # one-shot
lm --repl --autocomplete                 # interactive REPL
```

## Config changes

Two new fields in `config.json`:

```json
{
  "default_autocomplete_model": "smollm:360m",
  "roles": {
    "autocomplete": {
      "system": "You are a code autocomplete engine. Only output valid code tokens..."
    }
  }
}
```

New `lmConfig` command: `--set-default-autocomplete <model>`.

## Prompt and role enforcement

When `--autocomplete` is active, LemonPie injects the `autocomplete` system role.
Example system instruction:

> You are a code autocomplete engine. Only output valid code tokens that continue the
> given prefix. Do not include explanations, commentary, or markdown. If you cannot
> produce code, output an empty string.

## Output filtering

- **Primary**: system role constrains the model.
- **Secondary**: post-process output — syntactic sanity checks, strip leading natural
  language, retry with stricter prompt up to N times.
- **Fail-safe**: return empty completion + machine-readable error code (not a human
  explanation) after repeated failures.

## Model sizing tradeoffs

| Model class | Latency | Accuracy | Use case |
|---|---|---|---|
| Small (≤500M) | Low | Medium | Interactive REPL, quick suggestions |
| Medium (500M–3B) | Medium | Good | Most users, balanced |
| Large (>3B) | High | High | Offline batch, complex code |

Suggested default: `smollm:360m` for interactive; user-configurable for larger models.

## Flags

| Flag | Description |
|---|---|
| `--autocomplete` | Activate autocomplete mode (selects role, filters output) |
| `--model <name>` | Override default autocomplete model |
| `--stream` | Token streaming for low-latency incremental display |

## Rollout plan

Ship behind `--experimental-autocomplete` initially, promote once stable.

## Related

- [CLI commands](cli-commands.md) — see-also: flags will be added to the `lm` reference when implemented.
- [Config file format](../config/config-format.md) — supports: adds `default_autocomplete_model` and `roles` fields.
- [Model verification](../engine/model-verification.md) — reuses: `--add-model` state machine for verifying the autocomplete model.
