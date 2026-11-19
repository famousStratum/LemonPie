---
id: 20261117-cli-commands
title: CLI commands
tags: [cli]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-config-format, 20261117-session-storage, 20261117-model-verification]
summary: Full flag reference for lm/lemonpie and lmConfig — every flag, its effect, and usage examples.
---

# CLI commands

> Summary: Full flag reference for `lm`/`lemonpie` and `lmConfig` — every flag, its effect, and usage examples.

## Context

Two entry points are exposed: `lm` / `lemonpie` for chat sessions, and `lmConfig` for
managing the config file. Both are defined in `pyproject.toml` under `[project.scripts]`.
Full source of truth: `docs/usage/command-index.md` in the repo.

---

## lmConfig

Manages `config.json`.

| Flag | Description |
|---|---|
| `--init` | Interactive setup wizard: select backend, configure server URL, verify reachability, list and select installed models, optionally set a default |
| `--init --force` | Same as `--init` but skip server verification |
| `--host <url>` | Set server host URL (`http(s)://host:port`) |
| `--default-model <name>` | Set default model using alias or full name (must exist in models list) |
| `--add-model <alias> <model>` | Add a model mapping: alias → full model name |
| `--remove-model <identifier>` | Remove a model mapping by alias or full name |
| `--list-models` | List all configured model aliases and names |
| `--show` | Print the full `config.json` |
| `--force` | Force overwrite on alias conflict; skip server verification when used with `--init` |

### Examples

```bash
lmConfig --init
lmConfig --add-model qwen qwen2.5-coder:3b
lmConfig --list-models
lmConfig --remove-model qwen
lmConfig --host http://192.168.1.10:11434
lmConfig --default-model qwen
lmConfig --show
```

---

## lm / lemonpie

```
lm [FLAGS] [PROMPT]
```

| Flag | Description |
|---|---|
| `-v, --version` | Show version |
| `-m, --model <name>` | Model alias or full name |
| `-n, --new` | Start a new chat session |
| `-s, --session <id>` | Load an existing session by ID |
| `-l, --list` | List all chat sessions |
| `-d, --delete <id>` | Delete a session by ID |
| `-t, --title <text>` | Set or update the current session title |
| `-c, --close` | Close the current session |
| `-p, --print` | Print current session history |
| `--delete-all` | Delete all stored sessions |
| `--dry-run` | Print the HTTP payload without sending it (debugging) |
| `prompt` | Prompt text (positional) |

### Notes

- `--dry-run` prints the full `/v1/chat/completions` JSON body and exits with code 0.
- `--force` on `lmConfig --add-model` overwrites alias conflicts; on `--init` skips server verification.
- Flags can be combined: `lm -m smollm:360m -n "Hello world"`
- Ctrl-C is handled gracefully in both entry points.
- Model switching mid-session prompts for confirmation via `cli/ui.py`.

---

## Related

- [Config file format](../config/config-format.md) — prerequisite: `lmConfig` reads and writes this file.
- [Session storage](../sessions/session-storage.md) — see-also: `-l`, `-p`, `-d`, `-c`, `-s` all interact with stored sessions.
- [Model verification](../engine/model-verification.md) — see-also: `--add-model` triggers the verification state machine.
