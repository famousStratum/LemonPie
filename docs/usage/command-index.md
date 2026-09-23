# 📖 Command & Flag Index

Quick reference for LemonPie CLI commands and flags.  
Useful for both **users** (cheat sheet) and **developers** (tracking CLI surface area).

---

## lmConfig
Manage LemonPie configuration (`config.json`).

- `--host <url>` — Set Ollama host URL (`http(s)://host:port`)
- `--default-model <name>` — Set default model using alias or full name (must exist in models)
- `--add-model <alias> <model>` — Add model mapping: alias → model_full_name
- `--remove-model <identifier>` — Remove a model mapping by alias or full name
- `--list-models` — List configured model aliases and names
- `--show` — Print full `config.json`
- `--force` — Force overwrite when adding a model

---

## lm
Run LemonPie with a given model or prompt.

- `-v, --version` — Show version
- `-m, --model <name>` — Model alias or full name
- `-n, --new` — Start a new chat session
- `-s, --session <id>` — Load an existing session by ID
- `-l, --list` — List chat sessions
- `-d, --delete <id>` — Delete a session by ID
- `-t, --title <text>` — Set or update session title
- `-c, --close` — Close current session
- `-p, --print` — Print current session history
- `--delete-all` — Delete all stored sessions
- `prompt` — Prompt text (positional argument)

---

## Notes
- Flags can be combined with prompts, e.g.:
`lm -m smollm:360m -n "Hello world"`
- `--force` applies only to `lmConfig --add-model`.
- Future flags (e.g., `--autocomplete`, `--init`) will be added here as they are introduced.