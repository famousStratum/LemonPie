# LemonPie

**The ultra‑lightweight Ollama session manager for terminal workflows**

![GitHub License](https://img.shields.io/github/license/famousstratum/lemonpie)

LemonPie is a compact CLI for interacting with an Ollama server. It manages chat sessions and persists history locally, designed to be tiny and portable — ideal for lightweight systems and terminal users, but usable anywhere with Python and network access.

---

## ✨ Features
- Start and manage chat sessions with Ollama models
- Persist session history locally under `sessions/`
- Configure host, default model, and aliases via `config.json`
- Add, remove, and list models with aliases (`lmConfig`)
- Switch models mid‑session with confirmation
- Atomic writes for safety (tmp + replace)
- Streaming responses from Ollama for real‑time output
- Graceful handling of Ctrl‑C interrupts

---

## 📂 Project Structure

```text
lemonpie/
├── lm.py          # CLI session manager
├── lmConfig.py    # Config manager
├── config.json    # Example configuration
├── sessions/      # Session files (created at runtime)
├── README.md      # Project overview
├── LICENSE        # GPLv3 license
└── .gitignore     # Ignore venv, sessions, tmp files
```

---

## ⚙️ Configuration (`config.json`)
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

### lm.py
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

### lmConfig.py
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
  - Null vs empty string distinction for defaults
  - Clearer guidance messages when config is missing or invalid

- Packaging for Debian Trixie (`.deb` via apt)
- Future schema validation for config/session files


---

## 📜 License

This project is licensed under the **GNU General Public License v3.0** (**GPLv3**).You may redistribute and/or modify it under the terms of the GPL as published by the Free Software Foundation.See the [**license**]() file for details.


---

