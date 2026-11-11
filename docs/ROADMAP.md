# 🗺 Roadmap

Planned features and improvements

## Model verification state machine
Planned logic for `lmConfig --add-model`:
- Check server reachability
- Verify if model is installed
- Offer to pull missing models
- Handle pull success/failure and user choice
- Respect `--force` for overriding conflicts or skipping checks  

<sub>*See* docs/design/[model-verification.md](design/model-verification.md) *for full diagram once published*</sub>

## Cross‑platform packaging
- **Debian/Ubuntu**: `.deb` builds distributed via `apt` repository.
- **Windows**: package published to **winget** (Windows Package Manager).
- **macOS**: formula for **Homebrew** (brew install lemonpie).
- Ensure versioning consistency across all package managers.
- Automate builds with CI/CD pipelines (GitHub Actions, etc.).
- Provide signed binaries for security and trust.

## Code completion (autocomplete)
- **Native CLI code completion** that behaves like an IDE autocomplete but works from the LemonPie CLI:  
`lm -n "<prefix>" --autocomplete` or an interactive REPL mode.  
- The system must be able to **force the model to return only code** when autocomplete is selected and let users set a default autocomplete model via `lmConfig`.

<sub>*See* docs/design/[code-completion.md](design/code-completion.md) *for brainstorming and design notes.* </sub>

## ~~Enhanced error handling and user feedback~~ ✅ Done
- Connection refused, timeout, DNS, and protocol errors with actionable hints
- Tightened exception handling throughout

## Multi-backend support ✅ Done
- Unified OpenAI-compatible HTTP client (`/v1/chat/completions`) works with Ollama, llama.cpp, LM Studio, vLLM, and any compatible server
- `backend` field in config for identification and hints
- Optional `api_key` support for hosted APIs
- `lmConfig --init` guides users through backend selection and server setup

## Future schema validation
- Config/session file validation
