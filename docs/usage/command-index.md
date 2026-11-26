# 📖 Command & Flag Index

Quick reference for LemonPie CLI commands and flags.
Useful for both **users** (cheat sheet) and **developers** (tracking CLI surface area).

---

## lmConfig

Manage LemonPie configuration (`config.json`).

- `--init` — Interactive setup wizard: select backend, configure server URL (local default or custom), verify reachability, list and select installed models, optionally set a default. If the server answers 401/403, prompts for an API key (hidden input) and retries; a key from `LEMONPIE_API_KEY` is tried first and never saved
- `--init --force` — Same as `--init` but skip server verification
- `--host <url>` — Set server host URL (`http(s)://host:port`)
- `--default-model <name>` — Set default model using alias or full name (must exist in models)
- `--add-model <alias> <model>` — Add model mapping: alias → model_full_name
- `--remove-model <identifier>` — Remove a model mapping by alias or full name
- `--list-models` — List configured model aliases and names
- `--api-key [<key>]` — Set or update the API key. Omit `<key>` to be prompted without echo (keeps it out of shell history and the process list)
- `--remove-api-key` — Remove the API key from the config
- `--show` — Print `config.json` (the API key is masked)
- `--force` — Force overwrite when adding a model; skip server verification when used with `--init`

---

## lm

Start and manage chat sessions.

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
- `--dry-run` — Print the HTTP payload without sending it (debugging tool)
- `prompt` — Prompt text (positional argument)

---

## Notes

- `--dry-run` prints the full JSON payload to `/v1/chat/completions` and exits with code 0.
- Flags can be combined with prompts:

  ```bash
  lm -m smollm:360m -n "Hello world"
  ```

- `--force` applies to `lmConfig --add-model` (overwrite alias conflicts) and `lmConfig --init` (skip server verification).
- `LEMONPIE_API_KEY` overrides the `api_key` value in `config.json` at runtime, and is used (but never saved) by `lmConfig --init`.
- Future flags will be added here as they are introduced.
