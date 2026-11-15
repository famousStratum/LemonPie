# 🍋 Feature Ideas & Enhancement Brainstorm

**Status:** Draft / Brainstorm

This document collects feature ideas and enhancement recommendations for LemonPie.
It serves as a living reference for prioritization and implementation planning.
Items are categorized by effort/value and linked to design docs where applicable.

---

## 🔥 High Priority — Essential

### 1. Session Truncation / Context Management

**Problem:** Session history grows without bound. Eventually hits model context limits and inflates API cost. This is a technical bottleneck, not just a convenience issue.

**Proposal:**
- `--max-turns N` — auto-truncate oldest conversation turns (simple, no model call)
- `--context-size <tokens>` — trim messages to fit a specified context window
- `--compact` — summarize older turns before sending to reduce client-side memory and network payload size (inference cost is on the server, not the client)

**Status:** Not implemented.

---

### 2. System Prompt Support

**Problem:** No way to give the model a role or instructions outside the conversation. Cannot do "act as a code reviewer" or set context.

**Proposal:** Add system prompt via:
- `lm --system "You are a helpful Python tutor"`
- `lm --system-file ./system-prompt.txt`

Stored per-session so it persists with history. Default system prompt could be configured in `config.json`.

**Status:** Not implemented.

---

### 3. Interactive REPL Mode

**Problem:** `lm` is a single-shot tool — type prompt, get response, exit. No persistent chat.

**Proposal:** A `lm --repl` mode that stays in the loop:
- Accepts user input interactively
- Auto-appends to current session history
- Supports slash-commands:
  - `/new` — start a new session
  - `/close` — close current session
  - `/history` — print conversation history
  - `/model <name>` — switch model
  - `/title <text>` — rename session
  - `/exit` — quit
- Can be combined with existing flags: `lm --repl -m qwen`

**Sub-features:** REPL keyboard shortcuts and history (up-arrow for previous prompts, tab completion for model names/aliases, `Ctrl+R` for search). Depends on REPL being implemented first.

**Status:** Not implemented. Mentioned in [ROADMAP.md](../ROADMAP.md).

---

## ⚡ Medium Priority — Medium Value

### 4. Temperature / Sampling Parameters

**Proposal:** Add sampling control:
```
lm --temperature 0.7 --top-p 0.9 --max-tokens 2048
```
Store defaults in `config.json` or allow per-session overrides. Useful for code generation (low temp) vs. brainstorming (high temp).

**Status:** Not implemented.

---

### 5. Stdin / Pipe Input

**Problem:** No way to pipe text into a prompt. Forces users to type or use `-n "..."` with shell escaping.

**Proposal:**
- `lm -n -m qwen < some_file.py` — send a file's contents as the prompt
- `cat log.txt | lm "summarize this"` — natural Unix workflow
- Detect EOF / tty to differentiate pipe from interactive

**Status:** Not implemented.

---

### 6. Schema Validation for Config

**Problem:** Config is entirely duck-typed JSON. Typos like `"serer"` instead of `"server"` cause silent misbehavior.

**Proposal:** Validate `config.json` on load:
- Use `pydantic` or `jsonschema`
- Warn and auto-migrate on unknown fields
- Type-check required fields

**Status:** Partial — `ensure_models_list()` handles one migration case. No general validation.

---

## 🛠 Quick Wins — Low Effort, Noticeable Improvement

### 7. `--config <path>` Flag

Override the config file location from the CLI. Useful for testing, temporary overrides, or multi-environment setups.

**Status:** Not implemented.

### 8. `--dry-run` Flag

Print the HTTP payload (`/v1/chat/completions` body) without sending it. Debugging tool for verifying prompts, system prompts, and message history.

**Status:** Implemented.

### 9. Config Migration Warnings

Warn the user when loading an old config format (e.g. pre-0.2.0) and auto-migrate. Currently, missing keys silently default to `None`.

**Status:** Not implemented.

### 10. `lmConfig --update-models`

Re-fetch available models from the server without re-running the full `--init` wizard. A quick way to refresh the model list.

**Status:** Not implemented.

---

## ⏳ Deferred

### ~~Session Export / Import~~ — Deferred

~~**Proposal:**~~
~~- `lm --export <id> > session.json` — export a session to a file~~
~~- `lm --import session.json` — import a session from a file~~
~~- Useful for sharing, migrating, or backup~~

**Reason deferred:** Sessions are already JSON files stored on disk. For SBC/low-resource use cases, `scp` or `rsync` for backups, and git for migration, cover the common workflows. A dedicated export/import feature adds complexity for a convenience gap that file operations solve adequately today.

**Status:** Deferred — may revisit for schema versioning or batch operations in the future.

---

### ~~Model Comparison Mode~~ — Deferred

~~`lm --compare model1 model2 --prompt "explain quantum computing"` — sends the same prompt to two models, outputs responses side by side.~~

**Reason deferred:** Relatively high resource cost (2× API requests, 2× compute) for a niche feature. Lower priority than core functionality. May revisit if a lightweight streaming side-by-side mode makes sense later.

**Status:** Deferred.

---

## 📋 Already Planned (Linked Design Docs)

### Code Completion
- See [code-completion.md](code-completion.md)
- `--autocomplete` flag, system role enforcement, REPL integration

### Model Verification State Machine
- See [model-verification.md](model-verification.md)
- Server reachability check, model installation, pull workflow

### Cross-Platform Packaging
- See [packaging.md](packaging.md)
- `.deb`, `winget`, Homebrew distribution

---

## 📌 How to Use This Document

1. **Discuss and debate** — add comments, objections, alternatives
2. **Prioritize** — assign priority labels or move items between sections
3. **Combine** — ideas can merge (e.g., REPL + System Prompt + Parameters are related)
4. **Split** — large ideas can be broken into sub-tasks
5. **When ready**, promote an item to a dedicated design doc and move it to "Implemented"

---

*Last updated: 2026-11-12*

---

### Changes

- **2026-11-12:** Promoted session truncation and REPL mode to essential priority. Reordered essential section: (1) Truncation, (2) System prompt, (3) REPL. Moved compaction back in (client resource savings, not server cost concern). Moved session export/import and model comparison to "Deferred" section (crossed out). Removed "Niche/Fun" section (REPL shortcuts absorbed into REPL section).
