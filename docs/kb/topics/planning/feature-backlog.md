---
id: 20261117-feature-backlog
title: Feature backlog
tags: [planning]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-cli-commands, 20261117-session-storage, 20261117-config-format, 20261117-code-completion-design, 20261117-model-verification, 20261117-packaging-design]
summary: Prioritized feature backlog and roadmap status — what's planned, what's deferred, and what's already done.
---

# Feature backlog

> Summary: Prioritized feature backlog and roadmap status — what's planned, what's deferred, and what's already done.

## Context

Living documents: `docs/design/feature-ideas.md` (prioritized backlog) and `docs/ROADMAP.md`
(summary view). Last updated: 2026-11-12. Check source docs for full discussion and history.

---

## ✅ Done

| Feature | Notes |
|---|---|
| Multi-backend support | Unified OpenAI-compatible client; `backend` + `api_key` in config |
| Enhanced error handling | Connection refused, timeout, DNS, protocol errors with actionable hints |
| `lmConfig --init` | Interactive setup wizard |

---

## 🔥 High priority — not yet implemented

### Session truncation / context management
Prevents session history from hitting model context limits.
- `--max-turns N` — truncate oldest turns
- `--context-size <tokens>` — trim to fit a context window
- `--compact` — summarize older turns before sending

### System prompt support
No way currently to give the model a role outside the conversation.
- `lm --system "..."` and `lm --system-file <path>`
- Stored per-session; default configurable in `config.json`

### Interactive REPL mode
`lm` is currently single-shot. REPL mode would stay in the loop.
- `lm --repl` — interactive loop with `/new`, `/close`, `/history`, `/model`, `/title`, `/exit` slash commands
- Keyboard shortcuts (up-arrow, tab completion) as a follow-on

---

## ⚡ Medium priority

| Feature | Summary |
|---|---|
| Temperature / sampling params | `--temperature`, `--top-p`, `--max-tokens`; defaults in config |
| Stdin / pipe input | `cat file.py \| lm "explain this"` — detect EOF vs tty |
| Schema validation | Validate `config.json` on load with pydantic or jsonschema |

---

## 🛠 Quick wins

| Feature | Status | Notes |
|---|---|---|
| `--config <path>` flag | Not implemented | Override config file location from CLI |
| `--dry-run` flag | **Implemented** | Prints HTTP payload, exits 0 |
| Config migration warnings | Not implemented | Warn + auto-migrate old config formats |
| `lmConfig --update-models` | Not implemented | Re-fetch model list without full `--init` |

---

## ⏳ Deferred

| Feature | Reason |
|---|---|
| Session export/import | Sessions are already JSON files; `scp`/`rsync` covers the need adequately |
| Model comparison mode | High resource cost (2× requests) for a niche feature |

---

## Planned (with dedicated design docs)

- **Code completion** — `docs/design/code-completion.md` → KB: [code-completion-design](../cli/code-completion-design.md)
- **Model verification** — `docs/design/model-verification.md` → KB: [model-verification](../engine/model-verification.md)
- **Cross-platform packaging** — `docs/design/packaging.md` → KB: [packaging-design](../cicd/packaging-design.md)

## Related

- [CLI commands](../cli/cli-commands.md) — see-also: existing flags; planned flags will land here.
- [Session storage](../sessions/session-storage.md) — see-also: session truncation and REPL affect storage.
- [Config file format](../config/config-format.md) — see-also: several backlog items add new config fields.
