---
id: 20261117-ci-workflow
title: CI workflow
tags: [cicd]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-release-workflow]
summary: GitHub Actions CI pipeline — triggers, what it runs, and the tools it uses (uv, pytest).
---

# CI workflow

> Summary: GitHub Actions CI pipeline — triggers, what it runs, and the tools it uses (uv, pytest).

## Context

Defined in `.github/workflows/ci.yml`. Runs on every push and pull request to `main`.

## Triggers

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

## What it does

1. Checks out the repo (full history via `fetch-depth: 0` — needed for hatch-vcs).
2. Installs **uv** (pinned to `0.12.17` via `astral-sh/setup-uv`).
3. Sets up Python via `uv python install`.
4. Runs `uv build` — verifies the package builds without errors.
5. Runs `uv run pytest` — runs the test suite under `tests/`.

## Pinned actions

All actions are pinned to a commit SHA for supply-chain safety:
- `actions/checkout` → `3d3c42e...`
- `astral-sh/setup-uv` → `c771a70...`

## Related

- [Release workflow](release-workflow.md) — see-also: release also runs pytest + build before publishing.
