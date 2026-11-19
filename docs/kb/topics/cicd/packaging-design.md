---
id: 20261117-packaging-design
title: Cross-platform packaging design
tags: [cicd, packaging, design]
created: 2026-11-17
updated: 2026-11-17
related: [20261117-ci-workflow, 20261117-release-workflow]
summary: Brainstorm for distributing LemonPie via apt, winget, and Homebrew — build flow, signing, and CI/CD integration.
---

# Cross-platform packaging design

> Summary: Brainstorm for distributing LemonPie via apt, winget, and Homebrew — build flow, signing, and CI/CD integration.

## Context

Design doc: `docs/design/packaging.md`. Status: **Brainstorm**.
Not yet implemented. The current release pipeline publishes to PyPI only (see
[release workflow](release-workflow.md)).

## Target channels

| OS | Channel | Format |
|---|---|---|
| Linux (Debian/Ubuntu) | APT repo / PPA | `.deb` |
| Windows | winget | manifest YAML |
| macOS | Homebrew | formula |

## Planned CI/CD flow

```
Tag release (GitHub)
        │
        ▼
   Build artifacts (.deb, .msi/.exe, .tar.gz)
        │
        ▼
   Sign binaries
        │
        ▼
   Publish to GitHub Releases
        │
        ▼
   Update package managers
   (apt repo, winget manifest, Homebrew formula)
```

## Signing requirements

- `.deb` — GPG signing
- Windows — code signing certificate
- macOS — notarization

## Open questions (from brainstorm)

- Unified version numbers across all package managers?
- Nightly builds vs stable releases only?
- Portable binaries (zip/tar) alongside package manager installs?
- Docker image as an alternative distribution channel?

## Next steps (from design doc)

- Draft initial `.deb` build script
- Experiment with winget manifest submission
- Write a prototype Homebrew formula
- Document signing requirements

## Related

- [CI workflow](ci-workflow.md) — see-also: same Actions infra would be extended.
- [Release workflow](release-workflow.md) — see-also: tag-triggered PyPI publish is the model for triggering package manager updates.
