# LemonPie

![PyPI Version](https://img.shields.io/pypi/v/lemonpie-cli)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FfamousStratum%2FLemonPie%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

**LemonPie — A lightweight CLI for LLM inference servers**

LemonPie is a compact CLI for chatting with any OpenAI-compatible inference server — Ollama, llama.cpp, LM Studio, vLLM, and others. It manages chat sessions and persists history locally, designed to be tiny and portable — ideal for lightweight systems and terminal users, but usable anywhere with Python.



## 🚀 Quickstart
See [Installation](#-installation) for detailed installation instructions, [Configuration](#️-configuration) for configuration logic and structure, and [Usage](#️-usage) for usage examples

1. Install:     `uv tool install lemonpie-cli`

2. Configure:   `lmConfig --init`

3. Run:         `lm "Hello World!"`



## ✨ Features
- Works with any OpenAI-compatible backend — Ollama, llama.cpp, LM Studio, vLLM, and more
- Start and manage chat sessions with any configured model
- Persist session history in your OS's standard user data directory
- Configure host, backend, API key, default model, and aliases via a config file in your OS's standard user config directory
- Interactive setup wizard (`lmConfig --init`) — select backend, configure server, verify reachability, and register models
- Add, remove, and list models with aliases (`lmConfig`)
- Switch models mid‑session with confirmation
- Atomic writes for safety (tmp + replace)
- Streaming responses for real‑time output
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
│       ├── client.py        # HTTP client & error handling
│       ├── models.py        # Model finding & resolution
│       ├── cli/
│       │   ├── parser.py    # Argument parsing (lm)
│       │   ├── ui.py        # Terminal helpers & confirmation
│       │   └── config_cmd.py # Config manager (entrypoint: lmConfig)
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

## 📦 Installation

LemonPie requires **Python 3.11 or newer**. It installs three commands: `lm`, `lemonpie` (an alias), and `lmConfig`.

The recommended approach is to install it as an isolated command-line tool, so it doesn't interfere with your other Python projects.

### With [uv](https://docs.astral.sh/uv/) (recommended)

```bash
uv tool install lemonpie-cli
```

### With [pipx](https://pipx.pypa.io/)

```bash
pipx install lemonpie-cli
```

### With [pip](https://pip.pypa.io/en/stable/)

Use this inside a virtual environment:

```bash
python3 -m venv .venv          # Windows: py -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install lemonpie-cli
```
___
> **Note:**
> On many modern Linux distributions and Homebrew-managed Python installs, a global `pip install` is blocked (`externally-managed-environment`). Use uv, pipx, or a virtual environment instead.

## ⚙️ Configuration

LemonPie keeps its config file and session history in your OS's standard user directories (via [`platformdirs`](https://pypi.org/project/platformdirs/)) — not in the project folder:

| OS | Config Path                                | Sessions Path                                             |
|----------|--------------------------------------------|-----------------------------------------------------------|
| Linux    | `~/.config/lemonpie/`                      | `~/.local/share/lemonpie/sessions/`                       |
| macOS    | `~/Library/Application Support/lemonpie/`  | `~/Library/Application Support/lemonpie/sessions/`        |
| Windows  | `%LOCALAPPDATA%\lemonpie\`                 | `%LOCALAPPDATA%\lemonpie\sessions\`                       |


All three are overridable via environment variables — `LEMONPIE_HOST`, `LEMONPIE_CONFIG_DIR`, and `LEMONPIE_SESSION_DIR` — useful for testing or running in a container.

`docs/config.example.json` is a template. Run `lmConfig --init` to set up your config interactively — it verifies server reachability, lists installed models for selection, and writes the file for you. `lmConfig` also auto-creates a minimal config on first use if you prefer to configure manually.

### Example structure:
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
backend: a label for the inference server you're using (e.g. `ollama`, `llamacpp`, `lmstudio`) \
server: base URL of your inference server \
api_key: optional API key for hosted backends (e.g. OpenAI) \
default: canonical model name (full identifier) \
models: list of objects with alias (nullable) and name

## 🛠️ Usage
### `lm` / `lemonpie`

- Send a prompt\
`lm "Hello"`\
<sup>Sends a prompt to the current session</sup>

- Start a new session \
`lm -n "is there anybody in there?"`\
<sup>Starts a new session with the default model and sends the prompt</sup>\
`lm -n -m <alias> "just nod if you can hear me"`\
<sup>Starts a new session with a specific model `<alias>` and sends the prompt</sup>

- Manage sessions\
`lm -l`\
<sup>Lists all sessions, sorted by `<id>`</sup>\
`lm -p`\
<sup>Prints current session history</sup>\
`lm -s <id>`\
<sup>Loads an existing session by `<id>`</sup>

### `lmConfig`
- First-time setup\
`lmConfig --init`\
<sup>Walks you through choosing a backend, verifying your server, and registering models.</sup>

- Manage models\
`lmConfig --add-model <alias> <model>`\
<sup>Adds model mapping: alias → model_full_name</sup>\
`lmConfig --list-models`\
<sup>Lists configured model aliases and names</sup>


👉 For full command reference, please read [docs/usage/command-index.md](https://github.com/famousStratum/LemonPie/blob/main/docs/usage/command-index.md)

## 🗺 Roadmap

Planned features and improvements:

- Code completion (autocomplete)
- Model verification state machine
- Cross‑platform packaging (apt, winget, Homebrew)
- Future schema validation for config/session files

👉 See the full [roadmap](https://github.com/famousStratum/LemonPie/blob/main/docs/ROADMAP.md) for details.

## 📜 License

This project is licensed under the GNU General Public License v3.0 (**GPLv3**). You may redistribute and/or modify it under the terms of the GPL as published by the Free Software Foundation. See the [**license**](https://github.com/famousStratum/LemonPie/blob/main/LICENSE) file for details.
