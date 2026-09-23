# 📦 Cross‑Platform Packaging

**Status:** Brainstorm

This document outlines ideas and plans for distributing LemonPie across major operating systems.  
It is intended as a **whiteboard for brainstorming** CI/CD flows, signing, and repo hosting — not a finalized implementation plan.

---

## 🎯 Goals
- Provide native installation methods for Linux, Windows, and macOS.
- Ensure versioning consistency across package managers.
- Automate builds and publishing via CI/CD pipelines.
- Deliver signed binaries for security and trust.


## 🐧 Debian / Ubuntu (APT)
- Build `.deb` packages using `dpkg-buildpackage` or `debhelper`.
- Host packages in a PPA or custom apt repository.
- Automate publishing with GitHub Actions.
- Consider dependency handling (Python, Ollama client).


## 🪟 Windows (winget)
- Create manifest YAML for LemonPie.
- Submit package to the winget community repository.
- Support silent install for automation.
- Ensure installer includes path setup for `lm`.


## 🍎 macOS (Homebrew)
- Write a Homebrew formula pointing to GitHub releases.
- Support `brew install lemonpie`.
- Handle dependencies (Python, Ollama client).
- Automate formula updates via CI/CD.


## 🔄 CI/CD Flow
- Use GitHub Actions (or similar) to:
  - Build `.deb`, `.msi/.exe`, and `.tar.gz` artifacts.
  - Sign binaries for each OS.
  - Publish tagged releases to GitHub.
  - Trigger package manager updates (apt repo, winget manifest, Homebrew formula).
  

```text
Tag release (GitHub)
        │
        ▼
   Build artifacts
   (.deb, .msi/.exe, .tar.gz)
        │
        ▼
   Sign binaries?
    /        \
  NO          YES
  │            │
  │         Publish to GitHub
  │            │
  │            ▼
  │       Update package managers
  │       (apt repo, winget, Homebrew)
  │            │
  │            ▼
  │        Notify contributors
  │
  ▼
 Abort
 "signing required"
 ```


## 🔐 Signing and Security
- GPG signing for `.deb` packages.
- Code signing certificates for Windows executables.
- Notarization for macOS binaries.
- Document verification steps for contributors.


## 📝 Brainstorm Notes
- Should we unify version numbers across all package managers?  
- How to handle nightly builds vs stable releases?  
- Should LemonPie provide portable binaries (zip/tar) in addition to package manager installs?  
- Explore containerized distribution (Docker image) as an alternative.

## 📌 Next Steps
- Draft initial `.deb` build script.
- Experiment with winget manifest submission.
- Write a prototype Homebrew formula.
- Document signing requirements for each OS.
