# LemonPie — Knowledge Base Index

## How to use this KB (for agents)

0. This KB records what is **implemented today**. Code and tests are the source of truth; if a note disagrees with the code, fix the note in the same change.
1. Read this index first. Pick notes by their one-line descriptions; open only those.
2. To answer a question, prefer opening 1–3 specific notes over scanning everything.
3. Cite the note `id` when you use information from it.
4. Topic maps (`_topic.md` in each folder) are convenience views — the registry here is the source of truth.

## How to update this KB (for agents)

- New idea → create a new atomic note (`YYYYMMDD-slug`, kebab-case filename).
- Same idea, new information → edit the note in place and bump `updated`.
- Any create / rename / delete **must** update this registry and the topic's `_topic.md` in the same change.
- Use only tags from the controlled vocabulary below; add a new tag here before using it.
- Only document implemented behavior. Proposals and brainstorms belong in `docs/design/`, which is not part of the KB and is not a source of truth for existing code.
- When something is removed or replaced, delete its note outright and remove every reference to it (registry, `_topic.md`, `related:` ids, links). Do not leave tombstone or 'obsolete' notes.

## Controlled tags

`architecture`, `config`, `cli`, `sessions`, `backend`, `cicd`, `packaging`

---

## Registry

### architecture

- `20261117-project-structure` — **Project structure** — `topics/architecture/project-structure.md` — Source layout of the lemonpie package — what each module does and how they relate.

### config

- `20261117-config-format` — **Config file format** — `topics/config/config-format.md` — JSON schema for lemonpie's config file — backend, server URL, API key, default model, and model alias list.
- `20261117-config-paths` — **Config and data paths** — `topics/config/config-paths.md` — Where lemonpie stores its config file and session data on Linux, macOS, and Windows, and how to override them.

### cli

- `20261117-cli-commands` — **CLI commands** — `topics/cli/cli-commands.md` — Full flag reference for lm/lemonpie and lmConfig — every flag, its effect, and usage examples.

### sessions

- `20261117-session-storage` — **Session storage** — `topics/sessions/session-storage.md` — How chat sessions are persisted locally — file location, write strategy, and history format.

### backend

- `20261117-http-client` — **HTTP backend client** — `topics/backend/client.md` — Unified OpenAI-compatible HTTP client (client.py) supporting Ollama, llama.cpp, LM Studio, vLLM, and hosted APIs.

### cicd

- `20261117-ci-workflow` — **CI workflow** — `topics/cicd/ci-workflow.md` — GitHub Actions CI pipeline — triggers, what it runs, and the tools it uses (uv, pytest).
- `20261117-release-workflow` — **Release workflow** — `topics/cicd/release-workflow.md` — release-please manages the PR and tag, then PyPI publish uses OIDC trusted publishing.
