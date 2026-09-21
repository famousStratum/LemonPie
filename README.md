# LemonPie

**The ultra‑lightweight Ollama session manager for terminal workflows**

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FfamousStratum%2FLemonPie%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![GitHub License](https://img.shields.io/github/license/famousstratum/lemonpie)

LemonPie is a compact CLI for interacting with an Ollama server. It manages chat sessions and persists history locally, designed to be tiny and portable — ideal for lightweight systems and terminal users, but usable anywhere with Python and network access.

---

## ✨ Features
- Start and manage chat sessions with Ollama models
- Persist session history in your OS's standard user data directory
- Configure host, default model, and aliases via a config file in your OS's standard user config directory
- Add, remove, and list models with aliases (`lmConfig`)
- Switch models mid‑session with confirmation
- Atomic writes for safety (tmp + replace)
- Streaming responses from Ollama for real‑time output
- Graceful handling of Ctrl‑C interrupts

---

## 📂 Project Structure

```text
LemonPie/
├── src/
│   └── lemonpie/            # Core package namespace
│       ├── main.py          # CLI session manager (entrypoints: lm, lemonpie)
│       ├── config.py        # Configuration logic & I/O
│       ├── paths.py         # OS-appropriate config/data directory resolution
│       ├── model_utils.py   # Model finding & resolution
│       ├── cli_utils.py     # Terminal helpers & confirmation
│       ├── session_utils.py # Session persistence
│       ├── spinner.py       # Status spinner
│       ├── time_utils.py    # Timestamp helpers
│       └── cli/
│           └── config_cmd.py # Config manager (entrypoint: lmConfig)
├── config.example.json      # Configuration template
├── pyproject.toml           # Package & build configuration
├── README.md                # Project overview
├── LICENSE                  # GPLv3 license
└── .gitignore
```

---

## ⚙️ Configuration

LemonPie keeps its config file and session history in your OS's standard user directories (via [`platformdirs`](https://pypi.org/project/platformdirs/)) — not in the project folder:

|            | Linux                          | macOS                                       | Windows                     |
|------------|---------------------------------|----------------------------------------------|------------------------------|
| Config     | `~/.config/lemonpie/`           | `~/Library/Application Support/lemonpie/`     | `%LOCALAPPDATA%\lemonpie\`   |
| Sessions   | `~/.local/share/lemonpie/sessions/` | `~/Library/Application Support/lemonpie/sessions/` | `%LOCALAPPDATA%\lemonpie\sessions\` |

Both are overridable via environment variables — `LEMONPIE_CONFIG_DIR` and `LEMONPIE_SESSIONS_DIR` — useful for testing or running in a container.

`config.example.json` at the repo root is a template. `lmConfig` will create your real config file on first use if one doesn't exist yet.

### Example structure:
```json
{
  "server": "http://127.0.0.1:11434",
  "default": "qwen2.5-coder:3b",
  "models": [
    { "alias": "qwen", "name": "qwen2.5-coder:3b" },
    { "alias": null,   "name": "qwen2.5-coder:1.5b-base" }
  ]
}
```
server: Ollama host URL\
default: canonical model name (full identifier)\
models: list of objects with alias (nullable) and name


---

## 🚀 Usage

### `lm` / `lemonpie`
- Start a new session \
`lm -n "Hello"`

- Start with a specific model\
`lm -n -m qwen "Hello"`

- Send a prompt to the current session\
`lm "Tell me about git add"`

- List sessions\
`lm -l`

- Print current session history\
`lm -p`

- Switch model in current session\
`lm -m qwen2.5-coder:3b`

### `lmConfig`
- Manage models with lmConfig\
`lmConfig --add-model qwen qwen2.5-coder:3b`\
`lmConfig --list-models`\
`lmConfig --remove-model qwen`


## 🗺 Roadmap

Planned features and improvements:

- `lmConfig --init`  
  Interactive setup command that:
  - Prompts for Ollama server IP:port
  - Verifies server reachability
  - Lists available models if server responds
  - Allows user to select models to add
  - Handles cases where no models are found (with guidance to Ollama docs)
  - Supports `--force` to override verification or alias conflicts

- Model verification state machine  
  Planned logic for `lmConfig --add-model`:
  - Check server reachability
  - Verify if model is installed
  - Offer to pull missing models
  - Handle pull success/failure and user choice
  - Respect `--force` for overriding conflicts or skipping checks  
  *(See docs/design/state-machine.md for full diagram once published)*

- Enhanced error handling and user feedback
  - Graceful handling of server errors (HTTP codes, non‑JSON responses)

- Packaging for Debian (`.deb` via apt)
- Future schema validation for config/session files


---

## 📜 License

This project is licensed under the **GNU General Public License v3.0** (**GPLv3**).You may redistribute and/or modify it under the terms of the GPL as published by the Free Software Foundation.See the [**license**](LICENSE) file for details.


---
