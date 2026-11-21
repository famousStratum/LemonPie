# LemonPie — Knowledge Base Index

## How to use this KB (for agents)

1. Read this index first. Pick notes by their one-line descriptions; open only those.
2. To answer a question, prefer opening 1–3 specific notes over scanning everything.
3. Cite the note `id` when you use information from it.
4. Topic maps (`_topic.md` in each folder) are convenience views — the registry here is the source of truth.

## How to update this KB (for agents)

- New idea → create a new atomic note (`YYYYMMDD-slug`, kebab-case filename).
- Same idea, new information → edit the note in place and bump `updated`.
- Any create / rename / delete **must** update this registry and the topic's `_topic.md` in the same change.
- Use only tags from the controlled vocabulary below; add a new tag here before using it.

## Controlled tags

`architecture`, `config`, `cli`, `sessions`, `backend`, `cicd`, `packaging`, `design`, `planning`

---

## Registry

### architecture

- `20261117-project-structure` — **Project structure** — `topics/architecture/project-structure.md` — Source layout of the lemonpie package — what each module does and how they relate.

### config

- `20261117-config-format` — **Config file format** — `topics/config/config-format.md` — JSON schema for lemonpie's config file — backend, server URL, API key, default model, and model alias list.
- `20261117-config-paths` — **Config and data paths** — `topics/config/config-paths.md` — Where lemonpie stores its config file and session data on Linux, macOS, and Windows, and how to override them.

### cli

- `20261117-cli-commands` — **CLI commands** — `topics/cli/cli-commands.md` — Full flag reference for lm/lemonpie and lmConfig — every flag, its effect, and usage examples.
- `20261117-model-verification` — **Model verification state machine** — `topics/cli/model-verification.md` — State machine for lmConfig --add-model — reachability, install check, pull offer, and --force override. Status: Ready.
- `20261117-code-completion-design` — **Code completion design** — `topics/cli/code-completion-design.md` — Design for --autocomplete mode — role enforcement, output filtering, retry policy, and model sizing tradeoffs. Status: Draft.

### sessions

- `20261117-session-storage` — **Session storage** — `topics/sessions/session-storage.md` — How chat sessions are persisted locally — file location, write strategy, and history format.

### backend

- `20261117-http-client` — **HTTP backend client** — `topics/backend/client.md` — Unified OpenAI-compatible HTTP client (client.py) supporting Ollama, llama.cpp, LM Studio, vLLM, and hosted APIs.

### cicd

- `20261117-ci-workflow` — **CI workflow** — `topics/cicd/ci-workflow.md` — GitHub Actions CI pipeline — triggers, what it runs, and the tools it uses (uv, pytest).
- `20261117-release-workflow` — **Release workflow** — `topics/cicd/release-workflow.md` — release-please manages the PR and tag, then PyPI publish uses OIDC trusted publishing.
- `20261117-packaging-design` — **Cross-platform packaging design** — `topics/cicd/packaging-design.md` — Brainstorm for apt, winget, and Homebrew distribution — build flow, signing, CI/CD integration. Status: Brainstorm.

### planning

- `20261117-feature-backlog` — **Feature backlog** — `topics/planning/feature-backlog.md` — Prioritized backlog and roadmap status — what's planned, deferred, and done, with links to design docs.
