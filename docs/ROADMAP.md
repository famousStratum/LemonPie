# 🗺 Roadmap

Planned features and improvements

## lmConfig --init
Interactive setup command that:
- Prompts for Ollama server IP:port
- Verifies server reachability
- Lists available models if server responds
- Allows user to select models to add
- Handles cases where no models are found (with guidance to Ollama docs)
- Supports `--force` to override verification or alias conflicts

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

## Enhanced error handling and user feedback
- Graceful handling of server errors (HTTP codes, non‑JSON responses)

## Future schema validation
- Config/session file validation
