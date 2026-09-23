# LemonPie

![PyPI Version](https://img.shields.io/pypi/v/lemonpie-cli)
![GitHub License](https://img.shields.io/github/license/famousstratum/lemonpie)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FfamousStratum%2FLemonPie%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

**LemonPie — A lightweight Ollama client for terminal users**

LemonPie is a compact CLI for interacting with an Ollama server. It manages chat sessions and persists history locally, designed to be tiny and portable — ideal for lightweight systems and terminal users, but usable anywhere with Python and network access.



## ✨ Features
- Start and manage chat sessions with Ollama models
- Persist session history in your OS's standard user data directory
- Configure host, default model, and aliases via a config file in your OS's standard user config directory
- Add, remove, and list models with aliases (`lmConfig`)
- Switch models mid‑session with confirmation
- Atomic writes for safety (tmp + replace)
- Streaming responses from Ollama for real‑time output
- Graceful handling of Ctrl‑C interrupts



## 📂 Project Structure

```text
LemonPie/
├── src/
│   └── lemonpie/            # Core package namespace
│       ├── main.py          # CLI session manager (entrypoints: lm, lemonpie)
│       ├── config.py        # Configuration logic & I/O
│       ├── paths.py         # OS-appropriate config/data directory resolution
│       ├── time_utils.py    # Timestamp helpers
│       ├── cli/
│       │   ├── parser.py    # Argument parsing (lm)
│       │   ├── ui.py        # Terminal helpers & confirmation
│       │   └── config_cmd.py # Config manager (entrypoint: lmConfig)
│       ├── engine/
│       │   ├── models.py    # Model finding & resolution
│       │   └── ollama.py    # Ollama client interaction
│       └── sessions/
│           └── storage.py   # Session persistence
├── tests/                   # pytest suite
├── docs/
│   ├── config.example.json  # Configuration template
│   └── design/               # Design docs (model-verification.md, etc.)
├── .github/workflows/       # CI & release pipelines
├── pyproject.toml           # Package & build configuration
├── README.md                # Project overview
├── LICENSE                  # GPLv3 license
└── .gitignore
```

## ⚙️ Configuration

LemonPie keeps its config file and session history in your OS's standard user directories (via [`platformdirs`](https://pypi.org/project/platformdirs/)) — not in the project folder:

|            | Linux                          | macOS                                       | Windows                     |
|------------|---------------------------------|----------------------------------------------|------------------------------|
| Config     | `~/.config/lemonpie/`           | `~/Library/Application Support/lemonpie/`     | `%LOCALAPPDATA%\lemonpie\`   |
| Sessions   | `~/.local/share/lemonpie/sessions/` | `~/Library/Application Support/lemonpie/sessions/` | `%LOCALAPPDATA%\lemonpie\sessions\` |

Both are overridable via environment variables — `LEMONPIE_CONFIG_DIR` and `LEMONPIE_SESSIONS_DIR` — useful for testing or running in a container.

`docs/config.example.json` is a template. `lmConfig` will create your real config file on first use if one doesn't exist yet.

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

👉 Full [command reference](docs/usage/command-index.md).

## 🗺 Roadmap

Planned features and improvements:

- Code completion (autocomplete)
- lmConfig --init
- Model verification state machine
- Enhanced error handling and user feedback
- Cross‑platform packaging (apt, winget, Homebrew)
- Future schema validation for config/session files

👉 See the full [roadmap](docs/ROADMAP.md) for details.

## 📜 License

This project is licensed under the **GNU General Public License v3.0** (**GPLv3**).You may redistribute and/or modify it under the terms of the GPL as published by the Free Software Foundation.See the [**license**](LICENSE) file for details.
