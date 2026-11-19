---
id: 20261117-release-workflow
title: Release workflow
tags: [cicd, packaging]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-ci-workflow]
summary: GitHub Actions release pipeline — release-please manages the PR and tag, then PyPI publish uses OIDC trusted publishing.
---

# Release workflow

> Summary: GitHub Actions release pipeline — release-please manages the PR and tag, then PyPI publish uses OIDC trusted publishing.

## Context

Defined in `.github/workflows/release.yml`. Runs on every push to `main`.
Two jobs: `release-please` and `pypi-publish` (the second runs only when a release is created).

## Job 1: release-please

- Uses `googleapis/release-please-action@v4`.
- Reads config from `.release-please/config.json` and `.release-please/manifest.json`.
- Creates or updates a release PR; merging that PR creates the GitHub release and tag.
- Requires a `RELEASE_PLEASE_TOKEN` secret.

## Job 2: pypi-publish

Runs only when `release_created == 'true'` (output from release-please).

Steps:
1. Checkout with full history (`fetch-depth: 0`) — required for hatch-vcs to read the tag.
2. **Tag reachability check** — verifies the commit is on `main` before publishing. Refuses if not.
3. Install uv (pinned same as CI).
4. Run `uv run pytest` — tests must pass before publish.
5. `uv build` — produce wheel and sdist.
6. `pypa/gh-action-pypi-publish@release/v1` — uploads via **Trusted Publisher** (OIDC, no API key needed).

## Permissions

```yaml
permissions:
  contents: write        # create releases
  pull-requests: write   # manage release PR
  id-token: write        # OIDC for PyPI trusted publishing
```

## Related

- [CI workflow](ci-workflow.md) — see-also: same test + build steps run in CI on every push.
